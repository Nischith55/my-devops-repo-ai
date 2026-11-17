# Terraform Practical Examples & Interview Scenarios
## Ready-to-Use Code Snippets & Real Scenarios

---

## Table of Contents
1. [Complete Example: Build a New Cluster](#complete-example)
2. [Scenario 1: Scale Up Nodes](#scenario-1)
3. [Scenario 2: Upgrade Kubernetes Version](#scenario-2)
4. [Scenario 3: Add a New Node Pool](#scenario-3)
5. [Scenario 4: Enable New Features](#scenario-4)
6. [Common Issues & Solutions](#common-issues)
7. [Checklists](#checklists)

---

## Complete Example: Build a New Cluster {#complete-example}

### **Scenario: Build `pep-eiap-nonprod-eus-ml-01-aks` for ML Team**

#### **Step 1: Create Directory Structure**

```bash
# PowerShell
$cluster_path = "eip-infra-azure-terraform-support\src\eiap\nonprod\resources\eus\azure-kubernetes-services\pep-eiap-nonprod-eus-ml-01-aks"
mkdir $cluster_path -Force
```

#### **Step 2: Create defaults-pep-eiap-nonprod-eus-ml-01-aks.tfvars**

```hcl
# Cluster definition
aks_clusters = {
  pep-eiap-nonprod-eus-ml-01-aks = {
    # Identity and SKU
    identity_type = "UserAssigned"
    sku_tier      = "Standard"

    # Azure Active Directory RBAC
    ad_rbac_managed                        = true
    ad_azure_rbac_enabled                  = false
    ad_private_cluster_enabled             = true
    ad_private_cluster_public_fqdn_enabled = true

    # Auto-scaler settings
    as_balance_similar_node_groups      = true
    as_expander                         = "most-pods"
    as_empty_bulk_delete_max            = "10"
    as_max_graceful_termination_sec     = "60"
    as_max_unready_percentage           = "55"
    as_new_pod_scale_up_delay           = "10s"
    as_max_unready_nodes                = "3"
    as_scale_down_delay_after_add       = "5m"
    as_scale_down_delay_after_delete    = "10s"
    as_scale_down_delay_after_failure   = "3m"
    as_scale_down_unneeded              = "30m"
    as_scale_down_unready               = "20m"
    as_scale_down_utilization_threshold = "0.3"
    as_scan_interval                    = "10s"
    as_skip_nodes_with_local_storage    = false
    as_skip_nodes_with_system_pods      = true

    # Linux profile (SSH access)
    linux_profile_enabled = ["true"]

    # Windows profile (empty for Linux-only cluster)
    windows_profile_enabled = []
    wp_license              = ""

    # Network profile
    np_dns_service_ip     = "10.27.0.10"
    np_docker_bridge_cidr = "172.17.0.1/16"
    np_network_plugin     = "kubenet"
    np_load_balancer_sku  = "standard"
    np_network_policy     = "calico"
    np_outbound_type      = "userDefinedRouting"
    np_pod_cidr           = "10.227.0.0/16"
    np_service_cidr       = "10.27.0.0/16"

    # Default node pool
    node_count                   = 1
    enable_auto_scaling          = true
    enable_node_public_ip        = false
    pod_max_pid                  = ["4194304"]
    kubelet_disk_type            = "OS"
    max_count                    = 3
    min_count                    = 1
    name                         = "nps01z1"
    node_labels = {
      balance-group = "System01ZonedPools"
    }
    only_critical_addons_enabled = true
    orchestrator_version         = "1.34.7"
    os_disk_size_gb              = 105
    os_disk_type                 = "Ephemeral"
    os_sku                       = "Ubuntu"
    proximity_placement_group_id = null
    node_pool_type               = "VirtualMachineScaleSets"
    max_surge                    = []
    node_vm_size                 = "Standard_E4ds_v4"
    node_zones                   = [1]
    temporary_name_for_rotation  = "dfn"

    # Storage profile
    storage_profile_enabled = ["true"]
    blobCsiDriver           = true
    diskCsiDriver           = true
    fileCsiDriver           = true
    snapshotController      = true

    # Add-ons and features
    workload_autoscaler_profile        = ["true"]
    key_vault_secrets_provider_enabled = ["true"]
    secret_rotation_enabled            = true
    secret_rotation_interval           = "10m"
    oidc_issuer_enabled                = true
    oms_agent_enabled                  = []
    log_analytics_workspace_id         = ""
    disk_encryption_set_id             = null
    workload_identity_enabled          = true
  }
}
```

#### **Step 3: Create mandatory-pep-eiap-nonprod-eus-ml-01-aks.tfvars**

```hcl
# Infrastructure connectivity
cluster_location                      = "eastus"
cluster_vnet_snet_resource_group_name = "pep-eiap-nonprod-eus-network-01-rg"
cluster_vnet_name                     = "pep-eiap-nonprod-eus-network-01-vnet"
cluster_snet_name                     = "pep-eiap-nonprod-eus-network-01-vnet-ml-01-aks-01-snet"
cluster_resource_group_name           = "pep-eiap-nonprod-eus-k8s-01-rg"
managed_identity_name                 = "pep-eiap-nonprod-k8s-managed-identity"
managed_identity_resource_group_name  = "pep-eiap-nonprod-eus-k8s-01-rg"
default_node_pool_resource_group      = "pep-eiap-nonprod-eus-k8s-01-rg"
private_dns_zone_id                   = "/subscriptions/abc123/resourceGroups/rg/providers/Microsoft.Network/privateDnsZones/privatelink.eastus.azmk8s.io"
resource_name_to_create               = "pep-eiap-nonprod-eus-ml-01-aks"
kubernetes_version                    = "1.34.7"

# Authentication (from Azure DevOps Variable Group)
subscription                          = "your-subscription-id"
clientid                              = "your-client-id"
clientsecret                          = "your-client-secret"
tenantid                              = "your-tenant-id"

# Admin access
active_directory_admin_group_object_ids = ["00000000-0000-0000-0000-000000000001"]

# Tags
cluster_tags = {
  environment       = "nonprod"
  application       = "ml-01"
  costCenter        = "H-789123"
  department        = "DataScience"
  businessUnit      = "Analytics"
  createdBy         = "Terraform"
  createdDate       = "2024-01-15"
}

default_node_pool_tags = {
  purpose = "system"
}
```

#### **Step 4: Create nodepools-pep-eiap-nonprod-eus-ml-01-aks.tfvars**

```hcl
# Node pools for ML cluster
node_pools = {
  
  # System pool for cluster infrastructure
  system-np = {
    name                  = "systemnp"
    vm_size               = "Standard_D4s_v3"
    node_count            = 1
    enable_auto_scaling   = true
    enable_node_public_ip = false
    pod_max_pid           = ["4194304"]
    kubelet_disk_type     = "OS"
    max_count             = 3
    min_count             = 1
    
    node_labels = {
      workload-type = "system"
      zone-type     = "z1"
    }
    
    node_taints = ["CriticalAddonsOnly=true:NoSchedule"]
    orchestrator_version = "1.34.7"
    os_disk_size_gb      = 100
    os_disk_type         = "Ephemeral"
    os_type              = "Linux"
    os_sku               = "Ubuntu"
    
    tags = {
      purpose = "system-cluster"
    }
    
    max_surge                     = ["1"]
    zones                         = [1]
    mode                          = "System"
    cluster_name                  = "pep-eiap-nonprod-eus-ml-01-aks"
    cluster_resource_group_name   = "pep-eiap-nonprod-eus-k8s-01-rg"
    vnet_name                     = "pep-eiap-nonprod-eus-network-01-vnet"
    snet_name                     = "pep-eiap-nonprod-eus-network-01-vnet-ml-01-aks-01-snet"
    vnet_snet_resource_group_name = "pep-eiap-nonprod-eus-network-01-rg"
    proximity_placement_group_id  = null
  }

  # Training job pool (CPU-intensive)
  training-pool = {
    name                  = "trainingnp"
    vm_size               = "Standard_D16s_v3"  # 16 CPU, 64GB RAM
    node_count            = 2
    enable_auto_scaling   = true
    enable_node_public_ip = false
    pod_max_pid           = ["4194304"]
    kubelet_disk_type     = "Managed"
    max_count             = 10
    min_count             = 2
    
    node_labels = {
      workload-type = "ml-training"
      gpu           = "false"
      cpu-intensive = "true"
    }
    
    node_taints = ["training=true:NoSchedule"]
    orchestrator_version = "1.34.7"
    os_disk_size_gb      = 200
    os_disk_type         = "Managed"
    os_type              = "Linux"
    os_sku               = "Ubuntu"
    
    tags = {
      purpose = "ml-training-jobs"
    }
    
    max_surge                     = ["1"]
    zones                         = [1, 2]
    mode                          = "User"
    cluster_name                  = "pep-eiap-nonprod-eus-ml-01-aks"
    cluster_resource_group_name   = "pep-eiap-nonprod-eus-k8s-01-rg"
    vnet_name                     = "pep-eiap-nonprod-eus-network-01-vnet"
    snet_name                     = "pep-eiap-nonprod-eus-network-01-vnet-ml-01-aks-01-snet"
    vnet_snet_resource_group_name = "pep-eiap-nonprod-eus-network-01-rg"
    proximity_placement_group_id  = null
  }

  # GPU pool for deep learning
  gpu-pool = {
    name                  = "gpunp"
    vm_size               = "Standard_NC24ads_A100_v4"  # GPU node
    node_count            = 1
    enable_auto_scaling   = true
    enable_node_public_ip = false
    pod_max_pid           = ["4194304"]
    kubelet_disk_type     = "Managed"
    max_count             = 5
    min_count             = 0  # Scale down to 0 when not needed (expensive!)
    
    node_labels = {
      workload-type = "ml-gpu"
      gpu           = "true"
      gpu-type      = "A100"
    }
    
    node_taints = ["gpu=required:NoSchedule"]
    orchestrator_version = "1.34.7"
    os_disk_size_gb      = 250
    os_disk_type         = "Managed"
    os_type              = "Linux"
    os_sku               = "Ubuntu"
    gpu_driver           = "nvidia"
    gpu_instance         = "MIG-1g"
    
    tags = {
      purpose = "deep-learning"
      cost    = "high"
    }
    
    max_surge                     = ["1"]
    zones                         = [1]
    mode                          = "User"
    cluster_name                  = "pep-eiap-nonprod-eus-ml-01-aks"
    cluster_resource_group_name   = "pep-eiap-nonprod-eus-k8s-01-rg"
    vnet_name                     = "pep-eiap-nonprod-eus-network-01-vnet"
    snet_name                     = "pep-eiap-nonprod-eus-network-01-vnet-ml-01-aks-01-snet"
    vnet_snet_resource_group_name = "pep-eiap-nonprod-eus-network-01-rg"
    proximity_placement_group_id  = null
  }

  # Inference pool (serving models)
  inference-pool = {
    name                  = "inferencenp"
    vm_size               = "Standard_E16ds_v4"
    node_count            = 3
    enable_auto_scaling   = true
    enable_node_public_ip = false
    pod_max_pid           = ["4194304"]
    kubelet_disk_type     = "Ephemeral"
    max_count             = 8
    min_count             = 3  # Always 3 for HA
    
    node_labels = {
      workload-type = "ml-inference"
      serving       = "true"
    }
    
    node_taints = []  # Accept any pods
    orchestrator_version = "1.34.7"
    os_disk_size_gb      = 150
    os_disk_type         = "Ephemeral"
    os_type              = "Linux"
    os_sku               = "Ubuntu"
    
    tags = {
      purpose = "model-serving"
    }
    
    max_surge                     = ["1"]
    zones                         = [1, 2, 3]
    mode                          = "User"
    cluster_name                  = "pep-eiap-nonprod-eus-ml-01-aks"
    cluster_resource_group_name   = "pep-eiap-nonprod-eus-k8s-01-rg"
    vnet_name                     = "pep-eiap-nonprod-eus-network-01-vnet"
    snet_name                     = "pep-eiap-nonprod-eus-network-01-vnet-ml-01-aks-01-snet"
    vnet_snet_resource_group_name = "pep-eiap-nonprod-eus-network-01-rg"
    proximity_placement_group_id  = null
  }
}
```

#### **Step 5: Create main.tf in common-tf-config**

Location: `eip-infra-azure-terraform-support/src/eiap/nonprod/common-tf-config/azure-kubernetes-services/main.tf`

```hcl
# Main Terraform configuration that calls the AKS module

terraform {
  required_version = ">= 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

# The AKS module from the modules repository
module "aks_cluster" {
  source = "git::https://PepsiCoIT@dev.azure.com/PepsiCoIT/EIP-Infrastructure/_git/eip-infra-terraform-modules//modules/azure_kubernetes_services"
  
  # Required variables
  aks_clusters                            = var.aks_clusters
  node_pools                              = var.node_pools
  cluster_vnet_snet_resource_group_name   = var.cluster_vnet_snet_resource_group_name
  cluster_vnet_name                       = var.cluster_vnet_name
  cluster_snet_name                       = var.cluster_snet_name
  managed_identity_name                   = var.managed_identity_name
  managed_identity_resource_group_name    = var.managed_identity_resource_group_name
  cluster_resource_group_name             = var.cluster_resource_group_name
  resource_name_to_create                 = var.resource_name_to_create
  subscription                            = var.subscription
  clientid                                = var.clientid
  clientsecret                            = var.clientsecret
  tenantid                                = var.tenantid
  cluster_tags                            = var.cluster_tags
  default_node_pool_tags                  = var.default_node_pool_tags
  default_node_pool_resource_group        = var.default_node_pool_resource_group
  active_directory_admin_group_object_ids = var.active_directory_admin_group_object_ids
  private_dns_zone_id                     = var.private_dns_zone_id
  kubernetes_version                      = var.kubernetes_version
  cluster_location                        = var.cluster_location
  lp_admin_username                       = var.lp_admin_username
  lp_ssh_key                              = var.lp_ssh_key
  wp_admin_username                       = var.wp_admin_username
  wp_admin_password                       = var.wp_admin_password
}

# Export cluster information for other modules/systems
output "cluster_name" {
  description = "Name of the created AKS cluster"
  value       = module.aks_cluster.cluster_name
}

output "cluster_id" {
  description = "Azure resource ID of the AKS cluster"
  value       = module.aks_cluster.cluster_id
}

output "kube_config" {
  description = "Kubernetes configuration file"
  value       = module.aks_cluster.kube_config
  sensitive   = true
}

output "cluster_host" {
  description = "Kubernetes API server endpoint"
  value       = module.aks_cluster.cluster_host
  sensitive   = true
}

output "node_pool_names" {
  description = "Names of all created node pools"
  value       = module.aks_cluster.node_pool_name
}
```

#### **Step 6: Execute Pipeline**

1. **Commit to Git**
   ```bash
   git add eip-infra-azure-terraform-support/src/eiap/nonprod/resources/eus/azure-kubernetes-services/pep-eiap-nonprod-eus-ml-01-aks/
   git commit -m "feat: add ML cluster configuration

   - System pool for cluster infrastructure
   - Training pool for CPU-intensive jobs (D16s)
   - GPU pool for deep learning (A100)
   - Inference pool for model serving (E16ds)
   - Auto-scaling configured (GPU pool scales to 0)"
   git push origin main
   ```

2. **Trigger Pipeline**
   - Open Azure DevOps → Pipelines → azure-pipelines.yml
   - Click "Run"
   - Fill parameters:
     - Functional_Area: eiap
     - Environment: nonprod
     - Region: eus
     - ResourceType: azure-kubernetes-services
     - ResourceGroupName: pep-eiap-nonprod-eus-k8s-01-rg
     - ResourceName: pep-eiap-nonprod-eus-ml-01-aks
   - Click "Run pipeline"

3. **Monitor Execution**
   - terraform init: 2 minutes (download modules)
   - terraform plan: 2 minutes (preview changes)
   - terraform apply: 20 minutes (create cluster)
   - Total time: ~25 minutes

4. **Verify Success**
   ```bash
   # Get cluster credentials
   az aks get-credentials `
     --resource-group pep-eiap-nonprod-eus-k8s-01-rg `
     --name pep-eiap-nonprod-eus-ml-01-aks `
     --overwrite-existing

   # Check cluster health
   kubectl get nodes
   # Output:
   # NAME                                STATUS   ROLES   AGE
   # aks-systemnp-123456789-1             Ready    agent   2m
   # aks-trainingnp-123456789-1           Ready    agent   2m
   # aks-trainingnp-123456789-2           Ready    agent   2m
   # aks-gpunp-123456789-1                Ready    agent   1m
   # aks-inferencenp-123456789-1          Ready    agent   1m
   # aks-inferencenp-123456789-2          Ready    agent   1m
   # aks-inferencenp-123456789-3          Ready    agent   1m

   # Check node pool details
   kubectl describe nodes | grep -A 5 "node-role.kubernetes.io/agent"
   ```

---

## Scenario 1: Scale Up Nodes {#scenario-1}

### **Situation: ML Training Jobs Keep Failing - "Not Enough CPU"**

#### **Problem Investigation**

```bash
# Check current pods and resource requests
kubectl top nodes
kubectl top pods -A

# Check what's pending
kubectl get pods -A --sort-by=.status.conditions[?(@.type=="PodScheduled")].lastTransitionTime | grep -i pending
```

#### **Decision: Increase Training Pool from 2 to 5 Nodes**

**Edit**: `nodepools-pep-eiap-nonprod-eus-ml-01-aks.tfvars`

```hcl
training-pool = {
  name                  = "trainingnp"
  vm_size               = "Standard_D16s_v3"
  node_count            = 5          # ← CHANGED from 2
  enable_auto_scaling   = true
  min_count             = 2
  max_count             = 10
  # ... rest unchanged
}
```

#### **Deployment Steps**

```bash
# Step 1: Commit change
git add nodepools-pep-eiap-nonprod-eus-ml-01-aks.tfvars
git commit -m "scale: increase training pool from 2 to 5 nodes for ML jobs"
git push origin main

# Step 2: Trigger pipeline (same as above)
# Azure DevOps → Run pipeline with same parameters

# Step 3: Pipeline executes
# - terraform plan → shows "appnp pool will scale from 2 to 5"
# - terraform apply → creates 3 new VMs

# Step 4: Monitor scaling
kubectl get nodes -w  # Watch nodes being added
kubectl watch pods -A  # Watch pending pods scheduling

# Step 5: Verify all pods running
kubectl get pods -A | grep -i pending
# Should show 0 pending pods
```

#### **Automatic Alternative: Let Auto-Scaling Handle It**

If you enable auto-scaling (already enabled in our config), you don't need manual intervention:

```hcl
training-pool = {
  node_count            = 2          # Start with 2
  enable_auto_scaling   = true
  min_count             = 2
  max_count             = 10         # Auto-grow up to 10
  # ... rest unchanged
}
```

When pods can't schedule:
1. Kubernetes detects pending pods
2. Cluster Autoscaler adds nodes automatically
3. Pods schedule on new nodes
4. When load drops, scales back down
5. **Result**: Zero manual intervention

---

## Scenario 2: Upgrade Kubernetes Version {#scenario-2}

### **Situation: Kubernetes 1.33.5 → 1.34.7 Upgrade Required**

#### **Pre-Upgrade Checklist**

```bash
# 1. Check current version
kubectl version --short

# 2. Check AKS version compatibility
az aks get-versions --location eastus --output table

# 3. Backup cluster config
kubectl get all --all-namespaces -o yaml > cluster-backup.yaml

# 4. Check for problematic pod configurations
kubectl get pods -A -o json | jq '.items[] | select(.spec.restartPolicy=="Never") | {name: .metadata.name, namespace: .metadata.namespace}'

# 5. Schedule maintenance window (low traffic time)
```

#### **Update Terraform Configuration**

**File**: `defaults-pep-eiap-nonprod-eus-ml-01-aks.tfvars`

```hcl
aks_clusters = {
  pep-eiap-nonprod-eus-ml-01-aks = {
    # ... all other settings ...
    orchestrator_version = "1.34.7"  # ← CHANGED from 1.33.5
    # ... rest unchanged
  }
}

node_pools = {
  system-np = {
    orchestrator_version = "1.34.7"  # ← CHANGED
    # ... rest unchanged
  }
  
  training-pool = {
    orchestrator_version = "1.34.7"  # ← CHANGED
    # ... rest unchanged
  }
  
  gpu-pool = {
    orchestrator_version = "1.34.7"  # ← CHANGED
    # ... rest unchanged
  }
  
  inference-pool = {
    orchestrator_version = "1.34.7"  # ← CHANGED
    # ... rest unchanged
  }
}
```

**File**: `mandatory-pep-eiap-nonprod-eus-ml-01-aks.tfvars`

```hcl
kubernetes_version = "1.34.7"  # ← CHANGED from 1.33.5
```

#### **Use Special Upgrade Pipeline**

**File**: `AKS-Cluster-Upgrade-NonProd-Terraform.yml`

```yaml
# Trigger with these parameters:
- Functional_Area: eiap
- service_principal: NONPROD_K8S_SPN
- env: nonprod
- Region: eus
- ResourceType: azure-kubernetes-services
- ResourceGroupName: pep-eiap-nonprod-eus-k8s-01-rg
- ResourceName: pep-eiap-nonprod-eus-ml-01-aks
- control_plane_upgrade: true
- system_pool_upgrade: true
- user_pool_upgrade: true
- max_surge: 1  # One node at a time for safe upgrade
- parallelism: 1  # Execute serially for safety
```

#### **Monitor Upgrade Execution**

```bash
# Phase 1: Control Plane (5-10 min)
# Watch for "ProvisioningState": "Updating"
az aks show \
  -g pep-eiap-nonprod-eus-k8s-01-rg \
  -n pep-eiap-nonprod-eus-ml-01-aks \
  -o json | jq '.provisioningState'

# Phase 2: Node upgrades
kubectl watch nodes
# Watch each node transition: NotReady (draining) → Ready (upgraded)

# Phase 3: Pod rescheduling
kubectl get pods -A -w | grep -i imagepull
# New pods pull container images on upgraded nodes

# Final check: All nodes should be Ready with new version
kubectl get nodes -o json | jq '.items[] | {name: .metadata.name, version: .status.nodeInfo.kubeletVersion}'
```

#### **Post-Upgrade Validation**

```bash
# 1. Verify version upgrade
kubectl version --short
# Expected: Server Version: v1.34.7

# 2. Check all nodes are Ready
kubectl get nodes
# All should show "Ready" status

# 3. Check all pods are running
kubectl get pods -A
# No "CrashLoopBackOff" or "Pending" pods

# 4. Verify cluster autoscaling works
# Request pod that requires new node
kubectl scale deployment my-app --replicas 100 -n my-namespace
# Should auto-scale cluster

# 5. Rollback if needed (emergency only!)
# Edit tfvars back to 1.33.5 and re-run pipeline
```

---

## Scenario 3: Add a New Node Pool {#scenario-3}

### **Situation: Need GPU Pool for Existing Cluster**

**Note**: Our ML cluster already has GPU pool, so this is an example of adding to an existing cluster.

#### **Edit Tfvars**

Add to `nodepools-pep-eiap-nonprod-eus-ml-01-aks.tfvars`:

```hcl
node_pools = {
  # ... existing pools ...
  
  # NEW: Analytics GPU pool
  analytics-gpu-pool = {
    name                  = "analyticsgpu"
    vm_size               = "Standard_NC12ads_A100_v4"  # Smaller GPU node
    node_count            = 1
    enable_auto_scaling   = true
    enable_node_public_ip = false
    pod_max_pid           = ["4194304"]
    kubelet_disk_type     = "Managed"
    max_count             = 3
    min_count             = 0  # Scale to 0 when not in use
    
    node_labels = {
      workload-type = "analytics-gpu"
      gpu           = "true"
      gpu-type      = "A100"
    }
    
    node_taints = ["analytics-gpu=required:NoSchedule"]
    orchestrator_version = "1.34.7"
    os_disk_size_gb      = 200
    os_disk_type         = "Managed"
    os_type              = "Linux"
    os_sku               = "Ubuntu"
    gpu_driver           = "nvidia"
    gpu_instance         = "MIG-2g"
    
    tags = {
      purpose = "analytics-ml"
      team    = "DataAnalytics"
    }
    
    max_surge                     = ["1"]
    zones                         = [1]
    mode                          = "User"
    cluster_name                  = "pep-eiap-nonprod-eus-ml-01-aks"
    cluster_resource_group_name   = "pep-eiap-nonprod-eus-k8s-01-rg"
    vnet_name                     = "pep-eiap-nonprod-eus-network-01-vnet"
    snet_name                     = "pep-eiap-nonprod-eus-network-01-vnet-ml-01-aks-01-snet"
    vnet_snet_resource_group_name = "pep-eiap-nonprod-eus-network-01-rg"
    proximity_placement_group_id  = null
  }
}
```

#### **Deploy**

```bash
# Commit and push
git add nodepools-pep-eiap-nonprod-eus-ml-01-aks.tfvars
git commit -m "feat: add analytics GPU pool to ML cluster"
git push origin main

# Trigger pipeline (same parameters as before)
# Pipeline detects new pool and creates it
# Takes 10-15 minutes

# Verify
kubectl get nodes | grep analyticsgpu
# Shows new node in analytics-gpu pool
```

---

## Scenario 4: Enable New Features {#scenario-4}

### **Situation: Enable OIDC Workload Identity for Applications**

This allows Kubernetes pods to authenticate to Azure without secrets!

#### **Check Current State**

```bash
# Check if OIDC already enabled
az aks show -g pep-eiap-nonprod-eus-k8s-01-rg -n pep-eiap-nonprod-eus-ml-01-aks \
  -o json | jq '.oidcIssuerProfile'

# Expected (if enabled):
# {
#   "enabled": true,
#   "issuerUrl": "https://eastus.oic.prod-aks.azure.com/..."
# }
```

#### **Enable in Terraform**

**File**: `defaults-pep-eiap-nonprod-eus-ml-01-aks.tfvars`

```hcl
aks_clusters = {
  pep-eiap-nonprod-eus-ml-01-aks = {
    # ... existing settings ...
    oidc_issuer_enabled     = true   # Already enabled in our example
    workload_identity_enabled = true  # Already enabled
    # ... rest unchanged
  }
}
```

If not already enabled, Terraform will enable them on next apply.

#### **Use in Application**

Once enabled, pods can authenticate to Azure:

```yaml
# Kubernetes ServiceAccount
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ml-app
  namespace: ml-apps
  annotations:
    azure.workload.identity/client-id: "00000000-0000-0000-0000-000000000002"

---
# Deployment using workload identity
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-app
  namespace: ml-apps
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ml-app
  template:
    metadata:
      labels:
        app: ml-app
        azure.workload.identity/use: "true"  # Enable workload identity
    spec:
      serviceAccountName: ml-app
      containers:
      - name: ml-app
        image: myregistry.azurecr.io/ml-app:latest
        env:
        - name: AZURE_AUTHORITY_HOST
          value: https://login.microsoftonline.com
        - name: AZURE_CLIENT_ID
          value: "00000000-0000-0000-0000-000000000002"
        - name: AZURE_TENANT_ID
          value: "12345678-abcd-1234-efgh-567890ijklmn"
```

**Benefits**:
- ✅ No Azure credentials in environment variables
- ✅ No service principal secrets to manage
- ✅ Automatic token refresh
- ✅ Better security posture

---

## Common Issues & Solutions {#common-issues}

### **Issue 1: Nodes Stuck in "NotReady"**

```bash
# Diagnose
kubectl describe node aks-appnp-123456789-1 | tail -50

# Common causes and solutions:
# 1. CNI plugin issue
kubectl logs -n kube-system -l k8s-app=azure-cni -f

# 2. Node pressure (CPU/memory)
kubectl top nodes
# If usage > 90%, need to scale

# 3. Disk pressure
kubectl describe node <node-name> | grep -i disk

# Solution: Restart kubelet
kubectl drain <node-name> --ignore-daemonsets
az vmss restart -g MC_rg_cluster_region --name aks-pool-xxx --instance-ids 1
kubectl uncordon <node-name>
```

### **Issue 2: "Error acquiring state lock"**

```bash
# Cause: Another pipeline is running or lock is stuck

# Check lock status
terraform state list  # Shows lock error

# Force unlock (use carefully!)
terraform force-unlock LOCK_ID

# Better: Wait for other pipeline to finish
# Check Azure DevOps → Pipelines for running jobs
```

### **Issue 3: "Insufficient quota for SKU"**

```bash
# Cause: Too many VMs of one type in region

# Check quota
az vm list-usage --location eastus -o table | grep Standard_E8ds

# Solutions:
# 1. Use different VM size
# 2. Request quota increase from Azure
# 3. Delete unused clusters

# In tfvars, change VM size:
vm_size = "Standard_D16ds_v4"  # Alternative to E8ds
```

### **Issue 4: Pods Won't Schedule After Upgrade**

```bash
# Diagnose
kubectl describe pod <pod-name> -n <namespace>

# Check node resources
kubectl describe nodes

# Common causes:
# 1. Not enough resources
kubectl top nodes
# Solution: Scale cluster

# 2. Pod affinity/anti-affinity preventing scheduling
kubectl describe pod <pod> | grep -A 5 affinity

# 3. Taints/tolerations mismatch
kubectl get nodes -o json | jq '.items[] | {name: .metadata.name, taints: .spec.taints}'

# Solution: Add toleration to pod
spec:
  tolerations:
  - key: "CriticalAddonsOnly"
    operator: "Equal"
    value: "true"
    effect: "NoSchedule"
```

---

## Checklists {#checklists}

### **New Cluster Deployment Checklist**

```
□ Gather Requirements
  □ Cluster name, environment, region
  □ VM sizes and counts needed
  □ Node pool requirements (GPU, special configs)
  □ Features needed (private cluster, workload identity, etc.)
  □ Network requirements (subnets, DNS zones)

□ Preparation
  □ Create directory for cluster config
  □ Verify subnet exists and has available IPs
  □ Verify managed identity exists
  □ Verify resource group exists
  □ Prepare tags and labeling strategy

□ Terraform Configuration
  □ Create defaults-*.tfvars (cluster settings)
  □ Create mandatory-*.tfvars (infrastructure connectivity)
  □ Create nodepools-*.tfvars (node pool definitions)
  □ Review all values for correctness
  □ Validate Terraform syntax: terraform validate

□ Git & Review
  □ Create feature branch
  □ Commit all tfvars files
  □ Write descriptive commit message
  □ Create Pull Request
  □ Get code review approval
  □ Merge to main branch

□ Deployment
  □ Trigger Azure DevOps pipeline
  □ Review terraform plan output
  □ Verify "additions" are as expected
  □ Approve deployment gate
  □ Wait for terraform apply to complete

□ Post-Deployment
  □ Get kubeconfig: az aks get-credentials ...
  □ Verify cluster health: kubectl get nodes
  □ Verify all node pools created: kubectl get nodes
  □ Verify system pods running: kubectl get pods -n kube-system
  □ Test networking: kubectl run -it debug --image=busybox
  □ Document cluster endpoint and access details

□ Security Hardening
  □ Configure Network Policy (Calico)
  □ Enable Pod Security Policy or Pod Security Standards
  □ Setup RBAC for team access
  □ Enable monitoring/logging
  □ Enable secrets encryption

□ Application Deployment
  □ Deploy ingress controller (NGINX)
  □ Deploy monitoring (Prometheus)
  □ Deploy logging (ELK stack)
  □ Deploy service mesh if needed (Istio)
  □ Deploy applications via Helm/ArgoCD
```

### **Cluster Upgrade Checklist**

```
□ Pre-Upgrade
  □ Review release notes for breaking changes
  □ Test upgrade in lower environment first
  □ Identify maintenance window (low traffic)
  □ Backup cluster configuration: kubectl get all -A -o yaml
  □ Notify team of maintenance
  □ Check node capacity: kubectl top nodes

□ Terraform Changes
  □ Update orchestrator_version in all tfvars files
  □ Update kubernetes_version in mandatory tfvars
  □ Review changes: git diff
  □ Commit: git commit -m "upgrade: kubernetes 1.33.5 → 1.34.7"
  □ Push: git push origin feature-branch

□ Deployment
  □ Trigger upgrade pipeline (separate from main pipeline)
  □ Set control_plane_upgrade: true
  □ Set system_pool_upgrade: true
  □ Set user_pool_upgrade: true
  □ Set max_surge: 1 (safer) or 2 (faster)
  □ Monitor each phase

□ Monitoring During Upgrade
  □ Watch control plane: kubectl cluster-info
  □ Watch node status: kubectl get nodes -w
  □ Monitor pods: kubectl get pods -A -w
  □ Check logs: kubectl logs -n kube-system
  □ Alert on errors: Review pipeline logs

□ Post-Upgrade
  □ Verify kubernetes version: kubectl version --short
  □ Verify all nodes Ready: kubectl get nodes
  □ Verify all pods running: kubectl get pods -A
  □ Run smoke tests (deploy test app)
  □ Check autoscaling works
  □ Review metrics (CPU, memory, disk)
  □ Notify team upgrade complete
  □ Document any issues encountered
```

### **Scaling Checklist**

```
□ Decision Phase
  □ Current usage: kubectl top nodes
  □ Pending pods: kubectl get pods -A | grep Pending
  □ Cost impact: Calculate new cluster cost
  □ Downtime implications: Check pod redundancy

□ Manual Scale
  □ Edit nodepools-*.tfvars
  □ Change node_count value
  □ Commit and push
  □ Run pipeline
  □ Monitor scaling progress: kubectl get nodes -w

□ Auto-Scale Setup
  □ Verify enable_auto_scaling: true
  □ Verify min_count (minimum running)
  □ Verify max_count (maximum allowed)
  □ Commit configuration
  □ Run pipeline
  □ Test with load

□ Verification
  □ Monitor: kubectl top nodes
  □ Check: kubectl get pods -A (no pending)
  □ Verify: kubectl get nodes (all Ready)
  □ Cost check: New cluster size costs acceptable
```

---

## Interview Q&A Reference

```
Q: "Walk me through creating a new cluster"
A: "1. Create three tfvars files with cluster config
    2. Commit to Git
    3. Trigger pipeline with cluster parameters
    4. Pipeline runs: init → plan → (review) → apply
    5. Terraform uses module to create cluster
    6. Verify with kubectl commands
    Takes about 25 minutes total."

Q: "How would you handle an urgent cluster upgrade?"
A: "1. Update orchestrator_version in tfvars
    2. Use dedicated upgrade pipeline
    3. Execute in three phases: control plane → system → user
    4. Each node gets cordoned, drained, upgraded
    5. max_surge=1 ensures always running nodes
    6. Monitor each phase with kubectl commands
    Takes 1-2 hours depending on cluster size."

Q: "Describe your node pool strategy"
A: "1. System pool: Small VMs, tainted (only system pods)
    2. App pool: Medium VMs, untainted (user apps)
    3. Specialized pools: GPU, high-memory, CPU-intensive
    4. Each pool auto-scales independently
    5. Labels and taints control pod placement
    6. Multi-zone spread for high availability"

Q: "How do you prevent configuration drift?"
A: "Terraform state file is source of truth. On every plan:
    - Compare desired (tfvars) vs current (state) vs actual (Azure)
    - Show differences to operator
    - Only apply plan if approved
    - State stays synced with infrastructure
    Manual Azure changes get detected on next plan/apply."
```

This practical guide should give you ready-to-use examples for any interview scenario!

