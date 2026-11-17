node_pools = {
  nps1z2 = {
    name                  = "nps1z2"
    vm_size               = "Standard_E4ds_v4"
    node_count            = 1
    enable_auto_scaling   = true
    enable_node_public_ip = false
    pod_max_pid        = ["4194304"]
    kubelet_disk_type     = "OS"
    max_count             = 1
    min_count             = 1
    node_labels = {
      balance-group         = "System01ZonedPools"
    }  
    node_taints           = ["CriticalAddonsOnly=Exists:NoSchedule"]
    orchestrator_version  = "1.25.6"
    os_disk_size_gb       = 100
    os_disk_type          = "Ephemeral"
    os_type               = "Linux"
    os_sku                = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    tags = {
      ModifiedData  = "{\"User\": \"80303850\", \"TimeStamp\": \"2023-07-11T13:35:34\", \"ExecuteHost\": \"USC02DVADXML85\"}"
      department    = "weblogic"
      description   = "Global 01 AKS Cluster"
      environment   = "nonprod"
      financialTag  = "H-######"
      serviceName   = "weblogic"
      spn           = "pep-eiap-nonprod-k8s-sp"
    }
    max_surge                     = [] #set this to [] if not using this setting while AKS creation; provide max_surge value within "" if using this property    
    zones                         = [2]
    mode                          = "System"
    cluster_name                  = "pep-weblogic-nonprod-eus-01-aks"
    cluster_resource_group_name   = "pep-eiap-nonprod-eus-sqldba-01-rg"
    vnet_name                     = "pep-eiap-nonprod-eus-network-01-vnet"
    snet_name                     = "pep-eiap-nonprod-eus-network-01-vnet-weblogic-01-aks-01-snet"
    vnet_snet_resource_group_name = "pep-eiap-nonprod-eus-network-01-rg"
    proximity_placement_group_id  = null
  }

  npu1z1 = {
    name                  = "npu1z1"
    vm_size               = "Standard_E4ds_v4"
    node_count            = 0
    enable_auto_scaling   = true
    enable_node_public_ip = false
    pod_max_pid        = ["4194304"]
    kubelet_disk_type     = "OS"
    max_count             = 2
    min_count             = 0
    node_labels = {
      balance-group         = "User01ZonedPools"
    }
    node_taints           = []
    orchestrator_version  = "1.25.6"
    os_disk_size_gb       = 100
    os_disk_type          = "Ephemeral"
    os_type               = "Linux"
    os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    tags ={
      ModifiedData  = "{\"User\": \"80303850\", \"TimeStamp\": \"2023-07-11T13:47:31\", \"ExecuteHost\": \"USC02DVADXML85\"}"
      department    = "weblogic"
      description   = "Global 01 AKS Cluster"
      environment   = "nonprod"
      financialTag  = "H-######"
      serviceName   = "weblogic"
      spn           = "pep-eiap-nonprod-k8s-sp"
    }
    max_surge                     = [] #set this to [] if not using this setting while AKS creation; provide max_surge value within "" if using this property    
    zones                         = [1]
    mode                          = "User"
    cluster_name                  = "pep-weblogic-nonprod-eus-01-aks"
    cluster_resource_group_name   = "pep-eiap-nonprod-eus-sqldba-01-rg"
    vnet_name                     = "pep-eiap-nonprod-eus-network-01-vnet"
    snet_name                     = "pep-eiap-nonprod-eus-network-01-vnet-weblogic-01-aks-01-snet"
    vnet_snet_resource_group_name = "pep-eiap-nonprod-eus-network-01-rg"
    proximity_placement_group_id  = null
  }

  npu1z2 = {
    name                  = "npu1z2"
    vm_size               = "Standard_E4ds_v4"
    node_count            = 0
    enable_auto_scaling   = true
    enable_node_public_ip = false
    pod_max_pid        = ["4194304"]
    kubelet_disk_type     = "OS"
    max_count             = 2
    min_count             = 0
    node_labels = {
      balance-group         = "User01ZonedPools"
    }  
    node_taints           = []
    orchestrator_version  = "1.25.6"
    os_disk_size_gb       = 100
    os_disk_type          = "Ephemeral"
    os_type               = "Linux"
    os_sku                = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    
    tags = {
      ModifiedData = "{\"User\": \"80303850\", \"TimeStamp\": \"2023-07-11T13:45:33\", \"ExecuteHost\": \"USC02DVADXML85\"}"
      department = "weblogic"
      description = "Global 01 AKS Cluster"
      environment = "nonprod"
      financialTag = "H-######"
      serviceName = "weblogic"
      spn = "pep-eiap-nonprod-k8s-sp"
    }
    max_surge                     = [] #set this to [] if not using this setting while AKS creation; provide max_surge value within "" if using this property    
    zones                         = [2]
    mode                          = "User"
    cluster_name                  = "pep-weblogic-nonprod-eus-01-aks"
    cluster_resource_group_name   = "pep-eiap-nonprod-eus-sqldba-01-rg"
    vnet_name                     = "pep-eiap-nonprod-eus-network-01-vnet"
    snet_name                     = "pep-eiap-nonprod-eus-network-01-vnet-weblogic-01-aks-01-snet"
    vnet_snet_resource_group_name = "pep-eiap-nonprod-eus-network-01-rg"
    proximity_placement_group_id  = null
  }

  npu1z3 = {
    name                  = "npu1z3"
    vm_size               = "Standard_E4ds_v4"
    node_count            = 1
    enable_auto_scaling   = true
    enable_node_public_ip = false
    pod_max_pid        = ["4194304"]
    kubelet_disk_type     = "OS"
    max_count             = 1
    min_count             = 0
    node_labels = {
      balance-group         = "User01ZonedPools"
    }
    node_taints           = []
    orchestrator_version  = "1.25.6"
    os_disk_size_gb       = 100
    os_disk_type          = "Ephemeral"
    os_type               = "Linux"
    os_sku                = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    
    tags = {
      ModifiedData    = "{\"User\": \"80303850\", \"TimeStamp\": \"2023-07-11T13:49:51\", \"ExecuteHost\": \"USC02DVADXML85\"}"
      department      = "weblogic"
      description     = "Global 01 AKS Cluster"
      environment     = "nonprod"
      financialTag    = "H-######"
      serviceName     = "weblogic"
      spn             = "pep-eiap-nonprod-k8s-sp"
    }
    max_surge                     = [] #set this to [] if not using this setting while AKS creation; provide max_surge value within "" if using this property    
    zones                         = [3]
    mode                          = "User"
    cluster_name                  = "pep-weblogic-nonprod-eus-01-aks"
    cluster_resource_group_name   = "pep-eiap-nonprod-eus-sqldba-01-rg"
    vnet_name                     = "pep-eiap-nonprod-eus-network-01-vnet"
    snet_name                     = "pep-eiap-nonprod-eus-network-01-vnet-weblogic-01-aks-01-snet"
    vnet_snet_resource_group_name = "pep-eiap-nonprod-eus-network-01-rg"
    proximity_placement_group_id  = null
  }
}