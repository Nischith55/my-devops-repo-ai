node_pools = {
  nps01z2 = {
    name                  = "nps01z2"
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
    orchestrator_version = "1.28.9"
    os_disk_size_gb      = 100
    os_disk_type         = "Ephemeral"
    os_type              = "Linux"
    os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    tags = {
      department   = "automation"
      description  = "Global 01 AKS Cluster"
      environment  = "nonprod"
      financialTag = "H-######"
      serviceName  = "automation"
      spn          = "pep-eiap-nonprod-k8s-sp"
    }
    max_surge                     = ["1"] #set this to [] if not using this property while AKS creation
    zones                         = [2]
    mode                          = "System"
    cluster_name                  = "pep-automation-nonprod-eus-01-aks"
    cluster_resource_group_name   = "pep-ess-automation-aks-nonprod-eus-01-rg"
    vnet_name                     = "pep-paas-automation-nonprod-01-eus-vnet"
    snet_name                     = "pep-aks-01-subnet"
    vnet_snet_resource_group_name = "pep-network-nonprod-automation-eus-01-rg"
    proximity_placement_group_id  = null
  }
  nps01z3 = {
    name                  = "nps01z3"
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
    orchestrator_version = "1.28.9"
    os_disk_size_gb      = 100
    os_disk_type         = "Ephemeral"
    os_type              = "Linux"
    os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    tags = {
      department   = "automation"
      description  = "Global 01 AKS Cluster"
      environment  = "nonprod"
      financialTag = "H-######"
      serviceName  = "automation"
      spn          = "pep-eiap-nonprod-k8s-sp"
    }
    max_surge                     = ["1"] #set this to [] if not using this property while AKS creation
    zones                         = [3]
    mode                          = "System"
    cluster_name                  = "pep-automation-nonprod-eus-01-aks"
    cluster_resource_group_name   = "pep-ess-automation-aks-nonprod-eus-01-rg"
    vnet_name                     = "pep-paas-automation-nonprod-01-eus-vnet"
    snet_name                     = "pep-aks-01-subnet"
    vnet_snet_resource_group_name = "pep-network-nonprod-automation-eus-01-rg"
    proximity_placement_group_id  = null
  }
  npu01z1 = {
    name                  = "npu01z1"
    vm_size               = "Standard_E4ds_v4"
    node_count            = 0
    enable_auto_scaling   = true
    enable_node_public_ip = false
    pod_max_pid           = ["4194304"]
    kubelet_disk_type     = "OS"
    max_count             = 5
    min_count             = 0
    node_labels = {
      balance-group = "User01ZonedPools"
    }
    node_taints          = [] #this is always blank for default node pool
    orchestrator_version = "1.28.9"
    os_disk_size_gb      = 100
    os_disk_type         = "Ephemeral"
    os_type              = "Linux"
    os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    tags = {
      department   = "automation"
      description  = "Global 01 AKS Cluster"
      environment  = "nonprod"
      financialTag = "H-######"
      serviceName  = "automation"
      spn          = "pep-eiap-nonprod-k8s-sp"
    }
    max_surge                     = ["1"] #set this to [] if not using this property while AKS creation
    zones                         = [1]
    mode                          = "User"
    cluster_name                  = "pep-automation-nonprod-eus-01-aks"
    cluster_resource_group_name   = "pep-ess-automation-aks-nonprod-eus-01-rg"
    vnet_name                     = "pep-paas-automation-nonprod-01-eus-vnet"
    snet_name                     = "pep-aks-01-subnet"
    vnet_snet_resource_group_name = "pep-network-nonprod-automation-eus-01-rg"
    proximity_placement_group_id  = null
  }
  npu01z2 = {
    name                  = "npu01z2"
    vm_size               = "Standard_E4ds_v4"
    node_count            = 0
    enable_auto_scaling   = true
    enable_node_public_ip = false
    pod_max_pid           = ["4194304"]
    kubelet_disk_type     = "OS"
    max_count             = 5
    min_count             = 0
    node_labels = {
      balance-group = "User01ZonedPools"
    }
    node_taints          = [] #this is always blank for default node pool
    orchestrator_version = "1.28.9"
    os_disk_size_gb      = 100
    os_disk_type         = "Ephemeral"
    os_type              = "Linux"
    os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    tags = {
      department   = "automation"
      description  = "Global 01 AKS Cluster"
      environment  = "nonprod"
      financialTag = "H-######"
      serviceName  = "automation"
      spn          = "pep-eiap-nonprod-k8s-sp"
    }
    max_surge                     = ["1"] #set this to [] if not using this property while AKS creation
    zones                         = [2]
    mode                          = "User"
    cluster_name                  = "pep-automation-nonprod-eus-01-aks"
    cluster_resource_group_name   = "pep-ess-automation-aks-nonprod-eus-01-rg"
    vnet_name                     = "pep-paas-automation-nonprod-01-eus-vnet"
    snet_name                     = "pep-aks-01-subnet"
    vnet_snet_resource_group_name = "pep-network-nonprod-automation-eus-01-rg"
    proximity_placement_group_id  = null
  }
  npu01z3 = {
    name                  = "npu01z3"
    vm_size               = "Standard_E4ds_v4"
    node_count            = 0
    enable_auto_scaling   = true
    enable_node_public_ip = false
    pod_max_pid           = ["4194304"]
    kubelet_disk_type     = "OS"
    max_count             = 5
    min_count             = 0
    node_labels = {
      balance-group = "User01ZonedPools"
    }
    node_taints          = [] #this is always blank for default node pool
    orchestrator_version = "1.28.9"
    os_disk_size_gb      = 100
    os_disk_type         = "Ephemeral"
    os_type              = "Linux"
    os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    tags = {
      department   = "automation"
      description  = "Global 01 AKS Cluster"
      environment  = "nonprod"
      financialTag = "H-######"
      serviceName  = "automation"
      spn          = "pep-eiap-nonprod-k8s-sp"
    }
    max_surge                     = ["1"] #set this to [] if not using this property while AKS creation
    zones                         = [3]
    mode                          = "User"
    cluster_name                  = "pep-automation-nonprod-eus-01-aks"
    cluster_resource_group_name   = "pep-ess-automation-aks-nonprod-eus-01-rg"
    vnet_name                     = "pep-paas-automation-nonprod-01-eus-vnet"
    snet_name                     = "pep-aks-01-subnet"
    vnet_snet_resource_group_name = "pep-network-nonprod-automation-eus-01-rg"
    proximity_placement_group_id  = null
  }
}