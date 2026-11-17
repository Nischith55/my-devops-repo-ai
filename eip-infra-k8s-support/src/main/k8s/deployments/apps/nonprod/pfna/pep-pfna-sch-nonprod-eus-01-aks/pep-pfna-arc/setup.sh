#!/usr/bin/env bash
#
# Manual install of GitHub ARC on pep-pfna-sch-nonprod-eus-01-aks.
#
# Installs, in dependency order:
#   1. arc-github-app secret   (runner namespace)
#   2. gha-runner-scale-set-controller  (arc-systems)
#   3. kube-mode Role/RoleBinding       (runner namespace)
#   4. gha-runner-scale-set             (runner namespace)
#   5. image prepull DaemonSet          (runner namespace)
#
# Usage:
#   export GITHUB_APP_ID=4558927
#   export GITHUB_APP_INSTALLATION_ID=152945158
#   export GITHUB_APP_PRIVATE_KEY_FILE=~/secure/arc-github-app.pem
#   ./install-arc.sh
#
set -euo pipefail

# ---------------------------------------------------------------- settings --
CLUSTER="pep-pfna-sch-nonprod-eus-01-aks"
CHART_VERSION="0.14.2"
CHART_REPO="oci://ghcr.io/actions/actions-runner-controller-charts"   # swap for an internal ACR mirror if ghcr.io is blocked

CONTROLLER_NS="arc-systems"
RUNNER_NS="pep-pfna-global-devsecops-dev"

CONTROLLER_RELEASE="arc-controller-${CLUSTER}"   # must stay in sync with
RUNNER_SET_RELEASE="arc-runner-set-${CLUSTER}"   # controller/helm-values.yaml

SECRET_NAME="arc-github-app"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTROLLER_VALUES="${SCRIPT_DIR}/controller/helm-values.yaml"
RUNNER_SET_VALUES="${SCRIPT_DIR}/runner-set/helm-values.yaml"
KUBE_MODE_RBAC="${SCRIPT_DIR}/runner-set/kube-mode-rbac.yaml"
PREPULL_MANIFEST="${SCRIPT_DIR}/prepull/image-prepull-daemonset.yaml"

# --------------------------------------------------------------- preflight --
: "${GITHUB_APP_ID:?set GITHUB_APP_ID}"
: "${GITHUB_APP_INSTALLATION_ID:?set GITHUB_APP_INSTALLATION_ID}"
: "${GITHUB_APP_PRIVATE_KEY_FILE:?set GITHUB_APP_PRIVATE_KEY_FILE (path to the .pem)}"
[[ -r "${GITHUB_APP_PRIVATE_KEY_FILE}" ]] || { echo "cannot read ${GITHUB_APP_PRIVATE_KEY_FILE}" >&2; exit 1; }

CURRENT_CTX="$(kubectl config current-context)"
echo ">> kubectl context: ${CURRENT_CTX}"
read -rp ">> install ARC into this cluster? [y/N] " ok
[[ "${ok}" == "y" || "${ok}" == "Y" ]] || { echo "aborted"; exit 1; }

# ------------------------------------------------------------- namespaces ---
for ns in "${CONTROLLER_NS}" "${RUNNER_NS}"; do
  kubectl create namespace "${ns}" --dry-run=client -o yaml | kubectl apply -f -
done

# ------------------------------------------------ 1. GitHub App secret ------
# NOTE: the chart resolves githubConfigSecret in the RUNNER SET's namespace,
# so this must live in ${RUNNER_NS} (not arc-runners).
echo ">> creating/updating secret ${SECRET_NAME} in ${RUNNER_NS}"
# kubectl create secret generic "${SECRET_NAME}" \
#   --namespace "${RUNNER_NS}" \
#   --from-literal=github_app_id="${GITHUB_APP_ID}" \
#   --from-literal=github_app_installation_id="${GITHUB_APP_INSTALLATION_ID}" \
#   --from-file=github_app_private_key="${GITHUB_APP_PRIVATE_KEY_FILE}" \
#   --dry-run=client -o yaml | kubectl apply -f -

kubectl apply -f ./secret/arc-github-app-secret.example.yaml

# --------------------------------------------------- 2. ARC controller ------
echo ">> installing controller ${CONTROLLER_RELEASE} (chart ${CHART_VERSION})"
helm upgrade --install "${CONTROLLER_RELEASE}" \
  "${CHART_REPO}/gha-runner-scale-set-controller" \
  --version "${CHART_VERSION}" \
  --namespace "${CONTROLLER_NS}" \
  --create-namespace \
  --values "${CONTROLLER_VALUES}" \
  --wait --timeout 10m

# the chart truncates the deployment name at 63 chars, so look it up by label
CONTROLLER_DEPLOY="$(kubectl -n "${CONTROLLER_NS}" get deploy \
  -l app.kubernetes.io/instance="${CONTROLLER_RELEASE}" -o name | head -1)"
kubectl -n "${CONTROLLER_NS}" rollout status "${CONTROLLER_DEPLOY}" --timeout=5m

# ------------------------------------------------- 3. kube-mode RBAC --------

echo ">> applying kube-mode RBAC"
kubectl apply -n "${RUNNER_NS}" -f "${KUBE_MODE_RBAC}"

# ---------------------------------------------------- 4. Runner scale set ---
echo ">> installing runner scale set ${RUNNER_SET_RELEASE} (chart ${CHART_VERSION})"
helm upgrade --install "${RUNNER_SET_RELEASE}" \
  "${CHART_REPO}/gha-runner-scale-set" \
  --version "${CHART_VERSION}" \
  --namespace "${RUNNER_NS}" \
  --create-namespace \
  --values "${RUNNER_SET_VALUES}" \
  --wait --timeout 10m

# ------------------------------------------------- 5. Image prepull DS ------
echo ">> applying prepull DaemonSet"
kubectl apply -n "${RUNNER_NS}" -f "${PREPULL_MANIFEST}"
kubectl -n "${RUNNER_NS}" rollout status daemonset/arc-runner-image-prepull --timeout=10m

# ------------------------------------------------------------- verify -------
echo
echo "===== installed ====="
helm list -n "${CONTROLLER_NS}"
helm list -n "${RUNNER_NS}"
kubectl -n "${RUNNER_NS}" get autoscalingrunnerset,autoscalinglistener 2>/dev/null || true
kubectl -n "${CONTROLLER_NS}" get pods
kubectl -n "${RUNNER_NS}" get pods -o wide
echo
echo "runner scale set should now appear in GitHub under the org's self-hosted runners"
echo "as: pfna-sch-nonprod-eus-01-arc"
