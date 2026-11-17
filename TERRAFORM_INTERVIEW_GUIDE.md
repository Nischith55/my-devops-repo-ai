# Terraform Infrastructure as Code - Interview Explanation Guide
## Complete Step-by-Step Flow: From Modules to Cluster Building, Updates & Node Management

---

## Table of Contents
1. [What is Terraform and Why Your Organization Uses It](#what-is-terraform)
2. [Your Terraform Architecture Overview](#architecture-overview)
3. [Module Structure and Breakdown](#module-structure)
4. [Step-by-Step: How to Build a New AKS Cluster](#build-new-cluster)
5. [Step-by-Step: How to Add New Nodes/Scale Up](#add-nodes)
6. [Step-by-Step: How to Update/Upgrade a Cluster](#upgrade-cluster)
7. [Step-by-Step: How to Install New Software](#install-software)
8. [Real-World Example Walkthrough](#real-world-example)
9. [Common Terraform Commands](#common-commands)
10. [Troubleshooting Guide](#troubleshooting)

---

## What is Terraform and Why Your Organization Uses It {#what-is-terraform}

### **What is Terraform?**

Terraform is an **Infrastructure as Code (IaC)** tool that allows you to define, provision, and manage cloud infrastructure using configuration files instead of manual clicking in the Azure portal.

**Key Benefits:**
- **Version Control**: Track infrastructure changes in Git (like code)
- **Consistency**: Same infrastructure every time you deploy
- **Repeatability**: Deploy to multiple environments easily (Dev → QA → Prod)
- **Scalability**: Manage 100s of resources from a single command
- **Auditability**: See who changed what and when

### **Why Your Organization Uses Terraform**

Your organization manages multiple Azure Kubernetes Service (AKS) clusters across different environments (nonprod, preprod, prod) and regions (EUS, SCUS, GWC, etc.). Doing this manually would be:
- Error-prone
- Time-consuming
- Difficult to replicate
- Hard to track changes

Terraform allows you to:
1. Define cluster configuration once as a module
2. Reuse that module for multiple clusters
3. Change a single value to roll out changes across 100 clusters
4. Track all changes in Git history

---

## Your Terraform Architecture Overview {#architecture-overview}

```
┌─────────────────────────────────────────────────────────────────┐
│                  TERRAFORM EXECUTION FLOW                       │
└─────────────────────────────────────────────────────────────────┘

    Azure DevOps Pipeline (azure-pipelines.yml)
              ↓
    Select Parameters (Environment, Region, Resource)
              ↓
    Checkout Terraform Modules Repo
              ↓
    Checkout Environment Config Repo
              ↓
    Run: terraform init (backend setup)
              ↓
    Run: terraform plan (preview changes)
              ↓
    Run: terraform apply (create/update resources)
              ↓
    Azure Resources Created (AKS Cluster + Node Pools)
```

### **The Three Main Components**

Your Terraform setup has **three distinct parts**:

#### **1. Terraform Modules Repository** ⚙️
**Location**: `eip-infra-terraform-modules/`

This is the **blueprint library**. It contains reusable modules for creating Azure resources:

```
eip-infra-terraform-modules/
├── modules/
│   ├── azure_kubernetes_services/    ← AKS Module (most important)
│   │   ├── versions.tf               ← Terraform & Provider versions
│   │   ├── variables.tf              ← Input parameters
│   │   ├── aks-nodepools.tf          ← Cluster & Node pool creation logic
│   │   ├── data.tf                   ← Data lookups (find existing resources)
│   │   └── outputs.tf                ← What to return after creation
│   ├── storage_account/
│   ├── key_vault/
│   ├── managed_identity/
│   └── ... other modules
```

**Think of it as**: A **recipe book** - each module is a complete recipe for creating a specific Azure resource.

#### **2. Terraform Support Repository (Environment Config)** 🌍
**Location**: `eip-infra-azure-terraform-support/`

This contains **environment-specific configurations**:

```
eip-infra-azure-terraform-support/
├── azure-pipelines.yml               ← Main pipeline definition
├── AKS-Cluster-Upgrade-Terraform.yml ← Cluster upgrade pipeline
├── src/
│   ├── eiap/
│   │   ├── nonprod/
│   │   │   ├── common-tf-config/     ← Shared configs for nonprod
│   │   │   │   └── azure-kubernetes-services/
│   │   │   │       ├── main.tf       ← Calls the AKS module
│   │   │   │       ├── variables.tf
│   │   │   │       ├── outputs.tf
│   │   │   │       └── versions.tf
│   │   │   └── resources/
│   │   │       ├── eus/              ← East US region
│   │   │       │   └── azure-kubernetes-services/
│   │   │       │       └── pep-eiap-nonprod-eus-infra-02-aks/
│   │   │       │           ├── defaults-*.tfvars    ← Default values
│   │   │       │           ├── mandatory-*.tfvars   ← Required values
│   │   │       │           └── nodepools-*.tfvars   ← Node pool config
│   │   │       └── scus/              ← South Central US region
│   │   ├── preprod/
│   │   └── prod/
│   ├── aisp/
│   ├── pfna/
│   └── ... other functional areas
```

**Think of it as**: The **ingredient list and amounts** for each meal (cluster).

#### **3. Azure DevOps Pipelines** 🚀
**File**: `azure-pipelines.yml`

These are **automated workflows** that:
1. Get triggered manually or by code commit
2. Execute Terraform commands
3. Deploy infrastructure to Azure

**Think of it as**: The **cooking process automation** - it takes recipes + ingredients and makes the dish automatically.

---

## Module Structure and Breakdown {#module-structure}

### **The AKS Module Deep Dive** (Most Important)

Let me explain the AKS module in interview detail:

#### **File 1: `versions.tf`** - Define providers and versions

```hcl
provider "azurerm" {
  alias                      = "provisioning"    # Give this provider an alias
  subscription_id            = var.subscription  # Which Azure subscription
  client_id                  = var.clientid      # Service Principal credentials
  client_secret              = var.clientsecret
  tenant_id                  = var.tenantid
  features {}
}
```

**What's happening:**
- Telling Terraform: "I'm using Azure Resource Manager (azurerm) provider"
- Giving it authentication credentials (Service Principal)
- This provider will create/manage all Azure resources
- The `alias = "provisioning"` lets us use different providers if needed

**Interview Answer**: "This file sets up the connection to Azure. Terraform authenticates using a Service Principal (username/password for the automation account) to ensure only authorized changes happen."

---

#### **File 2: `variables.tf`** - Input parameters

```hcl
# Example variable for node pools
variable "node_pools" {
  type = map(object({
    name                  = string              # Pool name (e.g., "npbp01")
    vm_size              = string              # VM size (e.g., "Standard_E8ds_v4")
    node_count           = number              # How many nodes initially
    enable_auto_scaling  = bool                # Should it auto-scale?
    max_count            = number              # Max nodes when scaling
    min_count            = number              # Min nodes (always running)
    node_labels          = map(string)         # Labels for scheduling pods
    node_taints          = list(string)        # Taints to repel pods
    orchestrator_version = string              # Kubernetes version
    os_disk_size_gb      = number              # Disk space
    os_type              = string              # Linux or Windows
    # ... many more properties
  }))
}

variable "aks_clusters" {
  type = map(any)  # AKS cluster configuration
}

variable "kubernetes_version" {
  type = string    # K8s version (e.g., "1.34.7")
}
```

**What's happening:**
- Defining what inputs the module accepts
- Creating a "contract" - this is what users of the module MUST provide
- `map(object(...))` means multiple node pools can be defined with specific properties

**Interview Answer**: "Variables are like function parameters. We define what must be passed in, what data types, and what they're for. This makes the module reusable - change the variables, get different infrastructure."

---

#### **File 3: `data.tf`** - Look up existing resources

```hcl
data "azurerm_client_config" "current" {
  provider = azurerm.provisioning
}
# Gets current Azure subscription/tenant info

data "azurerm_subnet" "aks_vnet_snet_assoc" {
  provider             = azurerm.provisioning
  name                 = var.cluster_snet_name      # Look for this subnet
  virtual_network_name = var.cluster_vnet_name      # In this virtual network
  resource_group_name  = var.cluster_vnet_snet_resource_group_name
}
# This FINDS an existing subnet (doesn't create it)

data "azurerm_user_assigned_identity" "mi" {
  provider            = azurerm.provisioning
  name                = var.managed_identity_name
  resource_group_name = var.managed_identity_resource_group_name
}
# This FINDS an existing managed identity
```

**What's happening:**
- Querying Azure to find resources that already exist
- These lookups return data we'll use when creating the cluster
- Example: Find the subnet → get its ID → use that ID when creating AKS

**Interview Answer**: "Data sources query existing infrastructure. Before creating an AKS cluster, we need to know: 'Which virtual network should it connect to? Which subnet? Who's the identity?' We query Azure for these."

---

#### **File 4: `aks-nodepools.tf`** - The actual resource creation

This is the **main file** where resources are created:

```hcl
# Create the AKS cluster
resource "azurerm_kubernetes_cluster" "aks_cluster" {
  provider = azurerm.provisioning
  for_each = var.aks_clusters  # Create one cluster per entry
  
  name     = var.resource_name_to_create  # Name of cluster
  location = var.cluster_location         # Where to put it (EUS, SCUS, etc.)
  
  # Identity
  identity {
    type         = each.value["identity_type"]     # UserAssigned
    identity_ids = [data.azurerm_user_assigned_identity.mi.id]
  }
  
  # Access control
  azure_active_directory_role_based_access_control {
    azure_rbac_enabled     = each.value["ad_azure_rbac_enabled"]
    admin_group_object_ids = var.active_directory_admin_group_object_ids
  }
  
  # Network
  private_cluster_enabled = each.value["ad_private_cluster_enabled"]
  private_dns_zone_id     = var.private_dns_zone_id
  
  # Auto-scaling settings
  auto_scaler_profile {
    balance_similar_node_groups = each.value["as_balance_similar_node_groups"]
    # ... 20+ auto-scaling tuning parameters
  }
  
  # Maintenance windows
  maintenance_window_auto_upgrade { ... }
  maintenance_window_node_os { ... }
  
  tags = var.cluster_tags  # Billing & management tags
}

# Create node pools
resource "azurerm_kubernetes_cluster_node_pool" "aks_node_pools" {
  for_each = var.node_pools  # Create one pool per entry
  
  name                  = each.value.name
  kubernetes_cluster_id = azurerm_kubernetes_cluster.aks_cluster[...].id
  vm_size              = each.value.vm_size
  node_count           = each.value.node_count
  
  # Auto-scaling
  enable_auto_scaling = each.value.enable_auto_scaling
  min_count          = each.value.min_count
  max_count          = each.value.max_count
  
  # Labels & taints (for pod scheduling)
  node_labels = each.value.node_labels
  node_taints = each.value.node_taints
  
  # OS configuration
  os_type            = each.value.os_type
  os_disk_size_gb    = each.value.os_disk_size_gb
  os_sku             = each.value.os_sku
  
  tags = each.value.tags
}
```

**What's happening:**
- `for_each` loop: Creates one cluster per entry in the `aks_clusters` map
- Sets all cluster properties (identity, networking, auto-scaling, maintenance)
- Creates multiple node pools, each with different properties
- Node pools are groups of VMs with specific roles (e.g., Build agents, System pods, etc.)

**Interview Answer**: "This is where the actual Azure resources are created. The `for_each` loop means one configuration can create multiple clusters. For example, if you pass two cluster definitions, it creates two clusters, each with their own node pools."

---

#### **File 5: `outputs.tf`** - What information to return

```hcl
output "cluster_name" {
  description = "Name of the created cluster"
  value = [for i in azurerm_kubernetes_cluster.aks_cluster: i.name]
}

output "cluster_id" {
  description = "Azure resource ID of the cluster"
  value = [for i in azurerm_kubernetes_cluster.aks_cluster: i.id]
}

output "kube_config" {
  description = "Kubernetes config file (sensitive)"
  value = [for i in azurerm_kubernetes_cluster.aks_cluster: i.kube_config_raw]
  sensitive = true  # Don't print in logs
}

output "cluster_host" {
  description = "Kubernetes API server endpoint"
  value = [for i in azurerm_kubernetes_cluster.aks_cluster: i.kube_config.0.host]
  sensitive = true
}

output "node_pool_name" {
  description = "Names of all created node pools"
  value = [for i in azurerm_kubernetes_cluster_node_pool.aks_node_pools: i.name]
}
```

**What's happening:**
- After creating resources, we return useful information
- Other Terraform configs or teams can use these outputs
- Marked as `sensitive` so passwords aren't logged

**Interview Answer**: "Outputs are like return values. After we create a cluster, someone might ask 'What's the API endpoint?' or 'Give me the config file.' Outputs provide this information to downstream processes."

---

## Step-by-Step: How to Build a New AKS Cluster {#build-new-cluster}

Let me walk you through building a brand new cluster from scratch.

### **Step 1: Prepare the Configuration Files**

You need to create values for your new cluster. Let's say you want to create a new cluster called `pep-eiap-nonprod-eus-app-01-aks`.

**Create three `.tfvars` files** in the cluster directory:

Location: `eip-infra-azure-terraform-support/src/eiap/nonprod/resources/eus/azure-kubernetes-services/pep-eiap-nonprod-eus-app-01-aks/`

**File 1: `defaults-pep-eiap-nonprod-eus-app-01-aks.tfvars`**

```hcl
aks_clusters = {
  pep-eiap-nonprod-eus-app-01-aks = {
    identity_type = "UserAssigned"                    # Use managed identity
    sku_tier      = "Standard"                        # Or "Free" for dev
    
    # Azure AD RBAC
    ad_azure_rbac_enabled              = false
    ad_private_cluster_enabled         = true         # Private cluster (no public IP)
    ad_private_cluster_public_fqdn_enabled = true
    
    # Auto-scaler settings
    as_balance_similar_node_groups      = true
    as_expander                         = "most-pods"
    as_max_unready_percentage           = "55"
    as_scale_down_unneeded              = "30m"
    # ... (many more auto-scaler settings)
    
    # Default node pool
    node_count            = 1
    enable_auto_scaling   = true
    max_count             = 3
    min_count             = 1
    name                  = "nps01z1"
    orchestrator_version  = "1.34.7"           # Kubernetes version
    os_disk_size_gb       = 105
    os_disk_type          = "Ephemeral"        # Fast SSD
    os_sku                = "Ubuntu"           # Linux OS
    node_vm_size          = "Standard_E4ds_v4" # VM size
    node_zones            = [1]                # Availability zone 1
    
    # Features
    oidc_issuer_enabled      = true            # For workload identity
    workload_identity_enabled = true
    storage_profile_enabled  = ["true"]
    blobCsiDriver            = true            # Allow blob storage mounting
    diskCsiDriver            = true            # Allow managed disk mounting
  }
}
```

**What you're doing:**
- Defining what the cluster looks like
- Kubernetes version (1.34.7)
- VM size and count
- Features (private cluster, workload identity, storage drivers)
- Auto-scaling behavior

**File 2: `mandatory-pep-eiap-nonprod-eus-app-01-aks.tfvars`**

```hcl
# Infrastructure resource names and locations
cluster_location                      = "eastus"
cluster_vnet_snet_resource_group_name = "pep-eiap-nonprod-eus-network-01-rg"
cluster_vnet_name                     = "pep-eiap-nonprod-eus-network-01-vnet"
cluster_snet_name                     = "pep-eiap-nonprod-eus-network-01-vnet-app-01-aks-01-snet"
cluster_resource_group_name           = "pep-eiap-nonprod-eus-k8s-01-rg"
managed_identity_name                 = "pep-eiap-nonprod-k8s-managed-identity"
managed_identity_resource_group_name  = "pep-eiap-nonprod-eus-k8s-01-rg"
default_node_pool_resource_group      = "pep-eiap-nonprod-eus-k8s-01-rg"
private_dns_zone_id                   = "/subscriptions/xxx/resourceGroups/rg/providers/Microsoft.Network/privateDnsZones/zone"
resource_name_to_create               = "pep-eiap-nonprod-eus-app-01-aks"
kubernetes_version                    = "1.34.7"

# Credentials
subscription                          = "a1b2c3d4-e5f6-..."  # Azure Subscription ID
clientid                              = var.client_id       # Service Principal ID
clientsecret                          = var.client_secret   # Service Principal Secret
tenantid                              = "12345678-abcd-..."  # Azure Tenant ID

# Admin access
active_directory_admin_group_object_ids = ["00000000-0000-0000-0000-000000000001"]  # Azure AD Group for admins

# Tagging
cluster_tags = {
  environment  = "nonprod"
  application  = "app-01"
  costCenter   = "H-######"
}
```

**What you're doing:**
- Providing the "where" and "how to authenticate" info
- Resource groups and networking resources must already exist
- Credentials for the Service Principal that will make the changes
- Tags for billing and organization

**File 3: `nodepools-pep-eiap-nonprod-eus-app-01-aks.tfvars`**

```hcl
node_pools = {
  # System node pool for critical add-ons
  system-np = {
    name                  = "systemnp"
    vm_size               = "Standard_D4s_v3"
    node_count            = 1
    enable_auto_scaling   = true
    min_count             = 1
    max_count             = 3
    
    node_labels = {
      workload-type = "system"
    }
    node_taints = ["CriticalAddonsOnly=true:NoSchedule"]  # Only system pods
    
    orchestrator_version = "1.34.7"
    os_disk_size_gb      = 100
    os_type              = "Linux"
    zones                = [1, 2]  # Spread across 2 zones
    
    # Networking
    vnet_name                     = "pep-eiap-nonprod-eus-network-01-vnet"
    snet_name                     = "pep-eiap-nonprod-eus-network-01-vnet-app-01-aks-01-snet"
    vnet_snet_resource_group_name = "pep-eiap-nonprod-eus-network-01-rg"
    
    tags = {
      purpose = "system"
    }
  }
  
  # Application node pool for user applications
  app-np = {
    name                  = "appnp"
    vm_size               = "Standard_E8ds_v4"
    node_count            = 3
    enable_auto_scaling   = true
    min_count             = 3
    max_count             = 10
    
    node_labels = {
      workload-type = "application"
    }
    
    orchestrator_version = "1.34.7"
    os_disk_size_gb      = 150
    os_type              = "Linux"
    zones                = [1, 2, 3]  # Spread across 3 zones for HA
    
    vnet_name                     = "pep-eiap-nonprod-eus-network-01-vnet"
    snet_name                     = "pep-eiap-nonprod-eus-network-01-vnet-app-01-aks-01-snet"
    vnet_snet_resource_group_name = "pep-eiap-nonprod-eus-network-01-rg"
    
    tags = {
      purpose = "applications"
    }
  }
}
```

**What you're doing:**
- Defining two node pools:
  - **System pool**: For Kubernetes system components (tainted to repel user pods)
  - **App pool**: For application workloads (multiple zones for high availability)
- Auto-scaling: Between 3-10 app nodes based on demand
- Taints and labels control where pods can run

---

### **Step 2: Create the Terraform Configuration**

Create `main.tf` in `common-tf-config/azure-kubernetes-services/`:

```hcl
# This calls the reusable AKS module from the modules repository
module "aks_cluster" {
  source = "git::https://PepsiCoIT@dev.azure.com/PepsiCoIT/EIP-Infrastructure/_git/eip-infra-terraform-modules//modules/azure_kubernetes_services"
  
  # Pass all the variables we defined above
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
  active_directory_admin_group_object_ids = var.active_directory_admin_group_object_ids
  private_dns_zone_id                     = var.private_dns_zone_id
  kubernetes_version                      = var.kubernetes_version
  cluster_location                        = var.cluster_location
  # ... (more variables)
}

# Return outputs for other systems to use
output "cluster_name" {
  value       = module.aks_cluster.cluster_name
  description = "The name of the created AKS cluster"
}

output "kube_config" {
  value       = module.aks_cluster.kube_config
  sensitive   = true
  description = "Kubernetes config for connecting to cluster"
}
```

**What you're doing:**
- Calling the reusable module from `eip-infra-terraform-modules`
- Passing all our configuration variables
- The module returns outputs we expose to other systems

---

### **Step 3: Run Azure DevOps Pipeline**

The `azure-pipelines.yml` is triggered manually. You fill in parameters:

```yaml
# You select:
- Functional_Area: eiap
- Environment: nonprod
- Region: eus
- ResourceType: azure-kubernetes-services
- ResourceGroupName: pep-eiap-nonprod-eus-k8s-01-rg
- ResourceName: pep-eiap-nonprod-eus-app-01-aks
```

The pipeline then:

**Step 3a: Initialize Terraform**
```bash
terraform init \
  -backend-config="resource_group_name=pep-eiap-nonprod-eus-infra-01-rg" \
  -backend-config="storage_account_name=pepstorage" \
  -backend-config="container_name=eiap-storage-container" \
  -backend-config="key=terraform.tfstate"
```

**What's happening:**
- Downloading the AKS module from the Git repo
- Setting up the backend (where to store the state file)
- State file = snapshot of created resources (critical for Terraform to know what exists)
- Stored in Azure Storage Account for team access

**Step 3b: Generate a Plan**
```bash
terraform plan \
  -var-file="defaults-pep-eiap-nonprod-eus-app-01-aks.tfvars" \
  -var-file="mandatory-pep-eiap-nonprod-eus-app-01-aks.tfvars" \
  -var-file="nodepools-pep-eiap-nonprod-eus-app-01-aks.tfvars" \
  -out=plan.tfplan
```

**What's happening:**
- Loads all three `.tfvars` files
- Merges them together
- Compares with state file to see what's different
- Outputs a plan: "I will create 1 cluster, 2 node pools, X networking resources"

**Step 3c: Review and Approve**
- DevOps engineer reviews the plan
- If it looks good, approves (gates prevent bad changes)
- If it's production, requires 2 approvals

**Step 3d: Apply**
```bash
terraform apply plan.tfplan
```

**What's happening:**
- Executes all the create/update operations
- AKS cluster starts provisioning in Azure (takes 10-15 minutes)
- Node pools are created with specified VMs
- Updates state file with new resources
- Returns outputs (cluster endpoint, config, etc.)

---

## Step-by-Step: How to Add New Nodes/Scale Up {#add-nodes}

Now you have a cluster running. Application load increased. You need more nodes.

### **Scenario: App Node Pool Currently Has 3 Nodes, Need to Scale to 5**

### **Option 1: Horizontal Scaling (Most Common)**

Edit the node pool configuration:

```hcl
# File: nodepools-pep-eiap-nonprod-eus-app-01-aks.tfvars
node_pools = {
  app-np = {
    name                  = "appnp"
    vm_size               = "Standard_E8ds_v4"
    node_count            = 5          # ← Changed from 3 to 5
    enable_auto_scaling   = true
    min_count             = 3          # Always keep 3
    max_count             = 10         # Can grow up to 10
    # ... rest stays the same
  }
}
```

Run the pipeline again:

```bash
# Pipeline runs with updated tfvars
terraform plan
# Output: "app node pool will be scaled from 3 to 5 nodes"

terraform apply
# 2 new VMs start in the node pool
# Kubernetes auto-discovers them and adds to cluster
```

**What's happening:**
- Terraform modifies the node pool definition
- Azure VM Scale Set adds 2 new VMs
- Kubernetes node agents start on them
- Pods automatically schedule on new nodes

**Why this is better than manual:**
- Change 1 number, 1000 clusters update
- Tracked in Git (who changed it, when, why)
- Reverted easily if needed
- No manual SSH to servers

### **Option 2: Automatic Scaling (Most Cost-Effective)**

If you already have autoscaling enabled:

```hcl
enable_auto_scaling = true
min_count           = 3      # Always running
max_count           = 10     # Auto-grow to this if needed
```

Kubernetes monitors pod requests. When it can't fit pods:
1. It asks the cloud provider to add nodes
2. Azure spins up new VMs (up to max_count)
3. Kubernetes reschedules pending pods
4. When load decreases, nodes scale down

### **Option 3: Vertical Scaling (Less Common)**

Replace smaller VMs with larger VMs:

```hcl
app-np = {
  name     = "appnp"
  vm_size  = "Standard_D16ds_v4"  # ← Changed from E8ds to D16ds
  # ... rest stays the same
}
```

Terraform will:
1. Create new node pool with larger VMs
2. Migrate pods from old nodes
3. Delete old smaller nodes

---

## Step-by-Step: How to Update/Upgrade a Cluster {#upgrade-cluster}

Kubernetes releases new versions quarterly. Azure supports the last 3 versions. You need to upgrade.

### **Current State:**
- Cluster running Kubernetes 1.33.5
- New version available: 1.34.7
- Need to upgrade control plane (API server) → node pools → wait for stability

### **Step 1: Plan the Upgrade**

Edit the tfvars files:

```hcl
# File: defaults-pep-eiap-nonprod-eus-app-01-aks.tfvars
aks_clusters = {
  pep-eiap-nonprod-eus-app-01-aks = {
    # ... all other settings ...
    # No need to change - just the individual node pools
  }
}

# File: nodepools-pep-eiap-nonprod-eus-app-01-aks.tfvars
node_pools = {
  system-np = {
    orchestrator_version = "1.34.7"  # ← Changed from 1.33.5
    # ... rest stays the same
  }
  app-np = {
    orchestrator_version = "1.34.7"  # ← Changed from 1.33.5
    # ... rest stays the same
  }
}
```

### **Step 2: Use the Upgrade Pipeline**

There's a special pipeline for upgrades: `AKS-Cluster-Upgrade-NonProd-Terraform.yml`

Parameters:
```yaml
- control_plane_upgrade: true
- system_pool_upgrade: true
- user_pool_upgrade: true
- max_surge: 1  # How many nodes to upgrade in parallel
```

### **Step 3: Execution Flow**

```
┌─────────────────────────────────────────────────┐
│  1. Control Plane Upgrade (5-10 mins)           │
│     - Kubernetes API server upgrades            │
│     - etcd (cluster database) upgrades          │
│     - Cluster remains available                 │
└─────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────┐
│  2. System Node Pool Upgrade (15-20 mins)       │
│     - Cordon nodes (no new pods)                │
│     - Drain existing pods                       │
│     - Upgrade node Kubernetes version           │
│     - Rejoin cluster                            │
│     - max_surge=1 means 1 node at a time        │
└─────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────┐
│  3. User Node Pool Upgrade (30-40 mins)         │
│     - Same process: cordon → drain → upgrade    │
│     - Pods reschedule to upgraded nodes         │
│     - Applications stay running (high availability)
└─────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────┐
│  4. Validation (automated)                      │
│     - Run cluster health checks                 │
│     - Verify all pods running                   │
│     - Check node status                         │
└─────────────────────────────────────────────────┘
```

**Key Point - max_surge Parameter:**

```hcl
max_surge = ["1"]  # Upgrade 1 node at a time

# If you have 3 app nodes:
# - Node 1: Cordon (stop new pods) → Drain → Upgrade → Uncordon → Join
# - Node 2: Same process starts
# - Node 3: Same process starts
# Total time scales with number of nodes
```

**Why max_surge=1 instead of 3?**
- With max_surge=1: Always have 2 nodes running, so apps stay up
- With max_surge=3: All nodes upgrade in parallel, apps might be down
- Trade-off: slower upgrade (1-2 hours) vs. continuous availability

---

## Step-by-Step: How to Install New Software {#install-software}

Terraform creates the infrastructure (cluster + nodes). But how do you install software like:
- Prometheus (monitoring)
- NGINX ingress controller (routing)
- Service mesh (Istio/Linkerd)

**Important**: Terraform creates infrastructure. **Helm/ArgoCD installs applications**.

### **Example: Install NGINX Ingress Controller**

#### **Method 1: Manual Installation (One-Time)**

```bash
# Login to cluster
az aks get-credentials --name pep-eiap-nonprod-eus-app-01-aks \
  --resource-group pep-eiap-nonprod-eus-k8s-01-rg

# Add Helm repository
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

# Install
helm install nginx-ingress ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer
```

#### **Method 2: Via Terraform (Infrastructure as Code)**

Create a Helm Terraform module (in `eip-infra-terraform-modules/modules/helm/`):

```hcl
# File: helm/nginx-ingress/main.tf
terraform {
  required_providers {
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
  }
}

provider "helm" {
  kubernetes {
    host                   = azurerm_kubernetes_cluster.aks_cluster.kube_config.0.host
    client_certificate     = base64decode(azurerm_kubernetes_cluster.aks_cluster.kube_config.0.client_certificate)
    client_key             = base64decode(azurerm_kubernetes_cluster.aks_cluster.kube_config.0.client_key)
    cluster_ca_certificate = base64decode(azurerm_kubernetes_cluster.aks_cluster.kube_config.0.cluster_ca_certificate)
  }
}

# Install NGINX via Helm
resource "helm_release" "nginx_ingress" {
  name             = "nginx-ingress"
  repository       = "https://kubernetes.github.io/ingress-nginx"
  chart            = "ingress-nginx"
  namespace        = "ingress-nginx"
  create_namespace = true
  
  set {
    name  = "controller.service.type"
    value = "LoadBalancer"
  }
  
  set {
    name  = "controller.replicaCount"
    value = "3"  # High availability
  }
}
```

Then in your environment-specific config:

```hcl
# File: src/eiap/nonprod/common-tf-config/main.tf
module "nginx" {
  source = "git::https://...//modules/helm/nginx-ingress"
  
  depends_on = [module.aks_cluster]
}
```

Run the pipeline:
```bash
terraform plan   # Shows: "Will install nginx-ingress Helm chart"
terraform apply  # Installs NGINX on the cluster
```

#### **Method 3: Via ArgoCD (Continuous Delivery)**

For production clusters, use ArgoCD (GitOps):

```yaml
# File: eip-infra-k8s-argocd-support/eiap/prod/ingress-nginx.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: nginx-ingress
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://kubernetes.github.io/ingress-nginx
    targetRevision: 4.8.0
    chart: ingress-nginx
    helm:
      values: |
        controller:
          replicaCount: 3
          service:
            type: LoadBalancer
  destination:
    server: https://kubernetes.default.svc
    namespace: ingress-nginx
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

**What happens:**
- Commit this file to Git
- ArgoCD continuously watches Git
- Detects change → automatically deploys/updates NGINX
- If someone manually changes cluster → ArgoCD fixes it (GitOps)

---

## Real-World Example Walkthrough {#real-world-example}

Let me walk through a complete real-world scenario that ties everything together.

### **Scenario: Build a New Cluster for a New Application Team**

**Requirements:**
- Application team "PEP-DataOps" needs a new AKS cluster
- Environment: Nonprod (for development)
- Region: East US (same region as other clusters)
- Initial: 1 cluster with 2 node pools (system + app)
- Auto-scaling: 3-10 app nodes based on load
- Need monitoring (Prometheus), logging (ELK), and ingress (NGINX)
- Timeline: 2 weeks to production

### **Week 1: Infrastructure Setup**

#### **Day 1: Requirements Gathering**
```
Meeting notes:
- Cluster name: pep-eiap-nonprod-eus-dataops-01-aks
- VM size: Standard_E8ds_v4 (app), Standard_D4s_v3 (system)
- K8s version: 1.34.7
- Network: Existing VNet (pep-eiap-nonprod-eus-network-01-vnet)
- DNS: Private (no public exposure)
```

#### **Day 2-3: Create Configuration Files**

**Create directory:**
```
mkdir -p eip-infra-azure-terraform-support/src/eiap/nonprod/resources/eus/azure-kubernetes-services/pep-eiap-nonprod-eus-dataops-01-aks
```

**Create three tfvars files** (as shown in Step-by-Step section above)

#### **Day 4: Commit to Git**
```bash
git add eip-infra-azure-terraform-support/src/eiap/nonprod/resources/eus/...
git commit -m "feat: add DataOps AKS cluster configuration"
git push origin main
```

#### **Day 5: Trigger Pipeline**

1. Open Azure DevOps → Pipelines → azure-pipelines.yml
2. Click "Run" → Fill parameters:
   - Functional_Area: eiap
   - Environment: nonprod
   - Region: eus
   - ResourceType: azure-kubernetes-services
   - ResourceGroupName: pep-eiap-nonprod-eus-k8s-01-rg
   - ResourceName: pep-eiap-nonprod-eus-dataops-01-aks
3. Click "Run"

**Pipeline Progress:**
- terraform init (2 mins)
- terraform plan (2 mins) → Review output
- terraform apply (15-20 mins) → Cluster provisioning

**Success!** Cluster is running.

### **Week 2: Install Applications**

#### **Day 6: Install Monitoring (Prometheus + Grafana)**

Create Terraform Helm module:
```hcl
# modules/helm/prometheus/main.tf
resource "helm_release" "prometheus" {
  name             = "prometheus"
  chart            = "kube-prometheus-stack"
  repository       = "https://prometheus-community.github.io/helm-charts"
  namespace        = "monitoring"
  create_namespace = true
  
  values = [file("${path.module}/values.yaml")]
}
```

Add to environment config and run pipeline.

#### **Day 7: Install Logging (ELK Stack)**

```hcl
resource "helm_release" "elasticsearch" {
  name       = "elasticsearch"
  chart      = "elasticsearch"
  repository = "https://helm.elastic.co"
  namespace  = "logging"
  # ... configuration
}

resource "helm_release" "logstash" { ... }
resource "helm_release" "kibana" { ... }
```

#### **Day 8-9: Install NGINX & Configure Ingress**

```hcl
resource "helm_release" "nginx_ingress" { ... }

# Create Kubernetes Ingress resource
resource "kubernetes_ingress_v1" "dataops_app" {
  metadata {
    name      = "dataops-app-ingress"
    namespace = "dataops-app"
  }
  
  spec {
    ingress_class_name = "nginx"
    
    rule {
      host = "dataops-app.company.com"
      http {
        path {
          path       = "/"
          path_type  = "Prefix"
          backend {
            service {
              name = "dataops-app-service"
              port {
                number = 8080
              }
            }
          }
        }
      }
    }
  }
}
```

#### **Day 10: Testing & Validation**

```bash
# Get cluster credentials
az aks get-credentials \
  --name pep-eiap-nonprod-eus-dataops-01-aks \
  --resource-group pep-eiap-nonprod-eus-k8s-01-rg

# Check nodes
kubectl get nodes
# Output:
# NAME                       STATUS   ROLES   AGE
# aks-systemnp-123456789-1   Ready    agent   2d
# aks-appnp-123456789-1      Ready    agent   2d
# aks-appnp-123456789-2      Ready    agent   2d
# aks-appnp-123456789-3      Ready    agent   2d

# Check Helm releases
helm list -A
# Output:
# NAME           NAMESPACE       STATUS
# prometheus     monitoring      deployed
# elasticsearch  logging         deployed
# kibana         logging         deployed
# nginx-ingress  ingress-nginx   deployed

# Access Grafana dashboard
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
# Navigate to http://localhost:3000
```

#### **Day 11-14: Production Readiness**

- Load testing
- Security scanning
- Backup/disaster recovery testing
- Team training

---

## Common Terraform Commands {#common-commands}

### **Basic Commands**

```bash
# Initialize Terraform (download modules, setup backend)
terraform init

# Validate syntax
terraform validate

# Format code (auto-fix indentation)
terraform fmt -recursive

# Plan (preview changes)
terraform plan -var-file="values.tfvars"

# Apply (make the changes)
terraform apply -var-file="values.tfvars"

# Show current state
terraform show

# Refresh state (sync with actual Azure state)
terraform refresh

# Destroy (delete all resources)
terraform destroy -var-file="values.tfvars"
```

### **Debugging Commands**

```bash
# Enable debug logging
export TF_LOG=DEBUG
terraform plan

# Show state file
terraform state list

# Show specific resource state
terraform state show azurerm_kubernetes_cluster.aks_cluster

# Graph resources (create visualization)
terraform graph | dot -Tsvg > graph.svg

# Get resource details
terraform show -json | jq '.values.root_module.resources[] | select(.address=="azurerm_kubernetes_cluster.aks_cluster")'
```

### **Azure CLI Integration**

```bash
# List all AKS clusters
az aks list --output table

# Get kubeconfig for a cluster
az aks get-credentials \
  --resource-group pep-eiap-nonprod-eus-k8s-01-rg \
  --name pep-eiap-nonprod-eus-dataops-01-aks

# Update cluster
az aks update --resource-group rg --name cluster-name --kubernetes-version 1.34.7

# Scale node pool
az aks nodepool scale \
  --resource-group rg \
  --cluster-name cluster-name \
  --name appnp \
  --node-count 5
```

---

## Troubleshooting Guide {#troubleshooting}

### **Problem 1: Terraform Plan Shows Errors**

#### **Error**: "Error acquiring the state lock"

**Cause**: Another pipeline is running or state lock file is stuck

**Solution**:
```bash
# Check who has the lock
terraform state list

# Force unlock (use carefully!)
terraform force-unlock LOCK_ID
```

#### **Error**: "Invalid resource reference: azurerm_subnet.aks_vnet_snet_assoc"

**Cause**: Terraform can't find the subnet (data source query failed)

**Solution**:
```bash
# Verify subnet exists in Azure
az network vnet subnet list \
  --resource-group pep-eiap-nonprod-eus-network-01-rg \
  --vnet-name pep-eiap-nonprod-eus-network-01-vnet \
  --query "[*].name"

# Check if vnet/subnet name in tfvars is correct (case-sensitive!)
```

### **Problem 2: Cluster Creation Fails Halfway**

#### **Error**: "Operation timed out"

**Cause**: Azure resource provisioning took too long

**Solution**:
```bash
# Check cluster status in Azure
az aks show -g pep-eiap-nonprod-eus-k8s-01-rg \
  -n pep-eiap-nonprod-eus-dataops-01-aks \
  --query provisioningState

# If "Updating", wait longer
# If "Failed", get error details
az aks show -g pep-eiap-nonprod-eus-k8s-01-rg \
  -n pep-eiap-nonprod-eus-dataops-01-aks \
  --query "{status: powerState.code, error: fqdn}"

# Retry apply
terraform apply -var-file="values.tfvars" -parallelism=2
```

### **Problem 3: Nodes Don't Join Cluster**

#### **Error**: Nodes in "NotReady" state

```bash
# Check node status
kubectl get nodes

# Describe problem node
kubectl describe node aks-appnp-123456789-1

# Check kubelet logs on node
kubectl logs -n kube-system -l component=kubelet --tail=50

# SSH to node and check Docker
# (only works if linux_profile_enabled = ["true"])
```

**Cause**: Usually networking or CNI issues

**Solution**:
```bash
# Check network policy
kubectl get networkpolicies -A

# Check DNS
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup kubernetes.default

# Restart kubelet on problematic node
kubectl drain aks-appnp-123456789-1 --ignore-daemonsets
az vmss restart -g MC_rg_cluster_region --name aks-nodepool-123456789 --instance-ids 1
```

### **Problem 4: Cluster Upgrade Fails**

#### **Error**: "Pod eviction failed"

**Cause**: Pod has no replacement (stateful without PVC)

**Solution**:
```bash
# See which pods are blocking drain
kubectl drain aks-appnp-123456789-1 --ignore-daemonsets

# If specific pod blocks, manually delete or migrate it
kubectl delete pod problematic-pod -n namespace --grace-period=0

# Retry upgrade
terraform apply -var-file="values.tfvars"
```

### **Problem 5: State File Issues**

#### **Error**: "State has diverged from actual infrastructure"

**Cause**: Someone manually changed Azure resources or state file is corrupted

**Solution**:
```bash
# Refresh state (sync with Azure)
terraform refresh

# If still diverged, import the resource
terraform import azurerm_kubernetes_cluster.aks_cluster /subscriptions/sub-id/resourceGroups/rg/providers/Microsoft.ContainerService/managedClusters/cluster-name

# Review and commit state file changes
git add terraform.tfstate
git commit -m "Sync state with actual Azure resources"
```

---

## Interview Tips Summary

### **If asked "How would you build a new cluster?"**

**Answer Structure:**
1. "First, I'd create three `.tfvars` files with cluster configuration"
2. "Then, I'd create a `main.tf` that calls the reusable AKS module from the modules repository"
3. "I'd commit to Git for version control"
4. "Then trigger the Azure DevOps pipeline with the cluster parameters"
5. "Pipeline runs terraform init → plan → (approval) → apply"
6. "Cluster is created in 15-20 minutes"

### **If asked "How do you scale nodes?"**

**Answer Structure:**
1. "There are three methods: horizontal (add nodes), vertical (bigger VMs), or automatic"
2. "For horizontal: Edit the `node_count` in tfvars from 3 to 5"
3. "For automatic: We use `enable_auto_scaling=true` with `min_count` and `max_count`"
4. "Kubernetes auto-scales when it detects pending pods"
5. "Either way, we use Terraform so it's tracked in Git and repeatable"

### **If asked "How do you upgrade Kubernetes?"**

**Answer Structure:**
1. "We have a dedicated `AKS-Cluster-Upgrade-NonProd-Terraform.yml` pipeline"
2. "Change `orchestrator_version` from 1.33.5 to 1.34.7 in tfvars"
3. "Pipeline executes in phases: control plane → system pool → user pools"
4. "`max_surge=1` ensures high availability (always some nodes running)"
5. "Nodes are cordoned (no new pods), drained (existing pods moved), upgraded, then rejoined"
6. "Zero downtime with proper pod replicas"

### **If asked "What's the difference between the module and environment repos?"**

**Answer Structure:**
1. "Modules repo (`eip-infra-terraform-modules`) is the blueprint library"
2. "One module can be used by 100+ clusters in 50+ environments"
3. "Environment repo (`eip-infra-azure-terraform-support`) has specific values for each cluster"
4. "Think of it like a recipe book vs. ingredient shopping list"
5. "Module = code, Environment = data"

---

## Key Takeaways

✅ **Terraform** = Infrastructure as Code (define infrastructure in `.tf` files)

✅ **Modules** = Reusable building blocks (one module, many clusters)

✅ **Tfvars** = Configuration values (cluster size, version, networking)

✅ **State File** = Source of truth (what resources exist)

✅ **Backend** = Where state file lives (Azure Storage Account)

✅ **Pipeline** = Automation (GitOps trigger for infrastructure changes)

✅ **Plan** = Preview of changes (always review before apply)

✅ **Apply** = Execute infrastructure creation/updates

✅ **Scaling** = 3 methods (horizontal, vertical, automatic)

✅ **Upgrades** = Phased approach (control plane → system → user pools)

✅ **High Availability** = Spread across zones, multiple replicas, max_surge settings

This comprehensive guide should help you explain Terraform infrastructure as code in an interview-friendly, one-to-one conversational manner!

