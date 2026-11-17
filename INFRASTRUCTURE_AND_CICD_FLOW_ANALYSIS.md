# 🏗️ End-to-End Infrastructure & CI/CD Flow Analysis

**Organization:** PepsiCo EIP (Enterprise Integration Platform)  
**Created:** October 29, 2026  
**Document Version:** 1.0

---

## 📑 Executive Summary

This document provides a **comprehensive analysis** of the EIP multi-repository ecosystem, covering:
- **Infrastructure Architecture** (Azure Terraform + Kubernetes)
- **Application Deployment** (Helm Charts + ArgoCD)
- **CI/CD Pipelines** (Azure DevOps)
- **Service Mesh & Add-ons** (Istio, KEDA, AppDynamics)
- **Deployment Strategies** (Canary, Blue-Green, Standard)
- **End-to-End Application Lifecycle**

---

# 🗂️ Part 1: Repository Ecosystem Overview

## Repositories Structure

```
my project/
├── eip-helm-chart/                           # 🚢 Central Helm Chart Repository
├── eip-infra-azure-terraform-support/        # ☁️ Azure Infrastructure as Code
├── eip-infra-k8s-argocd-support/             # 🔄 ArgoCD GitOps Configurations
├── eip-infra-k8s-support/                    # 🛠️ Kubernetes Post-Provisioning
├── eip-infra-terraform-modules/              # 📦 Reusable Terraform Modules
├── pep-eiap-potato-sourcing-matrix-pipeline-templates/  # 📋 CI/CD Pipeline Templates
├── potato-sourcing-argocd-configs/           # 🎯 Application-Specific ArgoCD Configs
└── potato-sourcing-matrix-api-repo/          # 🚀 Sample Application (Python)
```

### Repository Responsibilities

| Repository | Purpose | Key Components |
|---|---|---|
| **eip-helm-chart** | Application deployment templates | 🚢 Umbrella Chart, App Chart, Platform Chart |
| **eip-infra-azure-terraform-support** | Cloud infrastructure provisioning | ☁️ AKS, Storage, Key Vault, Networking |
| **eip-infra-k8s-argocd-support** | Continuous deployment configurations | 🔄 ArgoCD Apps, Projects, Configurations |
| **eip-infra-k8s-support** | Kubernetes cluster post-config | 🛠️ Storage Classes, Istio, Autoscaling, Add-ons |
| **eip-infra-terraform-modules** | Terraform reusable modules | 📦 AKS, Storage, RBAC, Networking modules |
| **pep-eiap-potato-sourcing-matrix-pipeline-templates** | Shared CI/CD templates | 📋 Build, Deploy, Approval workflows |
| **potato-sourcing-argocd-configs** | Environment-specific ArgoCD configs | 🎯 Dev, QA, Prod deployment specs |
| **potato-sourcing-matrix-api-repo** | Application source code | 🚀 Python API, Dockerfile, Azure Pipeline |

---

# 🏗️ Part 2: Infrastructure Architecture

## 2.1 Cloud Infrastructure (Azure) - Terraform Stack

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     AZURE CLOUD PLATFORM                         │
│                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │   Resource       │  │   Resource       │  │  Resource    │  │
│  │   Group (RG)     │  │   Group (RG)     │  │  Group (RG)  │  │
│  │                  │  │                  │  │              │  │
│  │  ┌────────────┐  │  │  ┌────────────┐  │  │ ┌──────────┐ │  │
│  │  │   Storage  │  │  │  │   Azure    │  │  │ │  Key     │ │  │
│  │  │  Account   │  │  │  │   SQL      │  │  │ │  Vault   │ │  │
│  │  │  (Backend  │  │  │  │  Database  │  │  │ │          │ │  │
│  │  │   TF)      │  │  │  │            │  │  │ │  (Secrets)│ │  │
│  │  └────────────┘  │  │  └────────────┘  │  │ └──────────┘ │  │
│  │  ┌────────────┐  │  │  ┌────────────┐  │  │ ┌──────────┐ │  │
│  │  │  Managed   │  │  │  │   Event    │  │  │ │   ACR    │ │  │
│  │  │  Identity  │  │  │  │   Hubs     │  │  │ │  (Images)│ │  │
│  │  └────────────┘  │  │  └────────────┘  │  │ └──────────┘ │  │
│  │                  │  │                  │  │              │  │
│  └──────────────────┘  └──────────────────┘  └──────────────┘  │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │               NETWORKING (Virtual Network)              │   │
│  │                                                         │   │
│  │  ┌──────────────────┐      ┌──────────────────────┐   │   │
│  │  │   Subnets        │──────│  Network Security    │   │   │
│  │  │   - AKS Subnet   │      │   Groups (NSG)       │   │   │
│  │  │   - App Subnet   │      │   - Ingress Rules    │   │   │
│  │  │                  │      │   - Egress Rules     │   │   │
│  │  └──────────────────┘      └──────────────────────┘   │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         AKS CLUSTERS (Kubernetes)                       │   │
│  │                                                         │   │
│  │  ┌─────────────────┐    ┌──────────────────────┐      │   │
│  │  │  Cluster Name   │    │  Node Pools          │      │   │
│  │  │ pep-eiap-nonprod│    │  - System Node Pool  │      │   │
│  │  │ -eus-global-01  │    │  - User Node Pool    │      │   │
│  │  │ -aks            │    │  - GPU Node Pool     │      │   │
│  │  │                 │    │  (optional)          │      │   │
│  │  └─────────────────┘    └──────────────────────┘      │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 2.1.1 Infrastructure Components (via Terraform)

**Environments Deployed:**
- **NONPROD** (Dev, QA, Sandbox)
- **PREPROD** (Pre-production)
- **PROD** (Production)
- **PROD-DR** (Disaster Recovery)

**Regions:**
- **EUS** (East US)
- **SCUS** (South Central US)
- **GWC**, **SUK**, **SEA**, etc. (Global expansion regions)

### 2.1.2 Terraform Module Structure

```
eip-infra-terraform-modules/
└── modules/
    ├── aks/                          # Azure Kubernetes Service
    │   ├── variables.tf
    │   ├── main.tf
    │   ├── outputs.tf
    │   └── cluster configuration
    │
    ├── storage-account/              # Azure Storage (Backend state + app data)
    │   ├── variables.tf
    │   ├── main.tf
    │   └── outputs.tf
    │
    ├── key-vault/                    # Azure Key Vault (Secrets management)
    │   ├── variables.tf
    │   ├── main.tf
    │   └── outputs.tf
    │
    ├── managed-identity/             # Azure Managed Identity (RBAC)
    │   ├── variables.tf
    │   ├── main.tf
    │   └── outputs.tf
    │
    ├── acr/                          # Azure Container Registry
    │   ├── variables.tf
    │   ├── main.tf
    │   └── outputs.tf
    │
    ├── event-hubs/                   # Azure Event Hubs (Messaging)
    │   ├── variables.tf
    │   ├── main.tf
    │   └── outputs.tf
    │
    ├── networking/                   # VNet, Subnets, NSG
    │   ├── variables.tf
    │   ├── main.tf
    │   └── outputs.tf
    │
    └── federated-credentials/        # Workload Identity Federation
        ├── variables.tf
        ├── main.tf
        └── outputs.tf
```

### 2.1.3 Azure Pipelines for Infrastructure

**File:** `eip-infra-azure-terraform-support/azure-pipelines.yml`

**Key Parameters:**
```yaml
- Functional_Area: eiap, edap, pfna, snt, cmp, aisp, etc.
- Service_Principal: NONPROD_K8S_SPN, PREPROD_K8S_SPN, PROD_K8S_SPN
- Environment: nonprod, preprod, prod, prod-dr
- Region: scus, eus, gwc, suk, sea, ae, na, essa, apac
- ResourceType: managed-identity, storage-account, aks, key-vault, acr, evh, etc.
```

**Terraform State Management:**
```yaml
Backend Storage Accounts:
- NONPROD: pe1003auto01tf01sa / eiap-storage-container
- PREPROD: pe2003auto01tf01sa / eiap-storage-container
- PROD: pe3003auto01tf01sa / eiap-storage-container

State files stored per functional area:
- eiap/
- edap/
- pfna/
- snt/
- cmp/
- etc.
```

**Agent Pools (Self-Hosted):**
```yaml
- nonprod_eus_agents: pep-eiap-nonprod-eus-infra-02-aks-agents
- nonprod_scus_agents: pep-eiap-nonprod-eus-infra-02-aks-agents
- preprod_eus_agents: pep-eiap-preprod-eus-infra-02-aks-agents
- preprod_scus_agents: pep-eiap-preprod-scus-infra-02-aks-agents
- prod_eus_agents: pep-eiap-prod-eus-infra-02-aks-agents
- prod_scus_agents: pep-eiap-prod-scus-infra-02-aks-agents
```

---

## 2.2 Kubernetes Cluster Post-Provisioning

**File:** `eip-infra-k8s-support/aks-post-provisioning.yml`

### Components Installed:

#### Storage Classes
- Azure Disk (Standard/Premium)
- Azure File Share (NFS)
- AWS S3, EBS, EFS (for multi-cloud)

#### Service Mesh & Networking
- **Istio** (Traffic management, security, observability)
  - VirtualServices
  - DestinationRules
  - EnvoyFilters
  - Gateways

#### Autoscaling Solutions
- **HPA** (Horizontal Pod Autoscaler) - CPU/Memory based
- **KEDA** (Kubernetes Event Autoscaling)
  - Kafka scaling
  - Redis scaling
  - EventHub scaling
  - Blob Storage scaling
  - Prometheus metrics scaling

#### Security & Access
- **Pod Disruption Budgets (PDB)**
- **Network Policies**
- **RBAC** (Role-Based Access Control)
- **ServiceAccounts** with RBAC bindings

#### Monitoring & Observability
- **AppDynamics** (APM sidecar injection)
- **Prometheus** (Metrics collection)
- **Logs** (Azure Monitor / ELK)

#### GPU Support (Optional)
- **NVIDIA GPU Operator** (for ML/AI workloads)

#### Ansible-based Configuration
- Uses Python 3.8 + Ansible 4.x
- Orchestrates cluster post-deployment tasks
- Configurable per cluster

---

# 🚀 Part 3: Application Deployment Architecture

## 3.1 Helm Chart Structure

The EIP Helm Chart is an **Umbrella Chart** system with **3-level hierarchy**:

```
┌──────────────────────────────────────────────────┐
│           UMBRELLACHART (Entry Point)            │
│              (Chart.yaml v2.2.4)                 │
│         What you install with: helm install      │
└──────────────────────────────────────────────────┘
                        │
                        │ depends on
                        ├────────────────────┬─────────────────────┐
                        ▼                    ▼                     ▼
        ┌──────────────────────────┐ ┌─────────────────┐ ┌─────────────────┐
        │     APP-CHART v1.3.2     │ │PLATFORM-CHART   │ │ values-*.yaml   │
        │ (Workload Templates)     │ │   v1.3.3        │ │  (Overrides)    │
        │                          │ │(Infrastructure) │ │                 │
        └──────────────────────────┘ └─────────────────┘ └─────────────────┘
                        │                    │                    │
           ┌────────────┴────────────┐       │         ┌──────────┴──────────┐
           │                         │       │         │                     │
           ▼                         ▼       ▼         ▼                     ▼
        Deployment          CronJob         HPA        VirtualService      Secrets
        StatefulSet         Service         PDB        DestinationRule      Storage
        Argo Rollout        ConfigMap       Scaling    EnvoyFilter          KEDA
        ServiceAccount       Experiment      KEDA      SecretProviderClass  PV/PVC
                             AnalysisTemplate
```

### 3.1.1 APP-CHART (Workload Layer)

**Purpose:** Define application workload objects

**Templates:**

```
app-chart/templates/
├── deployment.yaml              # Standard Kubernetes Deployment
├── statefulset.yaml             # Stateful application (databases, caches)
├── rollout.yaml                 # Argo Rollouts (Canary/Blue-Green)
├── service.yaml                 # ClusterIP/NodePort/LoadBalancer Service
├── cronjob.yaml                 # Scheduled batch jobs
├── serviceaccount.yaml          # RBAC ServiceAccount + tokens
├── configmap.yaml               # Environment variables & configs
├── configmap-from-file.yaml     # File-based configs (JSON, YAML)
├── experiment.yaml              # Argo Rollouts A/B Testing
├── analysistemplate.yaml        # Argo Rollouts success metrics
└── _helpers.tpl                 # Shared template functions
```

**Key Features:**

| Feature | Control Flag | Purpose |
|---------|--------------|---------|
| Deployment | `app-chart.deployment.enabled` | Standard workload |
| Rollout | `app-chart.rollout.enabled` | Advanced deployment strategy |
| Service | `app-chart.service.enabled` | Network access |
| CronJob | `app-chart.cronjob.enabled` | Scheduled tasks |
| StatefulSet | `app-chart.statefulset.enabled` | Stateful workloads |
| Sidecar | `app-chart.sidecar.enabled` | APM, proxy, logging sidecars |

### 3.1.2 PLATFORM-CHART (Infrastructure Layer)

**Purpose:** Define cluster-level infrastructure objects

**Templates:**

```
platform-chart/templates/
├── hpa.yaml                     # Horizontal Pod Autoscaler
├── pdb.yaml                     # Pod Disruption Budget (availability)
├── virtualservice.yaml          # Istio traffic management
├── destinationrule.yaml         # Istio load balancing subsets
├── envoyfilter.yaml             # Istio Envoy proxy customization
├── kedascaledobject.yaml        # Event-driven autoscaling (Kafka, Redis, EventHub)
├── pv.yaml / pvc.yaml           # Persistent storage
├── storageclass.yaml            # Storage provisioning
├── secretProviderClass.yaml     # Azure Key Vault CSI integration
├── gw-patch-job.yaml            # Post-install Istio Gateway patch
└── _helpers.tpl                 # Shared helpers
```

**Key Features:**

| Feature | Control Flag | Purpose |
|---------|--------------|---------|
| HPA | `platform-chart.autoscalingEnabled` | CPU/Memory-based scaling |
| PDB | `platform-chart.pdbEnabled` | Ensure availability during disruptions |
| VirtualService | `platform-chart.virtualService.enabled` | Istio routing, retries, CORS |
| DestinationRule | `platform-chart.destinationRule.enabled` | Subset definitions, traffic policies |
| EnvoyFilter | `platform-chart.envoyfilter.enabled` | Custom Envoy proxy rules |
| KEDA | `platform-chart.keda.enabled` | Event-driven autoscaling |
| Storage | `platform-chart.pv.enabled` / `storageClass.enabled` | Persistent data |
| Key Vault | `platform-chart.secretManagement.enabled` | Azure Key Vault integration |

### 3.1.3 Umbrella Chart Values Hierarchy

```yaml
# umbrellachart/values.yaml (base defaults)
global:
  nameOverride: ""
  namespace: "default"
  
app-chart:
  enabled: true

platform-chart:
  enabled: true

# --- Environment-specific overrides (applied with -f flag) ---

# values-fivestar-ivr-blue-green.yaml
global:
  deployment:
    enabled: false
  rollout:
    enabled: true
    strategy: blueGreen
  
# values-cronjob.yaml
global:
  deployment:
    enabled: false
  cronjob:
    enabled: true

# values-apm.yaml
global:
  sidecar:
    enabled: true
    type: apm  # AppDynamics

# values-overrides-aws.yaml
platform-chart:
  awsStorageClass:
    enabled: true
    isEBS: true
```

### 3.1.4 Deployment Strategies

The Helm chart supports **three main deployment strategies**:

#### 1️⃣ Standard Deployment

```yaml
# values-standard.yaml
global:
  deployment:
    enabled: true           # Use Deployment
  rollout:
    enabled: false          # Disable Argo Rollouts
  service:
    enabled: true
    type: ClusterIP
```

**Behavior:** Standard Kubernetes rolling update

#### 2️⃣ Canary Deployment (Argo Rollouts)

```yaml
# values-fivestar-ivr-canary.yaml
global:
  deployment:
    enabled: false          # Disable standard Deployment
  rollout:
    enabled: true           # Use Argo Rollouts
    strategy: canary        # Canary strategy
    minReadySeconds: 10
    revisionHistoryLimit: 2
    canary:
      steps:
        - setWeight: 20     # Route 20% traffic
          pause: {duration: 10}
        - setWeight: 40     # Route 40% traffic
          pause: {duration: 10}
        - setWeight: 60
          pause: {duration: 10}
        - setWeight: 80
          pause: {duration: 10}
        # Remaining 20% routed after all steps
```

**Flow:**
```
1. New version starts: 0% traffic
2. Step 1: 20% traffic → verify metrics
3. Step 2: 40% traffic → verify metrics
4. Step 3: 60% traffic → verify metrics
5. Step 4: 80% traffic → verify metrics
6. Final: 100% traffic → complete
7. Old version → terminated
```

**AnalysisTemplate Integration:**
```yaml
analysisTemplates:
  enabled: true
  failureLimit: 3
  metrics:
    - name: success_rate
      interval: 1m
      query: "Prometheus query here"
      failureLimit: 3
```

#### 3️⃣ Blue-Green Deployment (Argo Rollouts)

```yaml
# values-fivestar-ivr-blue-green.yaml
global:
  rollout:
    enabled: true
    strategy: blueGreen
    blueGreen:
      previewReplicaCount: 1           # Green pods ready before switch
      autoPromotionEnabled: true       # Automatic promotion
      autoPromotionSeconds: 30         # Wait 30s before promotion
      scaleDownDelaySeconds: 30        # Keep blue running for 30s
      abortScaleDownDelaySeconds: 30   # Rollback delay
```

**Flow:**
```
1. BLUE ACTIVE: Current version (stable)
2. GREEN DEPLOYED: New version starts (preview)
3. VALIDATION: Run tests against green
4. PROMOTION: Traffic switches to green
5. SCALE DOWN: Blue terminates after delay
6. On Error: Green terminates, blue continues
```

---

## 3.2 ArgoCD GitOps Deployment

### 3.2.1 Architecture

```
┌─────────────────────────────────────────────────────┐
│              ArgoCD (Continuous Delivery)           │
│     https://argocd.{cluster}.{region}.pepsico.io   │
└─────────────────────────────────────────────────────┘
              │                        │
              │ monitors               │ syncs to
              │                        ▼
    ┌────────────────────┐   ┌──────────────────────┐
    │  Git Repositories  │   │  Kubernetes Cluster  │
    │                    │   │  (AKS)               │
    │ - ApplicationSource│   │                      │
    │ - Application CRDs │   │ - Namespaces         │
    │ - ArgoCD Projects  │   │ - Deployments        │
    │                    │   │ - Services           │
    └────────────────────┘   │ - Helm Releases      │
          │                  │ - Custom Resources   │
          │                  └──────────────────────┘
          │
    ┌─────▼──────────────────────────────────────┐
    │  Trigger: Git Push / ArgoCD Sync           │
    │  1. Detect change in Git                   │
    │  2. Compare desired (Git) vs actual (k8s)  │
    │  3. Sync: Apply manifests to cluster       │
    │  4. Monitor: Track sync status & health    │
    └──────────────────────────────────────────┘
```

### 3.2.2 Repository Structure

**File:** `eip-infra-k8s-argocd-support/`

```
eip-infra-k8s-argocd-support/
├── README.md
├── aisp/
├── cgf/
├── cmp/                  # Per-functional-area configs
├── dps/
├── eiap/
├── infratools/
├── pbna/
├── pepgenx/
├── pfna/
├── snt/
└── templates/
    └── images/          # Architecture diagrams
```

### 3.2.3 ArgoCD Application ConfigMap Structure

**Stored as:** ConfigMaps in cluster namespace

**Contents:**
- **ApplicationSource:** Git repository URL + path
- **ArgoCD Project:** RBAC restrictions
- **Sync Policy:** Automatic/Manual sync, pruning, self-healing

### 3.2.4 Application Deployment Configs

**File:** `potato-sourcing-argocd-configs/`

```
potato-sourcing-argocd-configs/
├── dev/
│   └── pep-eiap-nonprod-eus-global-01-aks/
│       └── <app-name>/
│           └── helm-values.yaml      # Dev overrides
├── qa/
│   └── <cluster>/
│       └── <app-name>/
│           └── helm-values.yaml      # QA overrides
└── prod/
    └── <cluster>/
        └── <app-name>/
            └── helm-values.yaml      # Prod overrides
```

**helm-values.yaml Example:**
```yaml
global:
  namespace: "pep-eiap-apps"
  labels:
    app: "potato-sourcing-matrix-api"
    version: "1.2.3"
  
  deployment:
    enabled: true
    replicas: 3
    image:
      repository: "pepeiapnonprodcommonacr.azurecr.io/pep/eiap/potato-sourcing-matrix-api"
      tag: "20240315.5"
    
    resources:
      requests:
        memory: "512Mi"
        cpu: "250m"
      limits:
        memory: "1024Mi"
        cpu: "500m"
  
  service:
    enabled: true
    type: ClusterIP
    port: 8000

platform-chart:
  autoscalingEnabled: true
  hpa:
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70
  
  virtualService:
    enabled: true
    hosts:
      - "potato-sourcing-matrix-api.dev.eiap.pepsico.io"
    gateways:
      - "pep-eiap/main-gateway"
    retries:
      attempts: 3
      perTryTimeout: 10s
```

---

# 📊 Part 4: CI/CD Pipeline Flow

## 4.1 Complete Application Lifecycle

```
┌─────────────────────────────────────────────────────────────────────┐
│          Developer commits code to feature branch                    │
└────────────────────┬────────────────────────────────────────────────┘
                     │
                     ▼
         ┌──────────────────────────┐
         │  TRIGGER: Git Push Event │
         │  Branch: dev/qa/main     │
         └────────┬─────────────────┘
                  │
                  ▼
    ┌─────────────────────────────────────────┐
    │  STAGE 1: CI_Build (Compilation)        │
    │                                         │
    │  - Python: Run tests, coverage          │
    │  - SonarQube scan (quality gate)        │
    │  - Fortify SAST (security scan)         │
    │  - Snyk scan (dependency check)         │
    │  - Build Docker image (Kaniko)          │
    │  - Push to ACR (Azure Container Reg)    │
    │  - Publish artifacts                    │
    └────────────┬────────────────────────────┘
                 │ (if CI succeeds)
                 ▼
      ┌──────────────────────────────────────┐
      │  STAGE 2: DEV Deployment             │
      │  (Auto for dev/feature branch)       │
      │                                      │
      │  - Clone manifest repository         │
      │  - Update helm-values.yaml (tag)     │
      │  - Create Git PR                     │
      │  - Auto-merge PR (service account)   │
      │  - ArgoCD detects Git change         │
      │  - ArgoCD syncs to dev cluster       │
      └─────────────────┬────────────────────┘
                        │
                        ▼
      ┌──────────────────────────────────────┐
      │  STAGE 3: QA Deployment              │
      │  (Auto if tests pass in dev)         │
      │                                      │
      │  - Repeat manifest update            │
      │  - Auto-merge PR to QA branch        │
      │  - ArgoCD syncs to QA cluster        │
      └─────────────────┬────────────────────┘
                        │
                        ▼
      ┌──────────────────────────────────────┐
      │  STAGE 4: Prod Approval              │
      │  (Manual approval required)          │
      │                                      │
      │  - Create PR to prod branch          │
      │  - WAIT for manual approval          │
      │  - Approval condition: CR# required  │
      │  - Approver reviews & approves PR    │
      └─────────────────┬────────────────────┘
                        │ (if approved)
                        ▼
      ┌──────────────────────────────────────┐
      │  STAGE 5: PROD Deployment            │
      │  (After approval)                    │
      │                                      │
      │  - ACR image import (nonprod→prod)   │
      │  - Update prod helm-values.yaml      │
      │  - Merge PR to prod branch           │
      │  - ArgoCD syncs to prod cluster      │
      │  - Argo Rollout canary (gradual)     │
      │  - Monitor metrics (analysis)        │
      │  - Complete rollout or rollback      │
      └──────────────────────────────────────┘
```

## 4.2 Detailed Pipeline Stages

### STAGE 1: CI Build

**File:** `pep-eiap-potato-sourcing-matrix-pipeline-templates/build.yaml`

**Steps:**

1. **Code Compilation & Testing**
   ```bash
   python3 -m coverage run --source=src/,tests
   python3 -m coverage xml
   python3 -m coverage report -i -m
   ```

2. **SonarQube Code Quality Gate**
   ```yaml
   Task: SonarQubePrepare
   - Scan source code
   - Check quality metrics
   - Block if gate fails (sonar.qualitygate.wait=true)
   ```

3. **Security Scanning**
   - **Fortify SAST:** Application security vulnerability scan
   - **Snyk:** Container & dependency vulnerability scan
   ```bash
   snyk auth $(SNYK_AUTH_TOKEN)
   snyk container monitor <image>:<tag> --app-vulns
   ```

4. **Docker Image Build & Push**
   ```yaml
   Tool: Kaniko (in-cluster build, no Docker daemon)
   
   Process:
   - Mount PVC: $(PVC_MOUNT)/$(Build.DefinitionName)-$(Build.BuildNumber)
   - Copy source code to PVC
   - Create Kaniko Job YAML
   - Submit to Kubernetes
   - Wait for completion (20 min timeout)
   - Retrieve logs
   - Clean up
   
   Image Destination: 
   $(npglobalacrurl)/$(acrrepoprefix)/$(acrreponame):$(Build.BuildNumber)
   e.g., pepeiapnonprodcommonacr.azurecr.io/pep/eiap/potato-sourcing-matrix-api:20240315.5
   ```

5. **Artifact Publishing**
   ```bash
   PublishBuildArtifacts → Drop folder
   - Build logs
   - Test reports
   - Coverage reports
   ```

### STAGE 2-4: Deployment to Dev/QA/Prod

**File:** `pep-eiap-potato-sourcing-matrix-pipeline-templates/deploy-aks.yaml`

**Steps:**

1. **Clone Manifest Repository**
   ```bash
   git clone -b $(manifest_branch) $(manifest_repo_url)
   
   Repository: potato-sourcing-argocd-configs (GitOps repo)
   Branch: dev / qa / prod
   ```

2. **Download Build Artifacts**
   ```bash
   - download: current
     patterns: '**'
   ```

3. **Validate Deployment File Exists**
   ```bash
   if [ -e $(System.DefaultWorkingDirectory)/$(manifest_repo_name)/$(env)/${{ parameters.endpoint }}/$(Build.Repository.Name)/$(deploymentfile) ]; then
     echo "Deployment descriptor yaml exists"
   else
     exit 1  # Fail if missing
   fi
   ```

4. **Update Image Tag in helm-values.yaml**
   ```bash
   # Extract old tag
   image=$(grep 'tag:' helm-values.yaml | tail -n1 | awk '{ print $2}')
   
   # Replace with new build tag
   sed -i s/$image/"$(tag)"/ helm-values.yaml
   
   # Verify
   cat helm-values.yaml
   ```

5. **Commit & Push to Git**
   ```bash
   git checkout -b $(manifest_pr_branch)
   git add ./$(env)/${{ parameters.endpoint }}/$(Build.Repository.Name)/$(deploymentfile)
   git commit -m "updated manifest file with $(tag)"
   git push https://$(svcuser):$(svcPersonalAccessToken)@$(manifest_repo_url)
   ```

6. **Create Pull Request**
   ```powershell
   az repos pr create \
     --project $(System.TeamProject) \
     --repository $(manifest_repo_name) \
     --target-branch $(MANIFEST_BRANCH) \
     --source-branch $(MANIFEST_PR_BRANCH) \
     --title "deployment $(tag)"
   ```

7. **Merge PR (Non-Prod Only)**
   ```powershell
   # For Dev/QA: Auto-merge with service account
   az repos pr set-vote --id $(PR_NUM) --vote approve
   az repos pr update \
     --id $(PR_NUM) \
     --status completed \
     --delete-source-branch true \
     --bypass-policy true
   
   # For Prod: WAIT for manual approval
   # (Pipeline holds pending human review)
   ```

8. **ArgoCD Auto-Sync**
   ```
   ArgoCD detects Git change in manifest repo
   ↓
   Pulls new helm-values.yaml
   ↓
   Renders Helm chart with new image tag
   ↓
   Applies to target cluster namespace
   ↓
   Argo Rollout starts (canary/blue-green if enabled)
   ↓
   Monitors deployment health & metrics
   ```

### Production Promotion Flow

**Prod-Only Logic:**

```yaml
# Spring-CICD.yaml Stage: prod_approval
condition: |
  or(
    and(
      eq(variables['deployOnly'], 'true'),
      ne(variables['cr_number'], 'null'),           # CR # required!
      eq(variables.isReleaseBranch, true),
      eq(variables['restartOnly'], 'false')
    ),
    and(
      eq(variables.isReleaseBranch, true),
      ne(variables['cr_number'], 'null'),           # CR # required!
      eq(variables['restartOnly'], 'false'),
      succeeded('CI_Build')
    )
  )

Actions:
1. Create PR (waiting state)
2. PAUSE: Manual approval required
3. Pipeline: Hold until user approves
4. On Approval: Proceed to prod deployment
5. On Rejection: Stop (no prod push)
```

---

## 4.3 Pipeline Variables

**File:** `pep-eiap-potato-sourcing-matrix-pipeline-templates/variables.yaml`

**Common Variables:**

```yaml
# ACR Configuration
npglobalacrurl: pepeiapnonprodcommonacr.azurecr.io
acrrepoprefix: pep/eiap
acrreponame: potato-sourcing-matrix-api

# AKS Clusters
aks-nonprod-eus: pep-eiap-nonprod-eus-global-01-aks
aks-preprod-eus: pep-eiap-preprod-eus-global-01-aks

# Namespaces
aksnamespace-dev: pep-eiap-apps-dev
aksnamespace-qa: pep-eiap-apps-qa
aksnamespace-prod: pep-eiap-apps-prod

# Manifest Repository
manifest_repo_url: pepsicoit.visualstudio.com/EIAP_DevOps/_git/potato-sourcing-argocd-configs
manifest_repo_name: potato-sourcing-argocd-configs
manifest_branch: dev/qa/prod

# Security Scanning
SONARPROJECTKEY: potato-sourcing-matrix-api
CI_Token: <Fortify SSC token>
SNYK_AUTH_TOKEN: <Snyk API token>

# Build Configuration
java17path: /usr/lib/jvm/java-17-openjdk
java11path: /usr/lib/jvm/java-11-openjdk
Appname: potato-sourcing-matrix-api
```

---

# 🌐 Part 5: Service Mesh & Add-ons (Istio)

## 5.1 Istio Service Mesh Architecture

```
┌──────────────────────────────────────────────────────────────┐
│              ISTIO CONTROL PLANE                             │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Istiod (Pilot + Policy + Telemetry)                 │   │
│  │ - Service discovery                                  │   │
│  │ - Certificate management                             │   │
│  │ - Config distribution                                │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            ▼               ▼               ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  NAMESPACE 1     │ │  NAMESPACE 2     │ │  NAMESPACE 3     │
│  pep-eiap-apps   │ │  pep-eiap-infra  │ │  pep-eiap-system │
│                  │ │                  │ │                  │
│ ┌──────────────┐ │ │ ┌──────────────┐ │ │ ┌──────────────┐ │
│ │Pod (App-A)   │ │ │ │Pod (App-B)   │ │ │ │Pod (Proxy)   │ │
│ │              │ │ │ │              │ │ │ │              │ │
│ │┌────────────┐│ │ │ │┌────────────┐│ │ │ │┌────────────┐│ │
│ ││Envoy Proxy││ │ │ │││Envoy Proxy││ │ │ │││Envoy Proxy││ │ │
│ │└────────────┘│ │ │ │└────────────┘│ │ │ │└────────────┘│ │ │
│ └──────────────┘ │ │ └──────────────┘ │ │ └──────────────┘ │
│                  │ │                  │ │                  │
└──────────────────┘ └──────────────────┘ └──────────────────┘
        │                   │                      │
        │ observes          │ observes             │ observes
        └───────────────────┼──────────────────────┘
                            │
                            ▼
                ┌────────────────────────┐
                │  Prometheus Metrics    │
                │  Kiali Dashboard       │
                │  Jaeger Tracing        │
                │  Grafana Dashboards    │
                └────────────────────────┘
```

## 5.2 Istio Traffic Management

### VirtualService Configuration

**Template:** `eip-helm-chart/platform-chart/templates/virtualservice.yaml`

```yaml
# Generated from Helm values
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: potato-sourcing-matrix-api
  namespace: pep-eiap-apps
spec:
  hosts:
  - potato-sourcing-matrix-api.eiap.pepsico.io
  
  gateways:
  - pep-eiap/main-gateway  # Ingress Gateway
  
  http:
  # Route 1: API Traffic
  - match:
    - uri:
        prefix: "/api"
    route:
    - destination:
        host: potato-sourcing-matrix-api
        subset: v1
      weight: 100
    timeout: 10s
    retries:
      attempts: 3
      perTryTimeout: 5s
    corsPolicy:
      allowOrigins:
      - exact: "https://ui.eiap.pepsico.io"
      allowMethods:
      - GET
      - POST
      - PUT
      allowHeaders:
      - content-type
      - authorization
  
  # Route 2: Health Check
  - match:
    - uri:
        prefix: "/health"
    route:
    - destination:
        host: potato-sourcing-matrix-api
        subset: v1
    timeout: 2s
```

### DestinationRule Configuration

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: potato-sourcing-matrix-api
  namespace: pep-eiap-apps
spec:
  host: potato-sourcing-matrix-api
  
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 100
        http2MaxRequests: 1000
        maxRequestsPerConnection: 10
    
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 100
      minRequestVolume: 10
  
  subsets:
  - name: v1
    labels:
      version: v1
    trafficPolicy:
      connectionPool:
        tcp:
          maxConnections: 50
```

### EnvoyFilter for Custom Logic

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: EnvoyFilter
metadata:
  name: potato-sourcing-custom-headers
  namespace: pep-eiap-apps
spec:
  workloadSelector:
    labels:
      app: potato-sourcing-matrix-api
  
  configPatches:
  - applyTo: HTTP_FILTER
    match:
      context: SIDECAR_INBOUND
      listener:
        filterChain:
          filter:
            name: envoy.filters.network.http_connection_manager
    patch:
      operation: MERGE
      value:
        typed_config:
          '@type': type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
          codec_type: AUTO
          stat_prefix: ingress_http
```

## 5.3 Gateway Configuration

```yaml
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
    - "*.pepsico.io"
  
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "*.eiap.pepsico.io"
```

---

# ⚡ Part 6: KEDA Event-Driven Autoscaling

## 6.1 KEDA Scalers Supported

### Kafka Scaler

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: kafka-scaler
  namespace: pep-eiap-apps
spec:
  scaleTargetRef:
    name: kafka-consumer-app
  minReplicaCount: 2
  maxReplicaCount: 100
  
  triggers:
  - type: kafka
    metadata:
      bootstrapServers: kafka-broker-1:9092,kafka-broker-2:9092
      consumerGroup: potato-sourcing-consumer-group
      topic: potato-data-events
      lagThreshold: "100"  # Scale when lag > 100
      activationLagThreshold: "50"
```

### Redis Scaler

```yaml
- type: redis
  metadata:
    address: redis-service:6379
    listName: job-queue
    listLength: "30"  # Scale when list > 30
    dbIndex: "0"
```

### Azure Event Hub Scaler

```yaml
- type: azure-eventhub
  metadata:
    connectionFromAuth: pod
    storageConnection: azure-storage-key
    consumerGroup: $Default
    eventHubName: potato-sourcing-eventhub
    partitionId: "0"
    unprocessedEventThreshold: "100"
```

### Prometheus Custom Metrics

```yaml
- type: prometheus
  metadata:
    serverAddress: http://prometheus:9090
    metricName: http_requests_per_second
    query: sum(rate(http_requests_total[1m]))
    threshold: "1000"
```

---

# 🔐 Part 7: Security & Secrets Management

## 7.1 Azure Key Vault Integration

**SecretProviderClass Template:**

```yaml
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: potato-sourcing-secrets
  namespace: pep-eiap-apps
spec:
  provider: azure
  parameters:
    usePodIdentity: "false"
    useVMManagedIdentity: "true"
    userAssignedIdentityID: /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identity-name}
    keyvaultName: pep-eiap-kv-nonprod
    cloudEnv: AzurePublicCloud
    cloudEnvFileName: /etc/kubernetes/azure.json
    tenantId: {tenant-id}
    objects: |
      array:
        - |
          objectName: db-password
          objectType: secret
          objectAlias: DATABASE_PASSWORD
        - |
          objectName: api-key
          objectType: secret
          objectAlias: API_KEY
        - |
          objectName: ssl-cert
          objectType: secret
          objectAlias: SSL_CERTIFICATE
    syncSecret: "true"

# Usage in Pod:
# - volumeMounts:
#   - name: secrets-store
#     mountPath: "/mnt/secrets-store"
#     readOnly: true
# volumes:
# - name: secrets-store
#   csi:
#     driver: secrets-store.csi.k8s.io
#     readOnly: true
#     volumeAttributes:
#       secretProviderClass: potato-sourcing-secrets
```

## 7.2 Pod Security Policies

```yaml
apiVersion: policy/v1beta1
kind: PodDisruptionBudget
metadata:
  name: potato-sourcing-pdb
  namespace: pep-eiap-apps
spec:
  minAvailable: 1  # At least 1 pod must remain available
  selector:
    matchLabels:
      app: potato-sourcing-matrix-api
      tier: application
```

---

# 📊 Part 8: Monitoring & Observability

## 8.1 AppDynamics Integration

**APM Sidecar Injection:**

```yaml
# values-apm.yaml
global:
  sidecar:
    enabled: true
    type: appd
    appd:
      accountName: "pepsico-eiap"
      accessKey: "$(APPD_ACCESS_KEY)"
      controllerHost: "pepsico-eiap.saas.appdynamics.com"
      controllerPort: 443
      appName: "Potato-Sourcing-API"
      tierName: "backend"
      nodeName: "$(POD_NAME)"
```

**Helm Template injects sidecar:**

```yaml
spec:
  containers:
  - name: app
    image: "{{ .Values.global.image.repository }}:{{ .Values.global.image.tag }}"
  {{- if .Values.global.sidecar.enabled }}
  - name: appdynamics-agent
    image: appdynamics/java-agent:latest
    env:
    - name: APPDYNAMICS_AGENT_ACCOUNT_NAME
      value: "{{ .Values.global.sidecar.appd.accountName }}"
    - name: APPDYNAMICS_AGENT_APPLICATION_NAME
      value: "{{ .Values.global.sidecar.appd.appName }}"
  {{- end }}
```

## 8.2 Prometheus Metrics

**PrometheusRule:**

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: potato-sourcing-api-alerts
  namespace: pep-eiap-apps
spec:
  groups:
  - name: application.rules
    interval: 30s
    rules:
    - alert: HighErrorRate
      expr: |
        (sum(rate(http_requests_total{job="potato-sourcing-api",status=~"5.."}[5m])) /
         sum(rate(http_requests_total{job="potato-sourcing-api"}[5m]))) > 0.05
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High error rate on Potato Sourcing API"
    
    - alert: HighLatency
      expr: |
        histogram_quantile(0.95, rate(http_requests_duration_seconds_bucket{job="potato-sourcing-api"}[5m])) > 1
      for: 5m
      labels:
        severity: warning
```

---

# 🔄 Part 9: End-to-End Application Flow (Example)

## Scenario: Deploying Potato Sourcing Matrix API v1.2.3

### Step 1: Developer Commits to Feature Branch

```bash
git checkout -b feature/add-new-endpoint
# ... code changes ...
git add .
git commit -m "Add new sourcing endpoint"
git push origin feature/add-new-endpoint
```

### Step 2: Azure Pipeline Triggers

**Branch:** `feature/add-new-endpoint`  
**Trigger:** Automatic (configured in `azure-pipeline.yaml`)

### Step 3: CI Build Stage

```
┌─ Clone repository
├─ Install dependencies (pip install -r requirements.txt)
├─ Run unit tests (pytest)
├─ Calculate coverage (coverage report)
├─ SonarQube scan → ✓ PASS (quality gate met)
├─ Fortify SAST scan → ✓ PASS (no critical vulns)
├─ Snyk container scan → ✓ PASS (dependencies OK)
├─ Build Docker image (Kaniko)
│  └─ Image: pepeiapnonprodcommonacr.azurecr.io/pep/eiap/potato-sourcing-matrix-api:20240315.5
├─ Push to ACR → ✓ Success
└─ Publish artifacts → ✓ Complete
```

**Build Time:** ~15 minutes

### Step 4: Dev Deployment (Auto)

```
┌─ Branch detected: feature/add-new-endpoint → auto-deploys to DEV
├─ Stage: DEV (deploy-aks-env.yaml)
├─ Clone manifest repo: potato-sourcing-argocd-configs
├─ Checkout: branch = dev
├─ Update: dev/pep-eiap-nonprod-eus-global-01-aks/potato-sourcing-matrix-api/helm-values.yaml
│  └─ Change: tag: "20240315.4" → tag: "20240315.5"
├─ Git commit: "updated manifest file with 20240315.5"
├─ Create PR: branch dev-20240315-5 → target dev
├─ Merge PR: (auto-approved by service account)
├─ ArgoCD detects change in Git
├─ ArgoCD syncs: Render Helm chart + apply to dev cluster
│  └─ Namespace: pep-eiap-apps-dev
│  └─ Deployment: potato-sourcing-matrix-api
│  └─ Replicas: 2 (from helm-values.yaml)
│  └─ Image: ...:20240315.5
├─ Kubernetes pulls image from ACR
├─ New pod starts (Envoy sidecar injected by Istio)
├─ Health checks: ✓ Readiness ✓ Liveness
└─ VirtualService routes traffic → ✓ Active
```

**Deployment Time:** ~5 minutes

### Step 5: Test in Dev

```
Developer/QA team:
- Runs smoke tests
- Validates new endpoint: GET /api/v1/sourcing/matrix
- Checks AppDynamics metrics
- Reviews logs in Azure Monitor
```

### Step 6: QA Deployment (Auto)

**Triggered when:**
- Dev tests pass
- Branch: `dev` (merged from feature branch)

```
Same workflow as Dev:
- Clone manifest repo
- Update QA helm-values.yaml
- Create & merge PR
- ArgoCD syncs to QA cluster
- Namespace: pep-eiap-apps-qa
- Replicas: 3 (higher than dev)
```

### Step 7: Production Approval

**Branch:** `main` (release branch)

**Pipeline holds:**
```
Stage: prod_approval
Condition: CR# required (pep-eiap-potato-sourcing-matrix-api)
Action: WAIT for human approval
```

**Process:**
```
1. Change Request created: CR-2024-03-15-001
2. Engineering lead reviews deployment
3. Security team approves
4. Ops team approves
5. Manual approval given in Azure DevOps UI
```

### Step 8: Production Deployment

```
┌─ Approval confirmed
├─ Stage: PROD Deployment
├─ ACR image import: nonprod ACR → prod ACR
│  └─ Source: pepeiapnonprodcommonacr.azurecr.io/.../potato-sourcing-matrix-api:20240315.5
│  └─ Dest: pepeiapprodacr.azurecr.io/.../potato-sourcing-matrix-api:20240315.5
├─ Update manifest repo: potato-sourcing-argocd-configs/prod/...
├─ Merge PR to prod branch
├─ ArgoCD syncs to prod cluster(s)
│  └─ EUS Cluster + SCUS Cluster (multi-region)
├─ Namespace: pep-eiap-apps-prod
├─ Strategy: Canary Rollout (Argo Rollouts enabled)
│  ├─ Step 1: 20% traffic (5 min pause)
│  ├─ Step 2: 40% traffic (5 min pause)
│  ├─ Step 3: 60% traffic (5 min pause)
│  ├─ Step 4: 80% traffic (5 min pause)
│  └─ Step 5: 100% traffic (complete)
├─ Analysis Template monitors:
│  ├─ Success rate > 95%
│  ├─ Error rate < 1%
│  ├─ Latency p95 < 500ms
│  └─ All metrics ✓ PASS → Promotion
└─ Deployment Complete: v1.2.3 live in production
```

**Total Prod Deployment Time:** ~30 minutes (with canary monitoring)

### Step 9: Post-Deployment Validation

```
Monitoring dashboards:
┌─ Prometheus metrics ✓ Stable
├─ AppDynamics APM ✓ Normal response times
├─ Error rates ✓ < 0.1%
├─ Kiali service mesh ✓ All healthy
├─ Jaeger tracing ✓ No anomalies
├─ Azure Monitor logs ✓ No errors
└─ Alerts ✓ No critical issues

Production Status: ✓ GREEN ✓
Release: v1.2.3 → Production Complete
```

---

# 🎯 Part 10: Key Deployment Scenarios

## 10.1 Deploying a CronJob

```yaml
# values-cronjob.yaml
global:
  deployment:
    enabled: false  # No main deployment
  cronjob:
    enabled: true
    schedule: "0 2 * * *"  # 2 AM daily
    image:
      repository: "pepeiapnonprodcommonacr.azurecr.io/.../batch-job"
      tag: "20240315.5"
    
    container:
      args:
        - "/bin/bash"
        - "-c"
        - "python /app/job.py --task=sync-potatoes"
    
    resources:
      requests:
        memory: "256Mi"
        cpu: "100m"
      limits:
        memory: "512Mi"
        cpu: "250m"

platform-chart:
  pdb:
    enabled: false  # Not applicable to cron
```

## 10.2 Multi-Region Deployment

```yaml
# values-prod-multiregion.yaml
global:
  deployment:
    enabled: true
    replicas: 5  # Per region
  
  nodeSelector:
    region: "{{ .Values.region }}"  # eus / scus / etc.

# Deploy to both EUS and SCUS:
# helm install -f values-prod-multiregion.yaml \
#   -f values-eus.yaml potato-eus ./umbrellachart
# helm install -f values-prod-multiregion.yaml \
#   -f values-scus.yaml potato-scus ./umbrellachart
```

## 10.3 Blue-Green Deployment

```yaml
# values-bluegreen.yaml
global:
  rollout:
    enabled: true
    strategy: blueGreen
    blueGreen:
      previewReplicaCount: 3          # Green ready
      autoPromotionEnabled: true      # Auto switch
      autoPromotionSeconds: 60        # After 60s success
      scaleDownDelaySeconds: 300      # Keep blue 5 min

platform-chart:
  virtualService:
    enabled: true
  
  analysisTemplates:
    enabled: true
    failureLimit: 3
```

## 10.4 Canary with Custom Metrics

```yaml
# values-canary-analysis.yaml
global:
  rollout:
    enabled: true
    strategy: canary
    canary:
      steps:
        - setWeight: 10
          pause: {duration: 5m}
        - setWeight: 50
          pause: {duration: 10m}

platform-chart:
  analysisTemplates:
    enabled: true
    metrics:
      - name: success-rate
        interval: 1m
        count: 10  # Check 10 times
        failureLimit: 2
        provider:
          prometheus:
            query: |
              sum(rate(http_requests_total{status=~"2.."}[1m])) /
              sum(rate(http_requests_total[1m]))
```

---

# 📋 Part 11: Configuration Checklist

## Pre-Deployment Checklist

- [ ] **Code Review:** Peer review completed
- [ ] **Testing:** Unit tests + integration tests pass
- [ ] **Security:** SonarQube, Fortify, Snyk scans pass
- [ ] **Documentation:** README, API docs updated
- [ ] **Change Request:** CR created (for prod)
- [ ] **Resource Planning:** Compute, memory, storage verified
- [ ] **Monitoring:** Dashboards, alerts configured
- [ ] **Rollback Plan:** Rollback procedure documented

## Helm Chart Configuration

- [ ] **values.yaml:** Base values defined
- [ ] **values-dev.yaml:** Dev environment overrides
- [ ] **values-qa.yaml:** QA environment overrides
- [ ] **values-prod.yaml:** Prod environment overrides
- [ ] **Deployment:** Replicas, resources correct
- [ ] **Service:** Port, type, selector correct
- [ ] **Health Checks:** Readiness & liveness probes configured
- [ ] **Secrets:** SecretProviderClass linked to Key Vault

## ArgoCD Configuration

- [ ] **Manifest Repo:** Cloned to deployment target
- [ ] **Application CRD:** Created in cluster
- [ ] **GitOps Repo:** Branch structure (dev/qa/prod)
- [ ] **Sync Policy:** Auto-sync enabled
- [ ] **Health Checks:** Synced & healthy status

## Istio Configuration

- [ ] **Namespace Injection:** Sidecar injection labels
- [ ] **VirtualService:** Routes defined
- [ ] **DestinationRule:** Subsets configured
- [ ] **Gateway:** Ingress configured
- [ ] **Network Policy:** Egress/ingress rules

---

# 🚨 Troubleshooting Guide

## Common Issues

### Issue 1: Pod fails to start (ImagePullBackOff)

**Diagnosis:**
```bash
kubectl describe pod <pod-name> -n <namespace>
# Check Events section
```

**Solutions:**
- Verify ACR credentials (imagePullSecrets)
- Check image tag exists in ACR
- Verify pod has network access to ACR

### Issue 2: ArgoCD not syncing

**Diagnosis:**
```bash
# Check ArgoCD app status
kubectl get application <app-name> -n argocd -o yaml
argocd app get <app-name>
```

**Solutions:**
- Verify Git repo access (SSH key, PAT token)
- Check helm-values.yaml syntax
- Verify namespace exists
- Run ArgoCD hard refresh

### Issue 3: Canary rollout stuck

**Diagnosis:**
```bash
kubectl describe rollout <rollout-name> -n <namespace>
kubectl get analysisrun -n <namespace>
```

**Solutions:**
- Check AnalysisTemplate metrics
- Verify Prometheus queries return data
- Check pod logs for errors
- Manual abort and retry

---

# 📚 Reference Documentation

## Repository Links

1. **eip-helm-chart:** Central Helm repository
   - Sub-charts: app-chart, platform-chart, umbrellachart
   - Multiple values-*.yaml examples

2. **eip-infra-azure-terraform-support:** Infrastructure provisioning
   - Azure Pipelines for Terraform
   - State management backend
   - Multi-environment support

3. **eip-infra-k8s-support:** Kubernetes post-config
   - Ansible playbooks
   - Storage classes, Istio, KEDA setup

4. **potato-sourcing-argocd-configs:** Application deployment specs
   - Per-environment helm-values.yaml
   - Development → Production progression

5. **pep-eiap-potato-sourcing-matrix-pipeline-templates:** CI/CD templates
   - Build stages (SonarQube, Fortify, Snyk)
   - Deployment automation
   - Approval workflows

## Key Technologies

| Component | Purpose | Version |
|-----------|---------|---------|
| **Kubernetes** | Container orchestration | v1.28+ |
| **Helm** | Package manager | v3.x |
| **Argo Rollouts** | Advanced deployments | v1.6+ |
| **ArgoCD** | GitOps CD | v2.8+ |
| **Istio** | Service mesh | v1.18+ |
| **KEDA** | Event autoscaling | v2.12+ |
| **Prometheus** | Metrics | v2.40+ |
| **Jaeger** | Tracing | v1.41+ |
| **AppDynamics** | APM | Enterprise |
| **Terraform** | IaC | v1.5+ |
| **Azure DevOps** | CI/CD | Cloud |

---

# 🎓 Learning Path

**Level 1: Foundations**
1. Learn Kubernetes basics (Deployment, Service, Pod)
2. Understand Helm charts (values, templates)
3. Study Azure resources (AKS, ACR, Key Vault)

**Level 2: Intermediate**
1. Master Argo Rollouts (canary, blue-green)
2. Configure Istio VirtualService & DestinationRule
3. Setup ArgoCD applications

**Level 3: Advanced**
1. Implement KEDA scalers
2. Design multi-region deployments
3. Optimize observability (Prometheus, Jaeger, AppDynamics)
4. Terraform module development

---

**Document Generated:** October 29, 2026  
**Organization:** PepsiCo EIP  
**Version:** 1.0
