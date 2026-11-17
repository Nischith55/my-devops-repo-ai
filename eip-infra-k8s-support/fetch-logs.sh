#!/usr/bin/env bash

set -u -o pipefail

# Configurable thresholds via environment variables.
CPU_THRESHOLD_MILLICORES="${CPU_THRESHOLD_MILLICORES:-100}"
TAIL_LINES="${TAIL_LINES:-100}"

if ! command -v kubectl >/dev/null 2>&1; then
  echo "kubectl is required but was not found in PATH."
  exit 1
fi

low_usage_pods="$(kubectl top pods --all-namespaces --no-headers 2>/dev/null | awk -v threshold="$CPU_THRESHOLD_MILLICORES" '
function cpu_to_millicores(v) {
  if (v ~ /m$/) {
    sub(/m$/, "", v)
    return v + 0
  }
  return (v + 0) * 1000
}
{
  cpu_m = cpu_to_millicores($3)
  if (cpu_m < threshold) {
    print $1, $2, cpu_m
  }
}')"

if [[ -z "$low_usage_pods" ]]; then
  echo "No pods found below ${CPU_THRESHOLD_MILLICORES}m CPU usage."
  exit 0
fi

while read -r namespace pod_name cpu_m; do
  [[ -z "$namespace" || -z "$pod_name" ]] && continue
  echo "Fetching last ${TAIL_LINES} lines for pod ${pod_name} in namespace ${namespace} (cpu=${cpu_m}m)"
  if ! kubectl logs --tail="$TAIL_LINES" -n "$namespace" "$pod_name"; then
    echo "Warning: could not fetch logs for ${namespace}/${pod_name}"
  fi
done <<< "$low_usage_pods"
