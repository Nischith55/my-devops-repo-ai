# 🚀 Quick Reference & Implementation Guide

---

## 📋 Table of Contents

1. [Quick Start Commands](#quick-start-commands)
2. [Key File Locations](#key-file-locations)
3. [Deployment Checklist](#deployment-checklist)
4. [Troubleshooting Quick Tips](#troubleshooting-quick-tips)
5. [Common Commands](#common-commands)
6. [Environment Variables](#environment-variables)

---

## Quick Start Commands

### Clone & Setup Workspace

```bash
# Clone all repositories
git clone https://dev.azure.com/pepsicoit/EIAP_DevOps/_git/eip-helm-chart
git clone https://dev.azure.com/pepsicoit/EIAP_DevOps/_git/eip-infra-azure-terraform-support
git clone https://dev.azure.com/pepsicoit/EIAP_DevOps/_git/eip-infra-k8s-argocd-support
git clone https://dev.azure.com/pepsicoit/EIAP_DevOps/_git/eip-infra-k8s-support
git clone https://dev.azure.com/pepsicoit/EIAP_DevOps/_git/eip-infra-terraform-modules
git clone https://dev.azure.com/pepsicoit/EIAP_DevOps/_git/pep-eiap-potato-sourcing-matrix-pipeline-templates
git clone https://dev.azure.com/pepsicoit/EIAP_DevOps/_git/potato-sourcing-argocd-configs
git clone https://dev.azure.com/pepsicoit/EIAP_DevOps/_git/potato-sourcing-matrix-api-repo
```

### Install Prerequisites

```bash
# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# Install Terraform
wget https://releases.hashicorp.com/terraform/1.5.0/terraform_1.5.0_linux_amd64.zip
unzip terraform_1.5.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Install Argo Rollouts CLI
curl -sLO https://github.com/argoproj/argo-rollouts/releases/download/v1.6.0/kubectl-argo-rollouts-linux-amd64
chmod +x kubectl-argo-rollouts-linux-amd64
sudo mv kubectl-argo-rollouts-linux-amd64 /usr/local/bin/kubectl-argo-rollouts
```

### Deploy Infrastructure (Terraform)

```bash
# 1. Authenticate to Azure
az login
az account set --subscription <subscription-id>

# 2. Navigate to infrastructure repo
cd eip-infra-azure-terraform-support

# 3. Initialize Terraform (first time only)
terraform init \
  -backend-config="resource_group=<rg>" \
  -backend-config="storage_account_name=<sa>" \
  -backend-config="container_name=<container>" \
  -backend-config="key=terraform.tfstate"

# 4. Plan infrastructure changes
terraform plan \
  -var="environment=nonprod" \
  -var="region=eus" \
  -var="functional_area=eiap" \
  -out=tfplan

# 5. Apply infrastructure
terraform apply tfplan

# 6. Get AKS credentials
az aks get-credentials \
  --resource-group pep-eiap-nonprod-eus-infra-01-rg \
  --name pep-eiap-nonprod-eus-global-01-aks
```

### Deploy Application (Helm)

```bash
# 1. Add Helm repository (if using remote)
helm repo add eip https://helm-repo.eiap.pepsico.io
helm repo update

# 2. Create namespace
kubectl create namespace pep-eiap-apps-dev

# 3. Label namespace for Istio injection
kubectl label namespace pep-eiap-apps-dev istio-injection=enabled

# 4. Deploy with Helm
helm install potato-sourcing \
  -f eip-helm-chart/umbrellachart/values-dev.yaml \
  -n pep-eiap-apps-dev \
  eip-helm-chart/umbrellachart

# 5. Verify deployment
kubectl get deployment -n pep-eiap-apps-dev
kubectl get pods -n pep-eiap-apps-dev
kubectl logs -f deployment/potato-sourcing -n pep-eiap-apps-dev
```

### Setup ArgoCD (GitOps)

```bash
# 1. Create argocd namespace
kubectl create namespace argocd

# 2. Install ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# 3. Expose ArgoCD UI (port-forward)
kubectl port-forward svc/argocd-server -n argocd 8080:443

# 4. Get initial admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# 5. Login to ArgoCD UI
# Open https://localhost:8080
# Username: admin
# Password: <from above>

# 6. Create ArgoCD Application (via CLI or UI)
# Either:
# a) Create via CLI:
argocd app create potato-sourcing-dev \
  --repo https://dev.azure.com/pepsicoit/EIAP_DevOps/_git/potato-sourcing-argocd-configs \
  --path dev/pep-eiap-nonprod-eus-global-01-aks/potato-sourcing-matrix-api \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace pep-eiap-apps-dev

# b) Or create ConfigMap manually in cluster
```

### Setup Istio Service Mesh

```bash
# 1. Install Istio
curl -L https://istio.io/downloadIstio | sh -
cd istio-1.18.0
export PATH=$PWD/bin:$PATH
istioctl install --set profile=production -y

# 2. Label namespace for sidecar injection
kubectl label namespace pep-eiap-apps-dev istio-injection=enabled --overwrite

# 3. Create Gateway
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: main-gateway
  namespace: pep-eiap
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: SIMPLE
      credentialName: main-gateway-cert
    hosts:
    - "*.eiap.pepsico.io"
EOF

# 4. Verify Istio sidecar injection
kubectl get pods -n pep-eiap-apps-dev -o jsonpath='{.items[].spec.containers[*].name}' | tr ',' '\n' | sort | uniq
# Should show: istio-proxy among containers
```

### Setup Monitoring

```bash
# 1. Install Prometheus
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace

# 2. Install Grafana
helm repo add grafana https://grafana.github.io/helm-charts
helm install grafana grafana/grafana -n monitoring

# 3. Get Grafana password
kubectl get secret -n monitoring grafana -o jsonpath="{.data.admin-password}" | base64 --decode

# 4. Port-forward Grafana
kubectl port-forward svc/grafana 3000:80 -n monitoring

# 5. Access Grafana
# Open http://localhost:3000
# Username: admin
# Password: <from above>

# 6. Add Prometheus data source
# URL: http://prometheus-operated:9090
```

### Setup KEDA

```bash
# 1. Install KEDA
helm repo add kedacore https://kedacore.github.io/charts
helm install keda kedacore/keda --namespace keda --create-namespace

# 2. Verify KEDA
kubectl get deploy -n keda
kubectl get crd | grep keda

# 3. Deploy example KEDA ScaledObject (see Helm chart templates)
```

---

## Key File Locations

### Helm Charts

```
eip-helm-chart/
├── umbrellachart/
│   ├── Chart.yaml                      # Main entry point (v2.2.4)
│   ├── values.yaml                     # Base values
│   ├── values-apm.yaml                 # APM/AppDynamics config
│   ├── values-cronjob.yaml             # CronJob deployment
│   ├── values-fivestar-ivr-*.yaml      # Application-specific
│   └── templates/
│
├── app-chart/
│   ├── Chart.yaml                      # Workload chart (v1.3.2)
│   ├── values.yaml
│   └── templates/
│       ├── deployment.yaml
│       ├── rollout.yaml
│       ├── service.yaml
│       ├── cronjob.yaml
│       ├── configmap.yaml
│       ├── serviceaccount.yaml
│       └── _helpers.tpl
│
└── platform-chart/
    ├── Chart.yaml                      # Platform chart (v1.3.3)
    ├── values.yaml
    └── templates/
        ├── hpa.yaml
        ├── pdb.yaml
        ├── virtualservice.yaml
        ├── destinationrule.yaml
        ├── envoyfilter.yaml
        ├── kedascaledobject.yaml
        ├── pv.yaml / pvc.yaml
        ├── storageclass.yaml
        └── secretProviderClass.yaml
```

### Infrastructure

```
eip-infra-azure-terraform-support/
├── azure-pipelines.yml                 # Main pipeline
├── src/
│   ├── eiap/
│   │   ├── nonprod/
│   │   │   ├── common-tf-config/      # Shared config
│   │   │   └── resources/             # Per-resource TF files
│   │   ├── preprod/
│   │   └── prod/
│   └── [other-functional-areas]/
│
└── templates/                          # Terraform module templates

eip-infra-terraform-modules/
└── modules/
    ├── aks/
    ├── storage-account/
    ├── key-vault/
    ├── acr/
    ├── networking/
    └── ...
```

### CI/CD Pipelines

```
pep-eiap-potato-sourcing-matrix-pipeline-templates/
├── build.yaml                          # Build stage (tests, scanning)
├── deploy-aks.yaml                     # Deploy stage (Helm, ArgoCD)
├── deploy-aks-env.yaml                 # Environment-specific deploy
├── Spring-CICD.yaml                    # Main pipeline orchestration
├── pipelineapproval.yaml               # Manual approval
├── variables.yaml                      # Pipeline variables
└── job_template_kaniko.yaml            # Kaniko build template
```

### ArgoCD Configs

```
potato-sourcing-argocd-configs/
├── dev/
│   └── pep-eiap-nonprod-eus-global-01-aks/
│       └── potato-sourcing-matrix-api/
│           └── helm-values.yaml        # Dev deployment values
├── qa/
│   └── [cluster]/
│       └── [app]/
│           └── helm-values.yaml        # QA deployment values
└── prod/
    └── [cluster]/
        └── [app]/
            └── helm-values.yaml        # Prod deployment values
```

### Application

```
potato-sourcing-matrix-api-repo/
├── azure-pipeline.yaml                 # Application pipeline
├── Dockerfile                          # Container image build
├── requirements.txt                    # Python dependencies
├── pep-potato-sourcing-matrix-automation/
│   └── src/
│       ├── main.py
│       ├── routes/
│       ├── models/
│       └── ...
└── README.md
```

---

## Deployment Checklist

### Pre-Deployment (Engineering Team)

- [ ] **Code Review**
  - [ ] PR reviewed by 2+ engineers
  - [ ] Tests pass
  - [ ] No conflicts

- [ ] **Testing**
  - [ ] Unit tests pass (pytest)
  - [ ] Coverage > 80%
  - [ ] Integration tests pass

- [ ] **Security Scanning**
  - [ ] SonarQube quality gate: PASS
  - [ ] Fortify SAST: No critical/high
  - [ ] Snyk: No exploitable vulnerabilities

- [ ] **Documentation**
  - [ ] README updated
  - [ ] API docs updated (if needed)
  - [ ] Change summary documented

### Pre-Deployment (Operations Team)

- [ ] **Infrastructure Ready**
  - [ ] AKS cluster operational
  - [ ] Storage provisioned (if needed)
  - [ ] Key Vault secrets configured
  - [ ] Network policies applied

- [ ] **Cluster Configuration**
  - [ ] Namespace exists
  - [ ] Sidecar injection enabled (Istio)
  - [ ] RBAC configured
  - [ ] Resource quotas set

- [ ] **Monitoring Ready**
  - [ ] Prometheus scraping configured
  - [ ] Grafana dashboards created
  - [ ] AppDynamics application created
  - [ ] Alert rules configured

- [ ] **ArgoCD Ready**
  - [ ] ArgoCD instance running
  - [ ] Git repo access configured
  - [ ] Application CRD prepared
  - [ ] Sync policy set

### Deployment (Automation via CI/CD)

**Dev Environment:**
- [ ] Trigger: Push to dev branch
- [ ] CI/CD: Automatic
- [ ] Strategy: Standard rolling update
- [ ] Approval: None (automatic)

**QA Environment:**
- [ ] Trigger: Push to qa branch (or merge from dev)
- [ ] CI/CD: Automatic
- [ ] Strategy: Standard rolling update
- [ ] Approval: None (automatic)

**Production Environment:**
- [ ] Trigger: Push to main branch
- [ ] CI/CD: Build + pre-approval
- [ ] Strategy: Canary (Argo Rollouts)
- [ ] Approval: Manual (Change Manager required)

### Post-Deployment Verification

- [ ] **Application Health**
  - [ ] Pods running (kubectl get pods)
  - [ ] No CrashLoopBackOff
  - [ ] Readiness probes passing
  - [ ] Liveness probes passing

- [ ] **Connectivity**
  - [ ] Service DNS resolving
  - [ ] Network policies allowing traffic
  - [ ] Ingress accessible
  - [ ] TLS/SSL working

- [ ] **Monitoring**
  - [ ] Metrics flowing to Prometheus
  - [ ] Logs in Azure Monitor
  - [ ] APM traces visible
  - [ ] Dashboards showing data

- [ ] **Functional Tests**
  - [ ] Health check endpoint: 200 OK
  - [ ] API endpoints responding
  - [ ] Database connectivity
  - [ ] Business logic working

- [ ] **Performance**
  - [ ] Response time normal
  - [ ] CPU usage within limits
  - [ ] Memory usage within limits
  - [ ] No error spikes

### Post-Deployment Cleanup

- [ ] Old version confirmed terminated
- [ ] Artifacts archived
- [ ] Pipeline logs retained
- [ ] Documentation updated
- [ ] Team notified

---

## Troubleshooting Quick Tips

### Issue: Pod won't start (ImagePullBackOff)

```bash
# Check pod events
kubectl describe pod <pod-name> -n <namespace>

# Check image pull secrets
kubectl get secrets -n <namespace> | grep docker

# Verify image exists in ACR
az acr repository show-tags -n <acr-name> --repository <repo>

# Solution options:
# 1. Recreate imagePullSecret
kubectl create secret docker-registry regcred \
  --docker-server=<acr-name>.azurecr.io \
  --docker-username=<username> \
  --docker-password=<password>

# 2. Check ACR IP allowlisting (if using private ACR)
```

### Issue: ArgoCD application won't sync

```bash
# Check ArgoCD app status
argocd app get <app-name>

# Check Git credentials
kubectl get secrets -n argocd | grep repo

# Verify manifest repo access
# Try cloning manually:
git clone <manifest-repo-url>

# Check YAML syntax
kubectl apply -f <manifest-file> --dry-run=client

# Force ArgoCD hard refresh
argocd app set <app-name> --refresh --operation-retry-backoff-duration 2s
```

### Issue: Canary rollout stuck

```bash
# Check rollout status
kubectl describe rollout <rollout-name> -n <namespace>

# Check analysis run
kubectl get analysisrun -n <namespace>
kubectl describe analysisrun <analysis-run-name> -n <namespace>

# Check if Prometheus is responding
kubectl port-forward -n monitoring prometheus-operated-0 9090:9090
# Visit http://localhost:9090/graph

# Verify Prometheus query
# Go to Prometheus UI and test query from AnalysisTemplate

# Manually abort rollout if stuck
kubectl argo rollouts abort <rollout-name> -n <namespace>

# Retry rollout
kubectl argo rollouts retry <rollout-name> -n <namespace>
```

### Issue: Service mesh not working (traffic not routing)

```bash
# Check Istio sidecar injection
kubectl get pods -n <namespace> -o jsonpath='{.items[].spec.containers[*].name}'

# Check namespace injection label
kubectl get namespace <namespace> -o jsonpath='{.metadata.labels}'
# Should have: istio-injection=enabled

# Check VirtualService
kubectl get virtualservice -n <namespace>
kubectl describe vs <vs-name> -n <namespace>

# Check DestinationRule
kubectl get destinationrule -n <namespace>
kubectl describe dr <dr-name> -n <namespace>

# Check Gateway
kubectl get gateway -n <namespace>
kubectl describe gateway <gateway-name> -n <namespace>

# Test connectivity using Envoy debug endpoint
kubectl exec -it <pod-name> -c istio-proxy -n <namespace> -- curl http://localhost:15000/stats
```

### Issue: Secrets not accessible from pods

```bash
# Check SecretProviderClass
kubectl get secretproviderclass -n <namespace>
kubectl describe spc <spc-name> -n <namespace>

# Check if CSI driver is running
kubectl get ds -n kube-system | grep secrets

# Verify Key Vault access
kubectl exec -it <pod-name> -n <namespace> -- ls -la /mnt/secrets-store

# Check pod identity / managed identity
# Verify in Azure: Identity → Role Assignments
# Should have: Key Vault Secrets User role

# Troubleshoot:
kubectl logs -f <pod-name> -n <namespace> -c app
# Look for key vault access errors
```

### Issue: High memory/CPU usage

```bash
# Check current usage
kubectl top nodes
kubectl top pods -n <namespace>

# Check resource limits
kubectl get pods -n <namespace> -o yaml | grep -A 5 limits

# Check HPA status
kubectl get hpa -n <namespace>
kubectl describe hpa <hpa-name> -n <namespace>

# Check for memory leaks
kubectl logs -f <pod-name> -n <namespace>
# Look for growing memory patterns

# Solutions:
# 1. Increase resource requests/limits in values.yaml
# 2. Scale up replicas manually
# 3. Tune GC settings (for Java apps)
# 4. Add KEDA ScaledObject for event-driven scaling
```

---

## Common Commands

### Kubernetes Cluster Operations

```bash
# Get cluster info
kubectl cluster-info
kubectl get nodes
kubectl describe node <node-name>

# Get resource usage
kubectl top nodes
kubectl top pods -n <namespace>

# Scale deployment
kubectl scale deployment <deployment-name> --replicas=5 -n <namespace>

# Restart pods
kubectl rollout restart deployment/<deployment-name> -n <namespace>

# Check pod logs
kubectl logs -f <pod-name> -n <namespace>
kubectl logs --previous <pod-name> -n <namespace>  # If crashed

# Execute command in pod
kubectl exec -it <pod-name> -n <namespace> -- /bin/sh

# Port forward
kubectl port-forward svc/<service-name> 8000:8000 -n <namespace>

# Delete pods (for restart)
kubectl delete pod <pod-name> -n <namespace>

# Describe resources
kubectl describe pod <pod-name> -n <namespace>
kubectl describe deployment <deployment-name> -n <namespace>

# Get YAML
kubectl get deployment <deployment-name> -n <namespace> -o yaml
```

### Helm Operations

```bash
# Add repository
helm repo add <name> <url>
helm repo update

# List releases
helm list -n <namespace>

# Install release
helm install <release-name> <chart> -f values.yaml -n <namespace>

# Upgrade release
helm upgrade <release-name> <chart> -f values.yaml -n <namespace>

# Rollback release
helm rollback <release-name> <revision> -n <namespace>

# Get values
helm get values <release-name> -n <namespace>

# Get manifest
helm get manifest <release-name> -n <namespace>

# Test template rendering (dry-run)
helm template <release-name> <chart> -f values.yaml

# Delete release
helm delete <release-name> -n <namespace>

# Lint chart
helm lint <chart-path>
```

### Argo Rollouts Operations

```bash
# List rollouts
kubectl get rollout -n <namespace>
kubectl argo rollouts list -n <namespace>

# Get rollout status
kubectl argo rollouts status <rollout-name> -n <namespace>

# Describe rollout
kubectl describe rollout <rollout-name> -n <namespace>

# Promote rollout (if using manual promotion)
kubectl argo rollouts promote <rollout-name> -n <namespace>

# Abort rollout
kubectl argo rollouts abort <rollout-name> -n <namespace>

# Retry rollout
kubectl argo rollouts retry <rollout-name> -n <namespace>

# Watch rollout progress
kubectl argo rollouts get <rollout-name> -n <namespace> --watch

# Get analysis runs
kubectl get analysisrun -n <namespace>
kubectl describe analysisrun <analysis-run-name> -n <namespace>
```

### ArgoCD Operations

```bash
# List applications
argocd app list

# Get app status
argocd app get <app-name>

# Sync application
argocd app sync <app-name>
argocd app sync <app-name> --prune  # Delete objects not in Git

# Set auto-sync
argocd app set <app-name> --sync-policy auto

# Refresh application
argocd app refresh <app-name>

# Validate manifest
argocd app diff <app-name>

# Logs
argocd app logs <app-name>

# Hard refresh (slow)
argocd app set <app-name> --refresh
```

### Istio Operations

```bash
# Check Istio version
istioctl version

# Verify installation
istioctl verify-install

# Check sidecar injection
istioctl kube-inject -f <pod-spec> > <injected-spec>

# Analyze configuration
istioctl analyze

# Check routing
kubectl describe vs <virtualservice-name> -n <namespace>
kubectl describe dr <destinationrule-name> -n <namespace>

# Debug proxy
kubectl exec -it <pod-name> -c istio-proxy -n <namespace> -- \
  curl http://localhost:15000/config_dump

# Check metrics
kubectl exec -it <pod-name> -c istio-proxy -n <namespace> -- \
  curl http://localhost:15000/stats
```

### Azure CLI Operations

```bash
# Login
az login
az account show

# Set subscription
az account set --subscription <subscription-id>

# Get AKS credentials
az aks get-credentials --resource-group <rg> --name <cluster-name>

# Check ACR images
az acr repository list -n <acr-name>
az acr repository show-tags -n <acr-name> --repository <repo>

# Get Key Vault secrets
az keyvault secret list --vault-name <vault-name>
az keyvault secret show --vault-name <vault-name> --name <secret-name>

# Get resource details
az resource show --ids <resource-id>
```

### Terraform Operations

```bash
# Initialize
terraform init

# Format
terraform fmt -recursive .

# Validate
terraform validate

# Plan
terraform plan -out=tfplan

# Apply
terraform apply tfplan

# Destroy
terraform destroy

# Get state
terraform state list
terraform state show <resource>

# Force unlock (if needed)
terraform force-unlock <lock-id>
```

---

## Environment Variables

### Azure DevOps Pipeline Variables

```yaml
# Pipeline Variables (set in Azure Pipelines)
npglobalacrurl: pepeiapnonprodcommonacr.azurecr.io
acrrepoprefix: pep/eiap
acrreponame: potato-sourcing-matrix-api

aks-nonprod-eus: pep-eiap-nonprod-eus-global-01-aks
aks-preprod-eus: pep-eiap-preprod-eus-global-01-aks
aks-prod-eus: pep-eiap-prod-eus-global-01-aks

aksnamespace-dev: pep-eiap-apps-dev
aksnamespace-qa: pep-eiap-apps-qa
aksnamespace-prod: pep-eiap-apps-prod

manifest_repo_url: pepsicoit.visualstudio.com/EIAP_DevOps/_git/potato-sourcing-argocd-configs
manifest_branch: dev
manifest_pr_branch: manifest-$(Build.BuildNumber)

SONARPROJECTKEY: potato-sourcing-matrix-api
CI_Token: $(fortify-ci-token)
SNYK_AUTH_TOKEN: $(snyk-auth-token)

Appname: potato-sourcing-matrix-api
```

### Application Environment Variables (Helm ConfigMap)

```yaml
# values-prod.yaml
global:
  deployment:
    env:
      - name: APP_ENV
        value: production
      - name: LOG_LEVEL
        value: INFO
      - name: DATABASE_HOST
        valueFrom:
          secretKeyRef:
            name: db-credentials
            key: host
      - name: DATABASE_PORT
        value: "1433"
      - name: DATABASE_NAME
        value: cgfpsmadevsqlDB
      - name: API_KEY
        valueFrom:
          secretKeyRef:
            name: api-keys
            key: api-key
      - name: MSSQL_DRIVER
        value: "{ODBC Driver 18 for SQL Server}"
```

### Service Principal Variables

```bash
# For Azure authentication in pipelines
export AZURE_SUBSCRIPTION_ID="<subscription-id>"
export AZURE_TENANT_ID="<tenant-id>"
export AZURE_CLIENT_ID="<service-principal-app-id>"
export AZURE_CLIENT_SECRET="<service-principal-secret>"

# Authenticate
az login --service-principal \
  -u $AZURE_CLIENT_ID \
  -p $AZURE_CLIENT_SECRET \
  --tenant $AZURE_TENANT_ID
```

---

## Quick Troubleshooting Matrix

| Symptom | Likely Cause | Quick Fix |
|---------|--------------|-----------|
| Pod ImagePullBackOff | Bad credentials or image doesn't exist | Verify ACR access, check image tag |
| Pod CrashLoopBackOff | App error or missing secrets | Check logs: `kubectl logs <pod>` |
| Slow scaling | HPA target metrics not available | Verify Prometheus scraping, check HPA: `kubectl describe hpa` |
| ArgoCD out of sync | Git credentials expired or YAML syntax error | Refresh repo, run `argocd app refresh` |
| Istio routing not working | Sidecar not injected or VS/DR misconfigured | Check namespace label, verify VS exists |
| Canary stuck | Analysis template failing | Check Prometheus, verify query in `kubectl describe analysisrun` |
| High latency | Resource contention or network issues | Check `kubectl top pods`, review latency metrics |
| Deployment timeout | Image too large or K8s API slow | Check pod events: `kubectl describe pod` |

---

**Quick Reference Guide Generated:** October 29, 2026  
**Organization:** PepsiCo EIP  
**Version:** 1.0
