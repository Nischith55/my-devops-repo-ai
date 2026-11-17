node_pools = {
    nps1z2 = {
    name                  = "nps1z2"
    vm_size               = "Standard_E4ds_v4"
    node_count            = 1
    enable_auto_scaling   = true
    enable_node_public_ip = false
    pod_max_pid           = ["4194304"]
    kubelet_disk_type     = "OS"
    max_count             = 3
    min_count             = 1
    node_labels = {
      balance-group = "System01ZonedPools"
    }
    node_taints          = ["CriticalAddonsOnly=Exists:NoSchedule"] #this is always blank for default node pool
    orchestrator_version = "1.33.6"
    os_disk_size_gb      = 100
    os_disk_type         = "Ephemeral"
    os_type              = "Linux"
    os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    tags = {
      department   = "pbna"
      description  = "PBNA Apigee scus prod DR 01 AKS Cluster"
      environment  = "prod-dr"
      financialTag = "H-007819"
      serviceName  = "pbna"
      spn          = "pep-eiap-prod-k8s-sp"
    }
    max_surge                     = ["1"] #set this to [] if not using this property while AKS creation
    zones                         = [2]
    mode                          = "System"
    cluster_name                  = "pep-pbna-apigee-prod-scus-dr-01-aks"
    cluster_resource_group_name   = "pep-dr-apigee-prod-scus-k8s-01-rg"
    vnet_name                     = "pep-sharedservice-dr-01-scus-vnet"
    snet_name                     = "pep-aks-01-subnet"
    vnet_snet_resource_group_name = "pep-network-sharedservice-dr-scus-01-rg"
    proximity_placement_group_id  = null
  }
  napgdata01z1 = {
    name                  = "napgdata01z1"
    vm_size               = "Standard_D4ds_v4"
    node_count            = 1
    enable_auto_scaling   = true
    enable_node_public_ip = false
    pod_max_pid           = ["4194304"]
    kubelet_disk_type     = "OS"
    max_count             = 1
    min_count             = 1
    node_labels = {
      balance-group = "APGData01ZonedPools"
    }
    node_taints          = ["APG01dataNodeOnly=Exists:NoSchedule"] #this is always blank for default node pool
    orchestrator_version = "1.33.6"
    os_disk_size_gb      = 150
    os_disk_type         = "Ephemeral"
    os_type              = "Linux"
    os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    tags = {
      department   = "pbna"
      description  = "PBNA Apigee scus prod DR 01 AKS Cluster"
      environment  = "prod-dr"
      financialTag = "H-007819"
      serviceName  = "pbna"
      spn          = "pep-eiap-prod-k8s-sp"
    }
    max_surge                     = [] #set this to [] if not using this property while AKS creation
    zones                         = [1]
    mode                          = "User"
    cluster_name                  = "pep-pbna-apigee-prod-scus-dr-01-aks"
    cluster_resource_group_name   = "pep-dr-apigee-prod-scus-k8s-01-rg"
    vnet_name                     = "pep-sharedservice-dr-01-scus-vnet"
    snet_name                     = "pep-aks-01-subnet"
    vnet_snet_resource_group_name = "pep-network-sharedservice-dr-scus-01-rg"
    proximity_placement_group_id  = null
  }
  napgcomp01z1 = {
    name                  = "napgcomp01z1"
    vm_size               = "Standard_D4ds_v4"
    node_count            = 1
    enable_auto_scaling   = true
    enable_node_public_ip = false
    pod_max_pid           = ["4194304"]
    kubelet_disk_type     = "OS"
    max_count             = 3
    min_count             = 1
    node_labels = {
      balance-group = "APGComp01ZonedPools"
    }
    node_taints          = ["APGComp01NodeOnly=Exists:NoSchedule"] #this is always blank for default node pool
    orchestrator_version = "1.33.6"
    os_disk_size_gb      = 150
    os_disk_type         = "Ephemeral"
    os_type              = "Linux"
    os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    tags = {
      department   = "pbna"
      description  = "PBNA Apigee scus prod DR 01 AKS Cluster"
      environment  = "prod-dr"
      financialTag = "H-007819"
      serviceName  = "pbna"
      spn          = "pep-eiap-prod-k8s-sp"
    }
    max_surge                     = ["1"] #set this to [] if not using this property while AKS creation
    zones                         = [1]
    mode                          = "User"
    cluster_name                  = "pep-pbna-apigee-prod-scus-dr-01-aks"
    cluster_resource_group_name   = "pep-dr-apigee-prod-scus-k8s-01-rg"
    vnet_name                     = "pep-sharedservice-dr-01-scus-vnet"
    snet_name                     = "pep-aks-01-subnet"
    vnet_snet_resource_group_name = "pep-network-sharedservice-dr-scus-01-rg"
    proximity_placement_group_id  = null
  }
  napgrt01z1 = {
    name                  = "napgrt01z1"
    vm_size               = "Standard_D4ds_v4"
    node_count            = 1
    enable_auto_scaling   = true
    enable_node_public_ip = false
    pod_max_pid           = ["4194304"]
    kubelet_disk_type     = "OS"
    max_count             = 3
    min_count             = 1
    node_labels = {
      balance-group = "APGRuntime01ZonedPools"
    }
    node_taints          = ["APG01RuntimeNodeOnly=Exists:NoSchedule"] #this is always blank for default node pool
    orchestrator_version = "1.33.6"
    os_disk_size_gb      = 150
    os_disk_type         = "Ephemeral"
    os_type              = "Linux"
    os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    tags = {
      department   = "pbna"
      description  = "PBNA Apigee scus prod DR 01 AKS Cluster"
      environment  = "prod-dr"
      financialTag = "H-007819"
      serviceName  = "pbna"
      spn          = "pep-eiap-prod-k8s-sp"
    }
    max_surge                     = ["1"] #set this to [] if not using this property while AKS creation
    zones                         = [1]
    mode                          = "User"
    cluster_name                  = "pep-pbna-apigee-prod-scus-dr-01-aks"
    cluster_resource_group_name   = "pep-dr-apigee-prod-scus-k8s-01-rg"
    vnet_name                     = "pep-sharedservice-dr-01-scus-vnet"
    snet_name                     = "pep-aks-01-subnet"
    vnet_snet_resource_group_name = "pep-network-sharedservice-dr-scus-01-rg"
    proximity_placement_group_id  = null
  }
  npu1z1 = {
    name                  = "npu1z1"
    vm_size               = "Standard_D4ds_v4"
    node_count            = 1
    enable_auto_scaling   = true
    enable_node_public_ip = false
    pod_max_pid           = ["4194304"]
    kubelet_disk_type     = "OS"
    max_count             = 3
    min_count             = 1
    node_labels = {
      balance-group = "APGInternal01ZonedPools"
    }
    node_taints          = [] #this is always blank for default node pool
    orchestrator_version = "1.33.6"
    os_disk_size_gb      = 150
    os_disk_type         = "Ephemeral"
    os_type              = "Linux"
    os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    tags = {
      department   = "pbna"
      description  = "PBNA Apigee scus prod DR 01 AKS Cluster"
      environment  = "prod-dr"
      financialTag = "H-007819"
      serviceName  = "pbna"
      spn          = "pep-eiap-prod-k8s-sp"
    }
    max_surge                     = [] #set this to [] if not using this property while AKS creation
    zones                         = [1]
    mode                          = "User"
    cluster_name                  = "pep-pbna-apigee-prod-scus-dr-01-aks"
    cluster_resource_group_name   = "pep-dr-apigee-prod-scus-k8s-01-rg"
    vnet_name                     = "pep-sharedservice-dr-01-scus-vnet"
    snet_name                     = "pep-aks-01-subnet"
    vnet_snet_resource_group_name = "pep-network-sharedservice-dr-scus-01-rg"
    proximity_placement_group_id  = null
  }
}