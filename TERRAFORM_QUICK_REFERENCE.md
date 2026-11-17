# Terraform Quick Reference & Visual Diagrams
## Interview-Ready Cheat Sheet with Architecture Flows

---

## 📊 Architecture Overview Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    TERRAFORM EXECUTION ARCHITECTURE                     │
└─────────────────────────────────────────────────────────────────────────┘

                        ┌────────────────────────┐
                        │  Azure DevOps Pipeline │
                        │ (azure-pipelines.yml)  │
                        └───────────┬────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
        ┌──────────────────┐  ┌─────▼─────┐  ┌───────────────┐
        │ Select Parameters│  │   Git     │  │ Get Secrets   │
        │ (Environment,    │  │  Checkout │  │ (SPN Creds)   │
        │  Region, Type)   │  │           │  │               │
        └──────────────────┘  └─────┬─────┘  └───────────────┘
                                    │
                ┌───────────────────┼───────────────────┐
                │                   │                   │
        ┌──────▼──────────┐ ┌──────▼──────────┐ ┌─────▼────────────┐
        │  Terraform Init  │ │ Backend Storage │ │  State File      │
        │                  │ │  (Azure Blob)   │ │  (terraform.tfstate)
        │ Downloads:       │ │                  │ │  Locked during   │
        │ • Modules        │ │  Container:      │ │  execution       │
        │ • Providers      │ │  eiap-storage-   │ │                  │
        │ • Plugins        │ │  container       │ │  Serialized      │
        └──────┬───────────┘ └──────────────────┘ │  JSON of all     │
               │                                   │  resources       │
               └───────────────────┬───────────────┴──────────────────┘
                                   │
                        ┌──────────▼──────────┐
                        │  Load Tfvars Files  │
                        │                     │
                        │ • defaults-*.tfvars │
                        │ • mandatory-*.tfvars│
                        │ • nodepools-*.tfvars│
                        └──────────┬──────────┘
                                   │
                        ┌──────────▼──────────┐
                        │ Terraform Plan      │
                        │                     │
                        │ Compares:           │
                        │ Desired (tfvars)    │
                        │ vs                  │
                        │ Current (state file)│
                        │ vs                  │
                        │ Actual (Azure)      │
                        └──────────┬──────────┘
                                   │
                        ┌──────────▼──────────┐
                        │ Show Plan Output    │
                        │                     │
                        │ "Will create:       │
                        │  - 1 AKS cluster    │
                        │  - 2 node pools     │
                        │  - X networking     │
                        │   resources"        │
                        └──────────┬──────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │    Manual Approval Gate     │
                    │ (Team lead reviews plan)    │
                    │  ✓ Looks good → Proceed    │
                    │  ✗ Issues found → Reject   │
                    └──────────────┬──────────────┘
                                   │
                        ┌──────────▼──────────┐
                        │ Terraform Apply     │
                        │                     │
                        │ Executes:           │
                        │ • Create resources  │
                        │ • Update resources  │
                        │ • Delete resources  │
                        └──────────┬──────────┘
                                   │
    ┌──────────────────────────────┼──────────────────────────────┐
    │                              │                              │
    ▼                              ▼                              ▼
┌─────────────┐         ┌─────────────────────┐      ┌────────────────┐
│ AKS Cluster │         │  Node Pools         │      │  Networking    │
│ Created     │         │  Created            │      │  Resources     │
│             │         │  - System Pool      │      │  - Subnets     │
│ Features:   │         │  - App Pool         │      │  - NSGs        │
│ • Kubelet   │         │  - Build Pool       │      │  - Route Tabs  │
│ • API Srv   │         │                     │      │                │
│ • Scheduler │         │  Each pool:         │      │  All locked    │
│ • ETCD      │         │  - Auto-scaling     │      │  in new state  │
│             │         │  - Taints/Labels    │      │  file          │
│ Updates     │         │  - VM sizes         │      │                │
│ state file  │         │  - OS configuration │      │                │
└─────────────┘         └─────────────────────┘      └────────────────┘
```

---

## 🔄 Three Repositories Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                    THREE GIT REPOSITORIES                        │
└──────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────┐
│  REPO 1: eip-infra-terraform-modules   │  ← BLUEPRINT LIBRARY
├────────────────────────────────────────┤
│                                        │
│  modules/                              │
│  ├── azure_kubernetes_services/       │
│  │   ├── aks-nodepools.tf             │
│  │   ├── variables.tf                 │
│  │   ├── data.tf                      │
│  │   ├── outputs.tf                   │
│  │   └── versions.tf                  │
│  ├── storage_account/                 │
│  ├── key_vault/                       │
│  ├── managed_identity/                │
│  ├── evh/                             │
│  └── ... 15+ more modules             │
│                                        │
│  These are REUSABLE RECIPES            │
│  Same module for 100 clusters          │
│                                        │
│  Git Commits:                          │
│  - terraform module updates            │
│  - New features                        │
│  - Bug fixes                           │
└────────────────────────────────────────┘
            ▲
            │ (Referenced in main.tf)
            │ git::https://...//modules/azure_kubernetes_services
            │
            ├─────────────────────────────────────────────┐
            │                                             │
            │                                             ▼

┌────────────────────────────────────────┐
│  REPO 2: eip-infra-azure-terraform-    │  ← CONFIGURATION DATA
│          support                       │
├────────────────────────────────────────┤
│                                        │
│  azure-pipelines.yml                   │
│  AKS-Cluster-Upgrade-Terraform.yml     │
│                                        │
│  src/                                  │
│  ├── eiap/                             │
│  │   ├── nonprod/                      │
│  │   │   ├── common-tf-config/         │
│  │   │   │   ├── azure-kubernetes-    │
│  │   │   │   │   services/main.tf      │
│  │   │   │   └── ... (other modules)   │
│  │   │   └── resources/                │
│  │   │       ├── eus/                  │
│  │   │       │   ├── azure-kubernetes-│
│  │   │       │   │   services/         │
│  │   │       │   │   ├── cluster-01/   │
│  │   │       │   │   │  ├── defaults-* │
│  │   │       │   │   │  ├── mandatory-*│
│  │   │       │   │   │  └── nodepools-*│
│  │   │       │   └── ... (other regions)
│  │   ├── preprod/                      │
│  │   └── prod/                         │
│  ├── aisp/                             │
│  ├── pfna/                             │
│  └── ... (other functional areas)      │
│                                        │
│  These are ENVIRONMENT CONFIGS         │
│  Specific values for each cluster      │
│                                        │
│  Git Commits:                          │
│  - New cluster configurations          │
│  - Version updates                     │
│  - Scaling changes                     │
└────────────────────────────────────────┘
            ▲
            │ (Defines tfvars files)
            │ Loaded during terraform plan/apply
            │
            └─────────────────────────────────────────────┐
                                                          │
                                                          ▼

┌────────────────────────────────────────┐
│  REPO 3: eip-infra-k8s-argocd-support  │  ← APPLICATION CONFIGS
├────────────────────────────────────────┤
│                                        │
│  (After cluster is created by Terraform)
│  ArgoCD watches this repo              │
│  and deploys applications              │
│                                        │
│  eiap/                                 │
│  ├── dev/                              │
│  │   ├── applications/                 │
│  │   ├── ingress/                      │
│  │   ├── monitoring/                   │
│  │   └── service-mesh/                 │
│  ├── prod/                             │
│  └── qa/                               │
│                                        │
│  These are K8s RESOURCES               │
│  Helm charts, Deployments, ConfigMaps  │
│                                        │
└────────────────────────────────────────┘

RELATIONSHIP:
  Terraform (Repos 1+2) → Creates Cluster
                      ↓
                  Cluster Running
                      ↓
                 ArgoCD (Repo 3) → Deploys Apps
```

---

## 📋 Terraform State File Explanation

```
┌─────────────────────────────────────────┐
│   terraform.tfstate (JSON File)         │
│   Stored in: Azure Storage Blob         │
│   Path: eiap-storage-container/         │
│          terraform.tfstate              │
└─────────────────────────────────────────┘

Content:
{
  "version": 4,
  "terraform_version": "1.5.0",
  "serial": 42,
  "lineage": "abc-123-def",
  "outputs": {
    "cluster_name": {
      "value": ["pep-eiap-nonprod-eus-app-01-aks"],
      "type": ["string"]
    },
    "cluster_id": {
      "value": ["/subscriptions/xxx/resourceGroups/rg/..."],
      "type": ["string"]
    }
  },
  "resources": [
    {
      "mode": "managed",
      "type": "azurerm_kubernetes_cluster",
      "name": "aks_cluster",
      "instances": [
        {
          "schema_version": 4,
          "attributes": {
            "id": "/subscriptions/xxx/resourceGroups/rg/providers/Microsoft.ContainerService/managedClusters/pep-eiap-nonprod-eus-app-01-aks",
            "name": "pep-eiap-nonprod-eus-app-01-aks",
            "location": "eastus",
            "kubernetes_version": "1.34.7",
            "sku_tier": "Standard",
            "tags": {
              "environment": "nonprod",
              "application": "app-01",
              "costCenter": "H-123456"
            },
            "node_pool": [...],
            "network_profile": {...},
            "identity": {...}
          }
        }
      ]
    }
  ]
}

KEY POINTS:
• "serial": Increments each apply (tracks changes)
• "lineage": Unique ID for this state line
• "resources": List of ALL created/managed resources
• Each resource has full attributes and current values
• Sensitive data (passwords) are encrypted at rest
```

---

## 🎯 Node Pool Configuration Mapping

```
┌────────────────────────────────────────────────────────────────┐
│          NODE POOL CONFIGURATION & USE CASES                   │
└────────────────────────────────────────────────────────────────┘

SYSTEM NODE POOL (Default)
┌─────────────────────────┐
│ name: nps01z1           │  ← Auto-created with cluster
│ vm_size: E4ds_v4        │  ← Medium VMs (system only)
│ node_count: 1           │
│ enable_auto_scaling: ✓  │
│ min_count: 1            │
│ max_count: 3            │
│ mode: System            │  ← Only system pods (cordon)
│ zones: [1]              │  ← Single zone
│ taints:                 │
│   CriticalAddonsOnly=   │  ← Repels user pods
│   true:NoSchedule       │
│                         │
│ PURPOSE: Run kube-system │
│ components:             │
│ • CoreDNS               │
│ • kube-proxy            │
│ • CNI (Calico)          │
│ • metrics-server        │
└─────────────────────────┘

ADDITIONAL SYSTEM POOLS (Multi-Zone HA)
┌─────────────────────────┐
│ nps01z2, nps01z3        │  ← Spread across zones
│ Same config as nps01z1  │  ← Zone 2, Zone 3
│ zones: [2], zones: [3]  │  ← HA for system pods
└─────────────────────────┘

USER/APP NODE POOL
┌─────────────────────────┐
│ name: appnp             │  ← Application workloads
│ vm_size: E8ds_v4        │  ← Larger VMs
│ node_count: 3           │  ← Start with 3
│ enable_auto_scaling: ✓  │
│ min_count: 3            │  ← Always 3 running
│ max_count: 10           │  ← Auto-scale to 10
│ mode: User              │  ← Application pods only
│ zones: [1, 2, 3]        │  ← Multi-zone HA
│ node_labels:            │
│   workload-type=app     │
│ node_taints: []         │  ← No taints (accepts pods)
│                         │
│ PURPOSE: Run user apps  │
│ • Microservices         │
│ • Web services          │
│ • Batch jobs            │
└─────────────────────────┘

BUILD AGENT POOL
┌─────────────────────────┐
│ name: npbp01            │  ← CI/CD build agents
│ vm_size: E8ds_v4        │  ← Large for fast builds
│ node_count: 5           │
│ enable_auto_scaling: ✓  │
│ min_count: 3            │
│ max_count: 10           │
│ mode: User              │
│ zones: [1, 2, 3]        │
│ node_labels:            │
│   balance-group=Build   │
│ node_taints:            │
│   BuildAgentPool=       │  ← Repels regular pods
│   Exists:NoSchedule     │
│                         │
│ PURPOSE: Run CI/CD      │
│ • Azure DevOps agents   │
│ • GitHub Actions        │
│ • Jenkins builders      │
└─────────────────────────┘

SCALING EXAMPLE
┌─────────────────────────────────────────┐
│  NORMAL OPERATION (Load = 50%)          │
│                                         │
│  appnp auto-scaled to: 3 nodes          │
│  Cost: Minimal                          │
│  Resources: 3×E8ds = $xxx/month         │
└─────────────────────────────────────────┘
         │ (Load increases to 80%)
         ▼
┌─────────────────────────────────────────┐
│  HIGH LOAD (Pending pods detected)      │
│                                         │
│  Kubernetes asks: "Need more nodes?"    │
│  Cluster Autoscaler: "Yes, adding one"  │
│  AWS/Azure: Creates new VM              │
│  Total: 4 nodes                         │
└─────────────────────────────────────────┘
         │ (Load increases to 90%)
         ▼
┌─────────────────────────────────────────┐
│  VERY HIGH LOAD                         │
│                                         │
│  Autoscaler: "Still have pending pods"  │
│  Adds node → 5 nodes                    │
│  Load balances across 5 VMs             │
│  All pods scheduled                     │
└─────────────────────────────────────────┘
         │ (Load drops to 20%)
         ▼
┌─────────────────────────────────────────┐
│  SCALE DOWN (30min delay)               │
│                                         │
│  Autoscaler detects unused nodes        │
│  Waits 30 minutes (scale_down_unneeded) │
│  If still unused: Delete node           │
│  Final: 3 nodes again                   │
│  Saves money                            │
└─────────────────────────────────────────┘
```

---

## 🔐 Service Principal & Authentication Flow

```
┌─────────────────────────────────────────────────┐
│  SERVICE PRINCIPAL (Automation Account)         │
│  Used by Terraform to authenticate with Azure  │
└─────────────────────────────────────────────────┘

Creation:
┌──────────────────────────────────────────────┐
│ Azure AD → App Registrations                 │
│ → Create new app                             │
│ → Name: pep-eiap-nonprod-k8s-sp             │
│ → Generate credentials:                      │
│   • Client ID (username)                     │
│   • Client Secret (password)                 │
│   • Tenant ID (domain)                       │
└──────────────────────────────────────────────┘

Storage:
┌──────────────────────────────────────────────┐
│ Azure DevOps → Variable Groups              │
│ → Group: preprod_nonprod_ansible_azure_secrets│
│   clientid: xxxx-xxxx-xxxx-xxxx             │
│   clientsecret: (encrypted)                  │
│   tenantid: xxxx-xxxx-xxxx-xxxx             │
│                                              │
│ Only pipeline can access (not in Git!)       │
│ Secrets encrypted in Azure DevOps           │
└──────────────────────────────────────────────┘

Usage in Terraform:
```hcl
variable "clientid" {
  type      = string
  sensitive = true    # Don't print in logs
}

variable "clientsecret" {
  type      = string
  sensitive = true    # Don't print in logs
}

provider "azurerm" {
  client_id       = var.clientid        # From pipeline variable
  client_secret   = var.clientsecret    # From pipeline variable
  tenant_id       = var.tenantid        # From pipeline variable
  subscription_id = var.subscription    # From pipeline variable
}
```

Pipeline Integration:
```yaml
variables:
  - group: preprod_nonprod_ansible_azure_secrets  # Contains secrets
  
steps:
  - task: TerraformTaskV4
    inputs:
      provider: 'azurerm'
      command: 'init'
  
  - task: TerraformTaskV4
    env:
      TF_VAR_clientid: $(clientid)         # Auto-injected
      TF_VAR_clientsecret: $(clientsecret) # Auto-injected
      TF_VAR_tenantid: $(tenantid)         # Auto-injected
    inputs:
      provider: 'azurerm'
      command: 'apply'
```

Permissions (RBAC):
┌──────────────────────────────────────────────┐
│ Service Principal needs role(s):            │
│ • Contributor (full permissions)            │
│   - Create/Update/Delete resources          │
│ • Network Contributor                       │
│   - Manage VNets, Subnets                   │
│ • Managed Identity Operator                 │
│   - Create managed identities               │
│ • Kubernetes Service Admin                  │
│   - Create AKS clusters                     │
│                                              │
│ Scope: Subscription or Resource Group       │
│ Example: "pep-eiap-nonprod-k8s-sp"         │
│ Role: "Contributor"                         │
│ Scope: /subscriptions/sub-id               │
└──────────────────────────────────────────────┘
```

---

## 📈 Upgrade Process Flowchart

```
KUBERNETES CLUSTER UPGRADE (1.33.5 → 1.34.7)
┌─────────────────────────────────────────────────────────┐
│                PLANNING PHASE                           │
│  1. Review release notes (breaking changes?)            │
│  2. Test in dev/nonprod first                           │
│  3. Schedule maintenance window (low traffic)           │
│  4. Update orchestrator_version in tfvars               │
│  5. Commit to Git with clear message                    │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│           CONTROL PLANE UPGRADE (5-10 min)             │
│  1. Terraform detects version change                    │
│  2. AKS starts control plane upgrade                    │
│     • API Server: 1.33.5 → 1.34.7                      │
│     • etcd database updated                            │
│     • Scheduler, Controller Manager upgraded           │
│  3. Cluster REMAINS ACCESSIBLE (API available)         │
│  4. Control plane comes back online                    │
│  5. Verify: kubectl version                            │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│       SYSTEM NODE POOL UPGRADE (15-20 min)             │
│  For each system node (nps01z1, nps01z2, nps01z3):    │
│                                                         │
│  1. Cordon node: "No new pods here"                    │
│     └─ Existing pods keep running                      │
│                                                         │
│  2. Drain node: "Move existing pods to other nodes"    │
│     └─ Each pod gets terminated & rescheduled          │
│     └─ System pods move to other system nodes          │
│                                                         │
│  3. Upgrade node OS & kubelet to 1.34.7               │
│     └─ Node reboots                                    │
│     └─ Kubelet starts with new version                 │
│                                                         │
│  4. Uncordon node: "Ready for new pods"               │
│     └─ Node rejoins cluster                            │
│     └─ Reports status as Ready                         │
│                                                         │
│  Repeat for next system node                           │
│  max_surge=1 means one at a time                       │
│  Guarantees at least one system pod available          │
│  for critical cluster functions                        │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│        USER NODE POOL UPGRADE (30-40 min)              │
│  For each app node (if 5 app nodes, do 5x):           │
│                                                         │
│  1. Cordon node                                        │
│  2. Drain node → Pods move to other app nodes         │
│  3. Upgrade node                                       │
│  4. Uncordon node                                      │
│                                                         │
│  max_surge=1 means:                                    │
│  • One node upgrading at a time                        │
│  • Always 4 app nodes running                          │
│  • Applications stay available                         │
│  • No service disruption                               │
│                                                         │
│  Alternative: max_surge=2                             │
│  • Two nodes upgrade in parallel                       │
│  • Faster (20-30 min)                                  │
│  • Riskier (only 3 app nodes up)                       │
│  • Choose based on app requirements                    │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│          POST-UPGRADE VALIDATION                        │
│  1. Verify all nodes Ready status                      │
│  2. Check Kubernetes version                           │
│  3. Run pod health checks                              │
│  4. Monitor resource usage                             │
│  5. Verify auto-scaling still works                    │
│  6. Run smoke tests (app deployment)                   │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│              UPGRADE COMPLETE ✓                         │
│  Cluster running 1.34.7                                │
│  Ready for production traffic                          │
└─────────────────────────────────────────────────────────┘

TROUBLESHOOTING DURING UPGRADE

Issue: Node stuck in "Draining" state
  Cause: Pod won't evict (has local storage, no PVC)
  Fix:
    - Force delete problematic pod
    - Manually migrate data
    - Retry drain

Issue: Control plane upgrade fails
  Cause: Resource quota exceeded or cluster unhealthy
  Fix:
    - Check Azure health dashboard
    - Increase resource limits
    - Retry upgrade

Issue: Application pods won't reschedule
  Cause: Insufficient resources or node affinity
  Fix:
    - Scale up app nodes (add more VMs)
    - Review pod resource requests
    - Adjust node selectors
```

---

## 🧮 Parameter Quick Reference Table

```
┌─────────────────────────────────────────────────────────────────┐
│  CRITICAL TFVARS PARAMETERS & WHAT THEY DO                     │
└─────────────────────────────────────────────────────────────────┘

CLUSTER PARAMETERS
┌──────────────────────┬──────────────────────┬─────────────────┐
│ Parameter            │ Example Value        │ Impact          │
├──────────────────────┼──────────────────────┼─────────────────┤
│ cluster_location     │ "eastus"             │ Where cluster   │
│                      │                      │ is hosted       │
├──────────────────────┼──────────────────────┼─────────────────┤
│ kubernetes_version   │ "1.34.7"             │ K8s version,    │
│                      │                      │ API features    │
├──────────────────────┼──────────────────────┼─────────────────┤
│ sku_tier             │ "Standard"           │ High availability│
│                      │ or "Free"            │ Free = no SLA   │
├──────────────────────┼──────────────────────┼─────────────────┤
│ ad_private_cluster   │ true / false         │ No public IP    │
│ _enabled             │                      │ Private DNS     │
├──────────────────────┼──────────────────────┼─────────────────┤
│ np_network_policy    │ "calico"             │ Network security│
│                      │ or "azure"           │ pod-to-pod      │
├──────────────────────┼──────────────────────┼─────────────────┤
│ workload_identity    │ true                 │ Azure workload  │
│ _enabled             │                      │ identity for    │
│                      │                      │ pods (no keys)  │
└──────────────────────┴──────────────────────┴─────────────────┘

NODE POOL PARAMETERS
┌──────────────────────┬──────────────────────┬─────────────────┐
│ Parameter            │ Example Value        │ Impact          │
├──────────────────────┼──────────────────────┼─────────────────┤
│ node_count           │ 3                    │ Initial nodes   │
│                      │                      │ created         │
├──────────────────────┼──────────────────────┼─────────────────┤
│ enable_auto_scaling  │ true                 │ Auto-add/remove │
│                      │                      │ nodes based on  │
│                      │                      │ demand          │
├──────────────────────┼──────────────────────┼─────────────────┤
│ min_count            │ 3                    │ Always keep     │
│                      │                      │ at least 3 nodes│
├──────────────────────┼──────────────────────┼─────────────────┤
│ max_count            │ 10                   │ Don't exceed    │
│                      │                      │ 10 nodes        │
├──────────────────────┼──────────────────────┼─────────────────┤
│ vm_size              │ "Standard_E8ds_v4"   │ CPU, RAM, disk  │
│                      │                      │ per node        │
├──────────────────────┼──────────────────────┼─────────────────┤
│ zones                │ [1, 2, 3]            │ Spread across 3 │
│                      │                      │ availability    │
│                      │                      │ zones for HA    │
├──────────────────────┼──────────────────────┼─────────────────┤
│ os_type              │ "Linux"              │ Linux or Windows│
│                      │ or "Windows"         │ VMs             │
├──────────────────────┼──────────────────────┼─────────────────┤
│ os_sku               │ "Ubuntu"             │ Ubuntu LTS or   │
│                      │ "Windows2022"        │ Windows Server  │
├──────────────────────┼──────────────────────┼─────────────────┤
│ os_disk_type         │ "Ephemeral"          │ SSD (fast) or   │
│                      │ or "Managed"         │ persistent disk │
├──────────────────────┼──────────────────────┼─────────────────┤
│ os_disk_size_gb      │ 150                  │ Disk space for  │
│                      │                      │ OS and apps     │
├──────────────────────┼──────────────────────┼─────────────────┤
│ mode                 │ "System"             │ System pods or  │
│                      │ or "User"            │ user apps       │
├──────────────────────┼──────────────────────┼─────────────────┤
│ max_surge            │ ["1"]                │ How many nodes  │
│                      │                      │ upgrade at once │
├──────────────────────┼──────────────────────┼─────────────────┤
│ node_labels          │ {"workload-type":    │ Pod scheduling  │
│                      │  "application"}      │ selector        │
├──────────────────────┼──────────────────────┼─────────────────┤
│ node_taints          │ ["pool=special:      │ Repel pods      │
│                      │  NoSchedule"]        │ unless tolerated│
└──────────────────────┴──────────────────────┴─────────────────┘

AUTO-SCALER PARAMETERS
┌──────────────────────┬──────────────────────┬─────────────────┐
│ Parameter            │ Example Value        │ Impact          │
├──────────────────────┼──────────────────────┼─────────────────┤
│ scale_down_unneeded  │ "30m"                │ Wait 30 min     │
│                      │                      │ before deleting │
│                      │                      │ idle nodes      │
├──────────────────────┼──────────────────────┼─────────────────┤
│ scale_down_delay_    │ "5m"                 │ Wait 5 min after│
│ after_add            │                      │ node added      │
├──────────────────────┼──────────────────────┼─────────────────┤
│ scan_interval        │ "10s"                │ Check every 10s │
│                      │                      │ if need to scale│
├──────────────────────┼──────────────────────┼─────────────────┤
│ max_unready_nodes    │ 3                    │ Allow 3 nodes   │
│                      │                      │ in NotReady     │
│                      │                      │ state           │
├──────────────────────┼──────────────────────┼─────────────────┤
│ expander             │ "most-pods"          │ Choose node size│
│                      │ or "priority"        │ that fits most  │
│                      │                      │ pending pods    │
└──────────────────────┴──────────────────────┴─────────────────┘
```

---

## 🎓 Interview Question Responses

```
Q1: "Explain your Terraform architecture"
A1: "We have three repos:
     1. eip-infra-terraform-modules = reusable recipes
     2. eip-infra-azure-terraform-support = environment values
     3. Azure DevOps pipeline = automation trigger
     
     Pipeline loads values → calls module → creates infrastructure.
     All changes tracked in Git, all state in Azure Storage."

Q2: "How do you handle state file consistency?"
A2: "State file is the source of truth, stored in Azure Storage.
     We use file locking (terraform state lock) so only one
     pipeline can run at a time. If lock is stuck, we can force
     unlock. State is versioned and encrypted at rest."

Q3: "Walk me through cluster upgrade"
A3: "Three phases:
     1. Control plane (API server) - cluster stays up
     2. System pools - one node at a time, others running
     3. User pools - rolling upgrade with max_surge=1
     
     Each node: cordon (no new pods) → drain (move existing pods)
     → upgrade → uncordon (rejoin cluster).
     Result: Zero downtime, apps keep running."

Q4: "How do you prevent configuration drift?"
A4: "Terraform is idempotent: state file stores what SHOULD exist.
     Before apply, we run plan to compare:
     Desired (tfvars) vs Current (state) vs Actual (Azure).
     If manual changes happen in Azure, next plan will show
     and try to fix it (or we import/reject the change)."

Q5: "What's the difference between max_count and max_surge?"
A5: "max_count = auto-scaling limit (cluster can grow to 10 nodes)
     max_surge = upgrade strategy (upgrade 1 node at a time)
     
     During upgrade with max_surge=1 and 5 app nodes:
     - Start: 5 nodes
     - Node 1 upgrading: 4 running + 1 upgrading
     - Upgrade complete: back to 5
     Ensures always some capacity."

Q6: "How do you add new software to all clusters?"
A6: "If infrastructure (Terraform): Add Helm module, tfvars,
     run pipeline, done.
     
     If applications (post-cluster): Use ArgoCD GitOps model.
     Commit Helm chart config to Git → ArgoCD watches
     → auto-deploys to all clusters using that config.
     
     Single Git commit = software on 100 clusters."

Q7: "What happens if terraform apply fails midway?"
A7: "Terraform is atomic for small resources, but can partially succeed.
     State file captures what was created before failure.
     Next apply continues from where it left off (idempotent).
     We review the state and error, fix config, retry apply.
     Worst case: destroy/rebuild (recovery path in docs)."

Q8: "How do you scale from 3 to 10 nodes?"
A8: "Three options:
     1. Manual: Change node_count=3 to node_count=10 in tfvars,
        run terraform apply, done.
     2. Auto-scaling: enable_auto_scaling=true,
        min_count=3, max_count=10. K8s auto-scales when pods
        can't be scheduled.
     3. Azure portal: Scale directly (not recommended - drift from IaC)."

Q9: "What's the role of the Service Principal?"
A9: "Credentials for automation. Terraform authenticates as
     the SPN (not a human) to create/update Azure resources.
     Stored securely in Azure DevOps variable groups, never
     in Git. SPN has RBAC permissions limited to what it needs
     (principle of least privilege)."

Q10: "How do you handle secrets in Terraform?"
A10: "We mark variables as sensitive=true so they don't print in logs.
      Stored in Azure DevOps variable groups (encrypted).
      Passed as environment variables to pipeline.
      Never hardcoded in Git or state files.
      For app secrets: Use Azure Key Vault provider in Terraform
      to read/inject secrets into pods."
```

---

## 🔧 Common Terraform File Structures

```
COMPLETE DIRECTORY STRUCTURE FOR ONE CLUSTER
eip-infra-azure-terraform-support/
└── src/
    └── eiap/
        └── nonprod/
            ├── common-tf-config/               ← Shared configs
            │   ├── azure-kubernetes-services/
            │   │   ├── main.tf                 ← Calls AKS module
            │   │   ├── variables.tf            ← Variable definitions
            │   │   ├── outputs.tf              ← Return values
            │   │   └── versions.tf             ← Versions & providers
            │   ├── managed-identity/
            │   │   ├── main.tf
            │   │   ├── variables.tf
            │   │   └── outputs.tf
            │   └── ... other resources
            │
            └── resources/                      ← Cluster-specific
                └── eus/                        ← Region
                    └── azure-kubernetes-services/
                        └── pep-eiap-nonprod-eus-infra-02-aks/
                            ├── defaults-*.tfvars       ← Defaults
                            ├── mandatory-*.tfvars      ← Required
                            └── nodepools-*.tfvars      ← Node pools

KEY FILES & THEIR PURPOSE

main.tf
--------
module "aks" {
  source = "git::https://...//modules/azure_kubernetes_services"
  
  # Pass all variables to module
  aks_clusters = var.aks_clusters
  node_pools   = var.node_pools
  # ...
}

output "cluster_name" {
  value = module.aks.cluster_name
}

variables.tf
-----------
variable "aks_clusters" {
  type        = map(any)
  description = "AKS cluster configuration"
}

variable "node_pools" {
  type        = map(object({
    name      = string
    vm_size   = string
    # ... more properties
  }))
}

versions.tf
-----------
terraform {
  required_version = ">= 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

outputs.tf
----------
output "cluster_id" {
  value = module.aks.cluster_id
}

output "kube_config" {
  value     = module.aks.kube_config
  sensitive = true
}

defaults-*.tfvars
-----------------
aks_clusters = {
  cluster-name = {
    identity_type = "UserAssigned"
    sku_tier      = "Standard"
    # ... 50+ more properties
  }
}

mandatory-*.tfvars
------------------
cluster_location = "eastus"
cluster_vnet_name = "..."
managed_identity_name = "..."
subscription = "abc-123-def"

nodepools-*.tfvars
------------------
node_pools = {
  pool-1 = { ... }
  pool-2 = { ... }
  pool-3 = { ... }
}
```

---

## 📊 Cost Impact Analysis

```
COST FACTORS IN TERRAFORM CONFIGURATION

VM SIZE IMPACT
┌─────────────────┬────────────────────┬──────────┐
│ VM Size         │ Cost/Hour (EUS)    │ Use Case │
├─────────────────┼────────────────────┼──────────┤
│ D4s_v3          │ ~$0.38/hour        │ System   │
│ E4ds_v4         │ ~$0.53/hour        │ System   │
│ E8ds_v4         │ ~$1.05/hour        │ App      │
│ E16ds_v4        │ ~$2.10/hour        │ Workload │
│ E32ds_v4        │ ~$4.20/hour        │ High-end │
└─────────────────┴────────────────────┴──────────┘

MONTHLY COST CALCULATION
For 3 app nodes (E8ds_v4) running 24/7:
  Cost = 3 nodes × $1.05/hour × 730 hours/month = ~$2,300

For 5 app nodes:
  Cost = 5 nodes × $1.05/hour × 730 hours/month = ~$3,800

SCALE IMPACT
min_count=1, max_count=10
┌──────────────┬────────────────────┬──────────────┐
│ Load Level   │ Avg Nodes Running  │ Monthly Cost │
├──────────────┼────────────────────┼──────────────┤
│ Low (20%)    │ 2-3 nodes          │ ~$1,500-2,300│
│ Medium (50%) │ 4-5 nodes          │ ~$2,600-3,800│
│ High (80%)   │ 7-8 nodes          │ ~$4,600-5,400│
└──────────────┴────────────────────┴──────────────┘

OS DISK IMPACT
- Ephemeral disk (fast SSD): Included in VM cost
- Managed disk (persistent): +$10-30/month
- Larger disk (200GB vs 100GB): +$5/month

NETWORK IMPACT
- Private cluster (private DNS): No extra cost
- Public cluster: Load Balancer = ~$20/month per cluster
- Egress data transfer: $0.02-0.12/GB

OPTIMIZATION TIPS
✓ Use auto-scaling (min=1, max=10) not static nodes
✓ Use Ephemeral OS disks (cheaper, faster)
✓ Use smaller system pools, larger app pools
✓ Use E-series VMs for IO-heavy apps
✓ Use B-series for unpredictable load (burstable)
✗ Don't use D-series for production (older)
✗ Don't keep dev/test clusters running 24/7
```

This quick reference guide should be printed/bookmarked for interviews!
