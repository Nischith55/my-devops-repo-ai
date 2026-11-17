node_pools = {
  nps01z2 = {
    name                  = "nps01z2"
    vm_size               = "Standard_E4ds_v4"
    node_count            = 3
    enable_auto_scaling   = false
    enable_node_public_ip = false
    pod_max_pid           = ["4194304"]
    kubelet_disk_type     = "OS"
    max_count             = null
    min_count             = null
    max_pods              = "110"
    node_labels = {
      balance-group = "System01ZonedPools"

    }
    node_taints          = ["CriticalAddonsOnly=Exists:NoSchedule"] #this is always blank for default node pool
    orchestrator_version = "1.34.7"
    os_disk_size_gb      = 100
    os_disk_type         = "Ephemeral"
    os_type              = "Linux"
    os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    tags = {
      department                = "pepgenx"
      description               = "pepgenx 2.0 Cluster"
      environment               = "nonprod"
      financialTag              = "H-######"
      serviceName               = "aisp-pepgenx"
      spn                       = "pep-eiap-nonprod-k8s-sp"
      pep-cmdb-bus-app-name       = "DAI PEPGENX"
      pep-cmdb-bus-app-id         = "7f0e42b8c3ba46d8b74985359901310f"
      pep-cmdb-app-service-name   = "DAI PEPGENX"
      pep-cmdb-app-service-id     = "841e42b8c3ba46d8b7498535990131f7"
    }
    max_surge                     = [] #set this to [] if not using this property while AKS creation
    zones                         = [2]
    mode                          = "System"
    cluster_name                  = "pep-pepgenx-nonprod-eus-global-01-aks"
    cluster_resource_group_name   = "pep-azr-pepgenx2-dev-eus-01-rg"
    vnet_name                     = "pep-paas-azr-nonprod-pepgenx-01-eus-vnet"
    snet_name                     = "pep-aks-01-subnet"
    vnet_snet_resource_group_name = "pep-network-azr-nonprod-pepgenx-01-eus-rg"
    proximity_placement_group_id  = null
  }
  nps01z3 = {
    name                  = "nps01z3"
    vm_size               = "Standard_E4ds_v4"
    node_count            = 3
    enable_auto_scaling   = false
    enable_node_public_ip = false
    pod_max_pid           = ["4194304"]
    kubelet_disk_type     = "OS"
    max_count             = null
    min_count             = null
    max_pods              = "110"
    node_labels = {
      balance-group = "System01ZonedPools"

    }
    node_taints          = ["CriticalAddonsOnly=Exists:NoSchedule"] #this is always blank for default node pool
    orchestrator_version = "1.34.7"
    os_disk_size_gb      = 100
    os_disk_type         = "Ephemeral"
    os_type              = "Linux"
    os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    tags = {
      department                = "pepgenx"
      description               = "pepgenx 2.0 Cluster"
      environment               = "nonprod"
      financialTag              = "H-######"
      serviceName               = "aisp-pepgenx"
      spn                       = "pep-eiap-nonprod-k8s-sp"
      pep-cmdb-bus-app-name       = "DAI PEPGENX"
      pep-cmdb-bus-app-id         = "7f0e42b8c3ba46d8b74985359901310f"
      pep-cmdb-app-service-name   = "DAI PEPGENX"
      pep-cmdb-app-service-id     = "841e42b8c3ba46d8b7498535990131f7"
    }
    max_surge                     = [] #set this to [] if not using this property while AKS creation
    zones                         = [3]
    mode                          = "System"
    cluster_name                  = "pep-pepgenx-nonprod-eus-global-01-aks"
    cluster_resource_group_name   = "pep-azr-pepgenx2-dev-eus-01-rg"
    vnet_name                     = "pep-paas-azr-nonprod-pepgenx-01-eus-vnet"
    snet_name                     = "pep-aks-01-subnet"
    vnet_snet_resource_group_name = "pep-network-azr-nonprod-pepgenx-01-eus-rg"
    proximity_placement_group_id  = null
  }
  npu01z1 = {
    name                  = "npu01z1"
    vm_size               = "Standard_E16ds_v4"
    node_count            = 1
    enable_auto_scaling   = false
    enable_node_public_ip = false
    pod_max_pid           = ["4194304"]
    kubelet_disk_type     = "OS"
    max_count             = null
    min_count             = null
    max_pods              = "110"
    node_labels = {
      balance-group = "User01ZonedPools"

    }
    node_taints          = [] #this is always blank for default node pool
    orchestrator_version = "1.34.7"
    os_disk_size_gb      = 150
    os_disk_type         = "Ephemeral"
    os_type              = "Linux"
    os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    tags = {
      department                = "pepgenx"
      description               = "pepgenx 2.0 Cluster"
      environment               = "nonprod"
      financialTag              = "H-######"
      serviceName               = "aisp-pepgenx"
      spn                       = "pep-eiap-nonprod-k8s-sp"
      pep-cmdb-bus-app-name       = "DAI PEPGENX"
      pep-cmdb-bus-app-id         = "7f0e42b8c3ba46d8b74985359901310f"
      pep-cmdb-app-service-name   = "DAI PEPGENX"
      pep-cmdb-app-service-id     = "841e42b8c3ba46d8b7498535990131f7"
    }
    max_surge                     = ["2"] #set this to [] if not using this property while AKS creation
    zones                         = [1]
    mode                          = "User"
    cluster_name                  = "pep-pepgenx-nonprod-eus-global-01-aks"
    cluster_resource_group_name   = "pep-azr-pepgenx2-dev-eus-01-rg"
    vnet_name                     = "pep-paas-azr-nonprod-pepgenx-01-eus-vnet"
    snet_name                     = "pep-aks-01-subnet"
    vnet_snet_resource_group_name = "pep-network-azr-nonprod-pepgenx-01-eus-rg"
    proximity_placement_group_id  = null
  }
  # npu01z2 = {
  #   name                  = "npu01z2"
  #   vm_size               = "Standard_E16ds_v4"
  #   node_count            = 0
  #   enable_auto_scaling   = true
  #   enable_node_public_ip = false
  #   pod_max_pid           = ["4194304"]
  #   kubelet_disk_type     = "OS"
  #   max_count             = 3
  #   min_count             = 1
  #   max_pods              = "110"
  #   node_labels = {
  #     balance-group = "User01ZonedPools"
  #   }
  #   node_taints          = [] #this is always blank for default node pool
  #   orchestrator_version = "1.34.7"
  #   os_disk_size_gb      = 150
  #   os_disk_type         = "Ephemeral"
  #   os_type              = "Linux"
  #   os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
  #   tags = {
  #     department                = "CGF"
  #     description               = "SCH-01-AKS Cluster"
  #     environment               = "nonprod"
  #     financialTag              = "H-######"
  #     serviceName               = "sch"
  #     spn                       = "pep-eiap-nonprod-k8s-sp"
  #     pep-cmdb-bus-app-id       = "327967b31be36010b050c992604bcbc8"
  #     pep-cmdb-bus-app-name     = "EIP AZURE KUBERNETES SERVICE"
  #     pep-cmdb-app-service-id   = "ea7967b31be36010b050c992604bcbc1"
  #     pep-cmdb-app-service-name = "EIP AZURE KUBERNETES SERVICE PROD"
  #   }
  #   max_surge                     = ["2"] #set this to [] if not using this property while AKS creation
  #   zones                         = [2]
  #   mode                          = "User"
  #   cluster_name                  = "pep-cgf-sch-nonprod-gwc-01-aks"
  #   cluster_resource_group_name   = "pep-cgf-sch-nonprod-gwc-k8s-01-rg"
  #   vnet_name                     = "pep-paas-europe-nonprod-gwc-01-vnet"
  #   snet_name                     = "pep-aks-global-01-subnet"
  #   vnet_snet_resource_group_name = "pep-network-non-prod-europe-gwc-01-rg"
  #   proximity_placement_group_id  = null
  # }
  # npu01z3 = {
  #   name                  = "npu01z3"
  #   vm_size               = "Standard_E16ds_v4"
  #   node_count            = 0
  #   enable_auto_scaling   = true
  #   enable_node_public_ip = false
  #   pod_max_pid           = ["4194304"]
  #   kubelet_disk_type     = "OS"
  #   max_count             = 3
  #   min_count             = 1
  #   max_pods              = "110"
  #   node_labels = {
  #     balance-group = "User01ZonedPools"
  #   }
  #   node_taints          = [] #this is always blank for default node pool
  #   orchestrator_version = "1.34.7"
  #   os_disk_size_gb      = 150
  #   os_disk_type         = "Ephemeral"
  #   os_type              = "Linux"
  #   os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
  #   tags = {
  #     department                = "CGF"
  #     description               = "SCH-01-AKS Cluster"
  #     environment               = "nonprod"
  #     financialTag              = "H-######"
  #     serviceName               = "sch"
  #     spn                       = "pep-eiap-nonprod-k8s-sp"
  #     pep-cmdb-bus-app-id       = "327967b31be36010b050c992604bcbc8"
  #     pep-cmdb-bus-app-name     = "EIP AZURE KUBERNETES SERVICE"
  #     pep-cmdb-app-service-id   = "ea7967b31be36010b050c992604bcbc1"
  #     pep-cmdb-app-service-name = "EIP AZURE KUBERNETES SERVICE PROD"
  #   }
  #   max_surge                     = ["2"] #set this to [] if not using this property while AKS creation
  #   zones                         = [3]
  #   mode                          = "User"
  #   cluster_name                  = "pep-cgf-sch-nonprod-gwc-01-aks"
  #   cluster_resource_group_name   = "pep-cgf-sch-nonprod-gwc-k8s-01-rg"
  #   vnet_name                     = "pep-paas-europe-nonprod-gwc-01-vnet"
  #   snet_name                     = "pep-aks-global-01-subnet"
  #   vnet_snet_resource_group_name = "pep-network-non-prod-europe-gwc-01-rg"
  #   proximity_placement_group_id  = null
  # }
  npb01z1 = {
    name                  = "npb01z1"
    vm_size               = "Standard_E8ds_v4"
    node_count            = 3
    enable_auto_scaling   = false
    enable_node_public_ip = false
    pod_max_pid           = ["4194304"]
    kubelet_disk_type     = "OS"
    max_count             = null
    min_count             = null
    max_pods              = "110"
    node_labels = {
      balance-group = "BuildAgentPools"

    }
    node_taints          = ["BuildAgentPool=Exists:NoSchedule"] #this is always blank for default node pool
    orchestrator_version = "1.34.7"
    os_disk_size_gb      = 150
    os_disk_type         = "Ephemeral"
    os_type              = "Linux"
    os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    tags = {
      department                = "pepgenx"
      description               = "pepgenx 2.0 Cluster"
      environment               = "nonprod"
      financialTag              = "H-######"
      serviceName               = "aisp-pepgenx"
      spn                       = "pep-eiap-nonprod-k8s-sp"
      pep-cmdb-bus-app-name       = "DAI PEPGENX"
      pep-cmdb-bus-app-id         = "7f0e42b8c3ba46d8b74985359901310f"
      pep-cmdb-app-service-name   = "DAI PEPGENX"
      pep-cmdb-app-service-id     = "841e42b8c3ba46d8b7498535990131f7"
    }
    max_surge                     = ["2"] #set this to [] if not using this property while AKS creation
    zones                         = [1]
    mode                          = "User"
    cluster_name                  = "pep-pepgenx-nonprod-eus-global-01-aks"
    cluster_resource_group_name   = "pep-azr-pepgenx2-dev-eus-01-rg"
    vnet_name                     = "pep-paas-azr-nonprod-pepgenx-01-eus-vnet"
    snet_name                     = "pep-aks-01-subnet"
    vnet_snet_resource_group_name = "pep-network-azr-nonprod-pepgenx-01-eus-rg"
    proximity_placement_group_id  = null
  }
  npargo01z1 = {
    name                  = "npargo01z1"
    vm_size               = "Standard_E4ds_v4"
    node_count            = 1
    enable_auto_scaling   = false
    enable_node_public_ip = false
    pod_max_pid           = ["4194304"]
    kubelet_disk_type     = "OS"
    max_count             = null
    min_count             = null
    max_pods              = "110"
    node_labels = {
      balance-group = "ArgoZonedPools"

    }
    node_taints          = ["ArgoZonedPools=Exists:NoSchedule"] #this is always blank for default node pool
    orchestrator_version = "1.34.7"
    os_disk_size_gb      = 150
    os_disk_type         = "Ephemeral"
    os_type              = "Linux"
    os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    tags = {
      department                = "pepgenx"
      description               = "pepgenx 2.0 Cluster"
      environment               = "nonprod"
      financialTag              = "H-######"
      serviceName               = "aisp-pepgenx"
      spn                       = "pep-eiap-nonprod-k8s-sp"
      pep-cmdb-bus-app-name       = "DAI PEPGENX"
      pep-cmdb-bus-app-id         = "7f0e42b8c3ba46d8b74985359901310f"
      pep-cmdb-app-service-name   = "DAI PEPGENX"
      pep-cmdb-app-service-id     = "841e42b8c3ba46d8b7498535990131f7"
    }
    max_surge                     = ["2"] #set this to [] if not using this property while AKS creation
    zones                         = [1]
    mode                          = "User"
    cluster_name                  = "pep-pepgenx-nonprod-eus-global-01-aks"
    cluster_resource_group_name   = "pep-azr-pepgenx2-dev-eus-01-rg"
    vnet_name                     = "pep-paas-azr-nonprod-pepgenx-01-eus-vnet"
    snet_name                     = "pep-aks-01-subnet"
    vnet_snet_resource_group_name = "pep-network-azr-nonprod-pepgenx-01-eus-rg"
    proximity_placement_group_id  = null
  }
  npargo01z2 = {
    name                  = "npargo01z2"
    vm_size               = "Standard_E4ds_v4"
    node_count            = 1
    enable_auto_scaling   = false
    enable_node_public_ip = false
    pod_max_pid           = ["4194304"]
    kubelet_disk_type     = "OS"
    max_count             = null
    min_count             = null
    max_pods              = "110"
    node_labels = {
      balance-group = "ArgoZonedPools"

    }
    node_taints          = ["ArgoZonedPools=Exists:NoSchedule"] #this is always blank for default node pool
    orchestrator_version = "1.34.7"
    os_disk_size_gb      = 150
    os_disk_type         = "Ephemeral"
    os_type              = "Linux"
    os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    tags = {
      department                = "pepgenx"
      description               = "pepgenx 2.0 Cluster"
      environment               = "nonprod"
      financialTag              = "H-######"
      serviceName               = "aisp-pepgenx"
      spn                       = "pep-eiap-nonprod-k8s-sp"
      pep-cmdb-bus-app-name       = "DAI PEPGENX"
      pep-cmdb-bus-app-id         = "7f0e42b8c3ba46d8b74985359901310f"
      pep-cmdb-app-service-name   = "DAI PEPGENX"
      pep-cmdb-app-service-id     = "841e42b8c3ba46d8b7498535990131f7"
    }
    max_surge                     = ["2"] #set this to [] if not using this property while AKS creation
    zones                         = [2]
    mode                          = "User"
    cluster_name                  = "pep-pepgenx-nonprod-eus-global-01-aks"
    cluster_resource_group_name   = "pep-azr-pepgenx2-dev-eus-01-rg"
    vnet_name                     = "pep-paas-azr-nonprod-pepgenx-01-eus-vnet"
    snet_name                     = "pep-aks-01-subnet"
    vnet_snet_resource_group_name = "pep-network-azr-nonprod-pepgenx-01-eus-rg"
    proximity_placement_group_id  = null
  }
  npargo01z3 = {
    name                  = "npargo01z3"
    vm_size               = "Standard_E4ds_v4"
    node_count            = 1
    enable_auto_scaling   = false
    enable_node_public_ip = false
    pod_max_pid           = ["4194304"]
    kubelet_disk_type     = "OS"
    max_count             = null
    min_count             = null
    max_pods              = "110"
    node_labels = {
      balance-group = "ArgoZonedPools"

    }
    node_taints          = ["ArgoZonedPools=Exists:NoSchedule"] #this is always blank for default node pool
    orchestrator_version = "1.34.7"
    os_disk_size_gb      = 150
    os_disk_type         = "Ephemeral"
    os_type              = "Linux"
    os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    tags = {
      department                = "pepgenx"
      description               = "pepgenx 2.0 Cluster"
      environment               = "nonprod"
      financialTag              = "H-######"
      serviceName               = "aisp-pepgenx"
      spn                       = "pep-eiap-nonprod-k8s-sp"
      pep-cmdb-bus-app-name       = "DAI PEPGENX"
      pep-cmdb-bus-app-id         = "7f0e42b8c3ba46d8b74985359901310f"
      pep-cmdb-app-service-name   = "DAI PEPGENX"
      pep-cmdb-app-service-id     = "841e42b8c3ba46d8b7498535990131f7"
    }
    max_surge                     = ["2"] #set this to [] if not using this property while AKS creation
    zones                         = [3]
    mode                          = "User"
    cluster_name                  = "pep-pepgenx-nonprod-eus-global-01-aks"
    cluster_resource_group_name   = "pep-azr-pepgenx2-dev-eus-01-rg"
    vnet_name                     = "pep-paas-azr-nonprod-pepgenx-01-eus-vnet"
    snet_name                     = "pep-aks-01-subnet"
    vnet_snet_resource_group_name = "pep-network-azr-nonprod-pepgenx-01-eus-rg"
    proximity_placement_group_id  = null   
  }
  napgdata01z1 = {
    name                  = "napgdata01z1"
    vm_size               = "Standard_D8ds_v5"
    node_count            = 1
    enable_auto_scaling   = false
    enable_node_public_ip = false
    pod_max_pid           = ["4194304"]
    kubelet_disk_type     = "OS"
    max_count             = 0
    min_count             = 0
    max_pods              = "110"
    node_labels = {
      balance-group = "APGData01ZonedPools"
    }
    node_taints          = ["APG01dataNodeOnly=Exists:NoSchedule"] #this is always blank for default node pool
    orchestrator_version = "1.34.7"
    os_disk_size_gb      = 256
    os_disk_type         = "Ephemeral"
    os_type              = "Linux"
    os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    tags = {
      department                = "pepgenx"
      description               = "pepgenx 2.0 Cluster"
      environment               = "nonprod"
      financialTag              = "H-######"
      serviceName               = "aisp-pepgenx"
      spn                       = "pep-eiap-nonprod-k8s-sp"
      pep-cmdb-bus-app-name       = "DAI PEPGENX"
      pep-cmdb-bus-app-id         = "7f0e42b8c3ba46d8b74985359901310f"
      pep-cmdb-app-service-name   = "DAI PEPGENX"
      pep-cmdb-app-service-id     = "841e42b8c3ba46d8b7498535990131f7"
    }
    max_surge                     = ["1"] #set this to [] if not using this property while AKS creation
    zones                         = [1]
    mode                          = "User"
    cluster_name                  = "pep-pepgenx-nonprod-eus-global-01-aks"
    cluster_resource_group_name   = "pep-azr-pepgenx2-dev-eus-01-rg"
    vnet_name                     = "pep-paas-azr-nonprod-pepgenx-01-eus-vnet"
    snet_name                     = "pep-aks-01-subnet"
    vnet_snet_resource_group_name = "pep-network-azr-nonprod-pepgenx-01-eus-rg"
    proximity_placement_group_id  = null
  }
  napgdata01z2 = {
    name                  = "napgdata01z2"
    vm_size               = "Standard_D8ds_v5"
    node_count            = 1
    enable_auto_scaling   = false
    enable_node_public_ip = false
    pod_max_pid           = ["4194304"]
    kubelet_disk_type     = "OS"
    max_count             = 0
    min_count             = 0
    max_pods              = "110"
    node_labels = {
      balance-group = "APGData01ZonedPools"
    }
    node_taints          = ["APG01dataNodeOnly=Exists:NoSchedule"] #this is always blank for default node pool
    orchestrator_version = "1.34.7"
    os_disk_size_gb      = 256
    os_disk_type         = "Ephemeral"
    os_type              = "Linux"
    os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    tags = {
      department                = "pepgenx"
      description               = "pepgenx 2.0 Cluster"
      environment               = "nonprod"
      financialTag              = "H-######"
      serviceName               = "aisp-pepgenx"
      spn                       = "pep-eiap-nonprod-k8s-sp"
      pep-cmdb-bus-app-name       = "DAI PEPGENX"
      pep-cmdb-bus-app-id         = "7f0e42b8c3ba46d8b74985359901310f"
      pep-cmdb-app-service-name   = "DAI PEPGENX"
      pep-cmdb-app-service-id     = "841e42b8c3ba46d8b7498535990131f7"
    }
    max_surge                     = ["1"] #set this to [] if not using this property while AKS creation
    zones                         = [2]
    mode                          = "User"
    cluster_name                  = "pep-pepgenx-nonprod-eus-global-01-aks"
    cluster_resource_group_name   = "pep-azr-pepgenx2-dev-eus-01-rg"
    vnet_name                     = "pep-paas-azr-nonprod-pepgenx-01-eus-vnet"
    snet_name                     = "pep-aks-01-subnet"
    vnet_snet_resource_group_name = "pep-network-azr-nonprod-pepgenx-01-eus-rg"
    proximity_placement_group_id  = null
  }
  napgdata01z3 = {
    name                  = "napgdata01z3"
    vm_size               = "Standard_D8ds_v5"
    node_count            = 1
    enable_auto_scaling   = false
    enable_node_public_ip = false
    pod_max_pid           = ["4194304"]
    kubelet_disk_type     = "OS"
    max_count             = 0
    min_count             = 0
    max_pods              = "110"
    node_labels = {
      balance-group = "APGData01ZonedPools"
    }
    node_taints          = ["APG01dataNodeOnly=Exists:NoSchedule"] #this is always blank for default node pool
    orchestrator_version = "1.34.7"
    os_disk_size_gb      = 256
    os_disk_type         = "Ephemeral"
    os_type              = "Linux"
    os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    tags = {
      department                = "pepgenx"
      description               = "pepgenx 2.0 Cluster"
      environment               = "nonprod"
      financialTag              = "H-######"
      serviceName               = "aisp-pepgenx"
      spn                       = "pep-eiap-nonprod-k8s-sp"
      pep-cmdb-bus-app-name       = "DAI PEPGENX"
      pep-cmdb-bus-app-id         = "7f0e42b8c3ba46d8b74985359901310f"
      pep-cmdb-app-service-name   = "DAI PEPGENX"
      pep-cmdb-app-service-id     = "841e42b8c3ba46d8b7498535990131f7"
    }
    max_surge                     = ["1"] #set this to [] if not using this property while AKS creation
    zones                         = [3]
    mode                          = "User"
    cluster_name                  = "pep-pepgenx-nonprod-eus-global-01-aks"
    cluster_resource_group_name   = "pep-azr-pepgenx2-dev-eus-01-rg"
    vnet_name                     = "pep-paas-azr-nonprod-pepgenx-01-eus-vnet"
    snet_name                     = "pep-aks-01-subnet"
    vnet_snet_resource_group_name = "pep-network-azr-nonprod-pepgenx-01-eus-rg"
    proximity_placement_group_id  = null
  }
  # npprom1z1 = {
  #   name                  = "npprom1z1"
  #   vm_size               = "Standard_E8ds_v4"
  #   node_count            = 1
  #   enable_auto_scaling   = true
  #   enable_node_public_ip = false
  #   pod_max_pid           = []
  #   kubelet_disk_type     = "OS"
  #   max_count             = 2
  #   min_count             = 1
  #   node_labels = {
  #     balance-group = "prometheus01ZonedPools"
  #   }
  #   node_taints          = ["Prometheus=Exists:NoSchedule"] #this is always blank for default node pool
  #   orchestrator_version = "1.34.7"
  #   os_disk_size_gb      = 128
  #   os_disk_type         = "Ephemeral"
  #   os_type              = "Linux"
  #   os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
  #   tags = {
  #     department                = "CGF"
  #     description               = "SCH-01-AKS Cluster"
  #     environment               = "nonprod"
  #     financialTag              = "H-######"
  #     serviceName               = "sch"
  #     spn                       = "pep-eiap-nonprod-k8s-sp"
  #     pep-cmdb-bus-app-id       = "327967b31be36010b050c992604bcbc8"
  #     pep-cmdb-bus-app-name     = "EIP AZURE KUBERNETES SERVICE"
  #     pep-cmdb-app-service-id   = "ea7967b31be36010b050c992604bcbc1"
  #     pep-cmdb-app-service-name = "EIP AZURE KUBERNETES SERVICE PROD"
  #   }
  #   max_surge                     = ["2"] #set this to [] if not using this property while AKS creation
  #   zones                         = [1]
  #   mode                          = "User"
  #   cluster_name                  = "pep-cgf-sch-nonprod-gwc-01-aks"
  #   cluster_resource_group_name   = "pep-cgf-sch-nonprod-gwc-k8s-01-rg"
  #   vnet_name                     = "pep-paas-europe-nonprod-gwc-01-vnet"
  #   snet_name                     = "pep-aks-global-01-subnet"
  #   vnet_snet_resource_group_name = "pep-network-non-prod-europe-gwc-01-rg"
  #   proximity_placement_group_id  = null
  # }  
}