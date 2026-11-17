node_pools = {
  nps01z1 = {
    name                  = "nps01z1"
    vm_size               = "Standard_E4ds_v4"
    node_count            = 1
    enable_auto_scaling   = true
    enable_node_public_ip = false
    pod_max_pid           = ["4194304"]
    kubelet_disk_type     = "OS"
    max_count             = 4
    min_count             = 1
    node_labels = {
      balance-group = "System01ZonedPools"
    }
    node_taints          = ["CriticalAddonsOnly=true:NoSchedule"] #this is always blank for default node pool
    orchestrator_version = "1.30.9"
    os_disk_size_gb      = 150
    os_disk_type         = "Ephemeral"
    os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    os_type              = "Linux"
    tags = {
      pep-cmdb-bus-app-id = "327967b31be36010b050c992604bcbc8"
      pep-cmdb-bus-app-name = "AISP AZURE KUBERNETES SERVICE"
      pep-cmdb-app-service-id = "ea7967b31be36010b050c992604bcbc1"
      pep-cmdb-app-service-name = "EIP AZURE KUBERNETES SERVICE PROD"
      department   = "EIAP"
      description  = "pep-eiap-nonprod-eus-sbox-03-aks"
      environment  = "nonprod"
      financialTag = "H-######"
      serviceName  = "eip"
      spn          = "pep-eiap-nonprod-k8s-sp"
    }
    max_surge                     = [] #set this to [] if not using this property while AKS creation
    zones                         = [1]
    mode                          = "System"
    cluster_name                  = "pep-eiap-nonprod-eus-sbox-03-aks"
    cluster_resource_group_name   = "pep-eiap-nonprod-eus-k8s-01-rg"
    vnet_name                     = "pep-eiap-nonprod-eus-network-01-vnet"
    snet_name                     = "pep-eiap-nonprod-eus-network-01-vnet-sbox-03-aks-01-snet"
    vnet_snet_resource_group_name = "pep-eiap-nonprod-eus-network-01-rg"
    proximity_placement_group_id  = null
  }
  npbp01 = {
    name                  = "npbp01"
    vm_size               = "Standard_E8ds_v4"
    node_count            = 0
    enable_auto_scaling   = true
    enable_node_public_ip = false
    pod_max_pid           = ["4194304"]
    kubelet_disk_type     = "OS"
    max_count             = 6
    min_count             = 0
    node_labels = {
      balance-group = "BuildAgentPools"
    }
    node_taints          = ["BuildAgentPool=Exists:NoSchedule"] #this is always blank for default node pool
    orchestrator_version = "1.31.7"
    os_disk_size_gb      = 200
    os_disk_type         = "Ephemeral"
    os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    os_type              = "Linux"
    tags = {
      pep-cmdb-bus-app-id = "327967b31be36010b050c992604bcbc8"
      pep-cmdb-bus-app-name = "AISP AZURE KUBERNETES SERVICE"
      pep-cmdb-app-service-id = "ea7967b31be36010b050c992604bcbc1"
      pep-cmdb-app-service-name = "EIP AZURE KUBERNETES SERVICE PROD"
      department   = "EIAP"
      description  = "pep-eiap-nonprod-eus-sbox-03-aks"
      environment  = "nonprod"
      financialTag = "H-######"
      serviceName  = "eip"
      spn          = "pep-eiap-nonprod-k8s-sp"
    }
    max_surge                     = [] #set this to [] if not using this property while AKS creation
    zones                         = []
    mode                          = "User"
    cluster_name                  = "pep-eiap-nonprod-eus-sbox-03-aks"
    cluster_resource_group_name   = "pep-eiap-nonprod-eus-k8s-01-rg"
    vnet_name                     = "pep-eiap-nonprod-eus-network-01-vnet"
    snet_name                     = "pep-eiap-nonprod-eus-network-01-vnet-sbox-03-aks-01-snet"
    vnet_snet_resource_group_name = "pep-eiap-nonprod-eus-network-01-rg"
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
    min_count             = 1
    node_labels = {
      balance-group = "User01ZonedPools"
    }
    node_taints          = [] #this is always blank for default node pool
    orchestrator_version = "1.31.7"
    os_disk_size_gb      = 100
    os_disk_type         = "Ephemeral"
    os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    os_type              = "Linux"
    tags = {
      pep-cmdb-bus-app-id = "327967b31be36010b050c992604bcbc8"
      pep-cmdb-bus-app-name = "AISP AZURE KUBERNETES SERVICE"
      pep-cmdb-app-service-id = "ea7967b31be36010b050c992604bcbc1"
      pep-cmdb-app-service-name = "EIP AZURE KUBERNETES SERVICE PROD"
      department   = "EIAP"
      description  = "pep-eiap-nonprod-eus-sbox-03-aks"
      environment  = "nonprod"
      financialTag = "H-######"
      serviceName  = "eip"
      spn          = "pep-eiap-nonprod-k8s-sp"
    }
    max_surge                     = [] #set this to [] if not using this property while AKS creation
    zones                         = [1]
    mode                          = "User"
    cluster_name                  = "pep-eiap-nonprod-eus-sbox-03-aks"
    cluster_resource_group_name   = "pep-eiap-nonprod-eus-k8s-01-rg"
    vnet_name                     = "pep-eiap-nonprod-eus-network-01-vnet"
    snet_name                     = "pep-eiap-nonprod-eus-network-01-vnet-sbox-03-aks-01-snet"
    vnet_snet_resource_group_name = "pep-eiap-nonprod-eus-network-01-rg"
    proximity_placement_group_id  = null
  }
  npu01z2 = {
    name                  = "npu01z2"
    vm_size               = "Standard_E16ds_v4"
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
    orchestrator_version = "1.31.7"
    os_disk_size_gb      = 256
    os_disk_type         = "Ephemeral"
    os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    os_type              = "Linux"
    tags = {
      pep-cmdb-bus-app-id = "327967b31be36010b050c992604bcbc8"
      pep-cmdb-bus-app-name = "AISP AZURE KUBERNETES SERVICE"
      pep-cmdb-app-service-id = "ea7967b31be36010b050c992604bcbc1"
      pep-cmdb-app-service-name = "EIP AZURE KUBERNETES SERVICE PROD"
      department   = "EIAP"
      description  = "pep-eiap-nonprod-eus-sbox-03-aks"
      environment  = "nonprod"
      financialTag = "H-######"
      serviceName  = "eip"
      spn          = "pep-eiap-nonprod-k8s-sp"
    }
    max_surge                     = [] #set this to [] if not using this property while AKS creation
    zones                         = [2]
    mode                          = "User"
    cluster_name                  = "pep-eiap-nonprod-eus-sbox-03-aks"
    cluster_resource_group_name   = "pep-eiap-nonprod-eus-k8s-01-rg"
    vnet_name                     = "pep-eiap-nonprod-eus-network-01-vnet"
    snet_name                     = "pep-eiap-nonprod-eus-network-01-vnet-sbox-03-aks-01-snet"
    vnet_snet_resource_group_name = "pep-eiap-nonprod-eus-network-01-rg"
    proximity_placement_group_id  = null
  }
  
  npu01z3 = {
    name                  = "npu01z3"
    vm_size               = "Standard_E16ds_v4"
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
    orchestrator_version = "1.30.9"
    os_disk_size_gb      = 100
    os_disk_type         = "Ephemeral"
    os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    os_type              = "Linux"
    tags = {
      pep-cmdb-bus-app-id = "327967b31be36010b050c992604bcbc8"
      pep-cmdb-bus-app-name = "AISP AZURE KUBERNETES SERVICE"
      pep-cmdb-app-service-id = "ea7967b31be36010b050c992604bcbc1"
      pep-cmdb-app-service-name = "EIP AZURE KUBERNETES SERVICE PROD"
      department   = "EIAP"
      description  = "pep-eiap-nonprod-eus-sbox-03-aks"
      environment  = "nonprod"
      financialTag = "H-######"
      serviceName  = "eip"
      spn          = "pep-eiap-nonprod-k8s-sp"
    }
    max_surge                     = ["2"] #set this to [] if not using this property while AKS creation
    zones                         = [3]
    mode                          = "User"
    cluster_name                  = "pep-eiap-nonprod-eus-sbox-03-aks"
    cluster_resource_group_name   = "pep-eiap-nonprod-eus-k8s-01-rg"
    vnet_name                     = "pep-eiap-nonprod-eus-network-01-vnet"
    snet_name                     = "pep-eiap-nonprod-eus-network-01-vnet-sbox-03-aks-01-snet"
    vnet_snet_resource_group_name = "pep-eiap-nonprod-eus-network-01-rg"
    proximity_placement_group_id  = null
  }
  napgrt01z2 = {
    name                  = "napgrt01z2"
    vm_size               = "Standard_E16ds_v4"
    node_count            = 0
    enable_auto_scaling   = true
    enable_node_public_ip = false
    pod_max_pid           = ["4194304"]
    kubelet_disk_type     = "OS"
    max_count             = 1
    min_count             = 0
    node_labels = {
      balance-group = "APGRuntime01ZonedPools"
    }
    node_taints          = ["APG01RuntimeNodeOnly=Exists:NoSchedule"] #this is always blank for default node pool
    orchestrator_version = "1.30.9"
    os_disk_size_gb      = 256
    os_disk_type         = "Ephemeral"
    os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    os_type              = "Linux"
    tags = {
      "department": "apigee",
      "description": "Apigee Test ORG",
      "environment": "nonprod",
      "financialTag": "H-######",
      "pep-cmdb-app-service-id": "ea7967b31be36010b050c992604bcbc1",
      "pep-cmdb-app-service-name": "EIP AZURE KUBERNETES SERVICE PROD",
      "pep-cmdb-bus-app-id": "327967b31be36010b050c992604bcbc8",
      "pep-cmdb-bus-app-name": "AISP AZURE KUBERNETES SERVICE",
      "serviceName": "eip",
      "spn": "pep-eiap-nonprod-k8s-sp"
    }
    max_surge                     = [] #set this to [] if not using this property while AKS creation
    zones                         = [1]
    mode                          = "User"
    cluster_name                  = "pep-eiap-nonprod-eus-sbox-03-aks"
    cluster_resource_group_name   = "pep-eiap-nonprod-eus-k8s-01-rg"
    vnet_name                     = "pep-eiap-nonprod-eus-network-01-vnet"
    snet_name                     = "pep-eiap-nonprod-eus-network-01-vnet-sbox-03-aks-01-snet"
    vnet_snet_resource_group_name = "pep-eiap-nonprod-eus-network-01-rg"
    proximity_placement_group_id  = null
  }
  napgdata01z1 = {
    name                  = "napgdata01z1"
    vm_size               = "Standard_D2ds_v4"
    node_count            = 0
    enable_auto_scaling   = true
    enable_node_public_ip = false
    pod_max_pid           = ["4194304"]
    kubelet_disk_type     = "OS"
    max_count             = 1
    min_count             = 0
    node_labels = {
      balance-group = "APGData01ZonedPools"
    }
    node_taints          = ["APG01dataNodeOnly=Exists:NoSchedule"] #this is always blank for default node pool
    orchestrator_version = "1.30.9"
    os_disk_size_gb      = 50
    os_disk_type         = "Ephemeral"
    os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    os_type              = "Linux"
    tags = {
      "department": "apigee",
      "description": "Apigee Test ORG",
      "environment": "nonprod",
      "financialTag": "H-######",
      "pep-cmdb-app-service-id": "ea7967b31be36010b050c992604bcbc1",
      "pep-cmdb-app-service-name": "EIP AZURE KUBERNETES SERVICE PROD",
      "pep-cmdb-bus-app-id": "327967b31be36010b050c992604bcbc8",
      "pep-cmdb-bus-app-name": "AISP AZURE KUBERNETES SERVICE",
      "serviceName": "eip",
      "spn": "pep-eiap-nonprod-k8s-sp"
    }
    max_surge                     = [] #set this to [] if not using this property while AKS creation
    zones                         = [1]
    mode                          = "User"
    cluster_name                  = "pep-eiap-nonprod-eus-sbox-03-aks"
    cluster_resource_group_name   = "pep-eiap-nonprod-eus-k8s-01-rg"
    vnet_name                     = "pep-eiap-nonprod-eus-network-01-vnet"
    snet_name                     = "pep-eiap-nonprod-eus-network-01-vnet-sbox-03-aks-01-snet"
    vnet_snet_resource_group_name = "pep-eiap-nonprod-eus-network-01-rg"
    proximity_placement_group_id  = null
  }
  npdatastx1z2 = {
    name                  = "npdatastx1z2"
    vm_size               = "Standard_E4ds_v4"
    node_count            = 0
    enable_auto_scaling   = true
    enable_node_public_ip = false
    kubelet_disk_type     = "OS"
    max_count             = 3
    pod_max_pid           = ["4194304"]
    min_count             = 0
    node_labels = {
      "balance-group": "DataStaxPoolsDB",
      "mission-control.datastax.com/role": "database"
    }
    node_taints          = ["DataStaxPool=Exists:NoSchedule"] #this is always blank for default node pool
    orchestrator_version = "1.30.9"
    os_disk_size_gb      = 128
    os_disk_type         = "Ephemeral"
    os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    os_type              = "Linux"
    tags = {
      "department": "EIAP",
      "description": "pep-eiap-nonprod-eus-sbox-03-aks",
      "environment": "nonprod",
      "financialTag": "H-######",
      "pep-cmdb-app-service-id": "ea7967b31be36010b050c992604bcbc1",
      "pep-cmdb-app-service-name": "EIP AZURE KUBERNETES SERVICE PROD",
      "pep-cmdb-bus-app-id": "327967b31be36010b050c992604bcbc8",
      "pep-cmdb-bus-app-name": "AISP AZURE KUBERNETES SERVICE",
      "serviceName": "eip",
      "spn": "pep-eiap-nonprod-k8s-sp"
    }
    max_surge                     = [] #set this to [] if not using this property while AKS creation
    zones                         = [1,2,3]
    mode                          = "User"
    cluster_name                  = "pep-eiap-nonprod-eus-sbox-03-aks"
    cluster_resource_group_name   = "pep-eiap-nonprod-eus-k8s-01-rg"
    vnet_name                     = "pep-eiap-nonprod-eus-network-01-vnet"
    snet_name                     = "pep-eiap-nonprod-eus-network-01-vnet-sbox-03-aks-01-snet"
    vnet_snet_resource_group_name = "pep-eiap-nonprod-eus-network-01-rg"
    proximity_placement_group_id  = null
    // temporary_name_for_rotation = "npz2tmp"
  }
  npdatastx1z1 = {
    name                  = "npdatastx1z1"
    vm_size               = "Standard_E4ds_v4"
    node_count            = 0
    enable_auto_scaling   = true
    enable_node_public_ip = false
    kubelet_disk_type     = "OS"
    max_count             = 3
    pod_max_pid           = ["4194304"]
    min_count             = 0
    node_labels = {
      "balance-group": "DataStaxPools",
      "mission-control.datastax.com/role": "platform"
    }
    node_taints          = ["DataStaxPool=Exists:NoSchedule"] #this is always blank for default node pool
    orchestrator_version = "1.30.9"
    os_disk_size_gb      = 128
    os_disk_type         = "Ephemeral"
    os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    os_type              = "Linux"
    tags = {
      "department": "EIAP",
      "description": "pep-eiap-nonprod-eus-sbox-03-aks",
      "environment": "nonprod",
      "financialTag": "H-######",
      "pep-cmdb-app-service-id": "ea7967b31be36010b050c992604bcbc1",
      "pep-cmdb-app-service-name": "EIP AZURE KUBERNETES SERVICE PROD",
      "pep-cmdb-bus-app-id": "327967b31be36010b050c992604bcbc8",
      "pep-cmdb-bus-app-name": "AISP AZURE KUBERNETES SERVICE",
      "serviceName": "eip",
      "spn": "pep-eiap-nonprod-k8s-sp"
    }
    max_surge                     = [] #set this to [] if not using this property while AKS creation
    zones                         = [1,2,3]
    mode                          = "User"
    cluster_name                  = "pep-eiap-nonprod-eus-sbox-03-aks"
    cluster_resource_group_name   = "pep-eiap-nonprod-eus-k8s-01-rg"
    vnet_name                     = "pep-eiap-nonprod-eus-network-01-vnet"
    snet_name                     = "pep-eiap-nonprod-eus-network-01-vnet-sbox-03-aks-01-snet"
    vnet_snet_resource_group_name = "pep-eiap-nonprod-eus-network-01-rg"
    proximity_placement_group_id  = null
  }
  npprom1z1 = {
    name                  = "npprom1z1"
    vm_size               = "Standard_E8ds_v4"
    node_count            = 0
    enable_auto_scaling   = true
    enable_node_public_ip = false
    pod_max_pid           = ["4194304"]
    kubelet_disk_type     = "OS"
    max_count             = 2
    min_count             = 0
    node_labels = {
      "balance-group": "prometheus01ZonedPools"
    }
    node_taints          = ["Prometheus=Exists:NoSchedule"] #this is always blank for default node pool
    orchestrator_version = "1.30.9"
    os_disk_size_gb      = 128
    os_disk_type         = "Ephemeral"
    os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    os_type              = "Linux"
    tags = {
      "department": "Prometheus",
      "description": "Prometheus Test ORG",
      "environment": "nonprod",
      "financialTag": "H-######",
      "pep-cmdb-app-service-id": "ea7967b31be36010b050c992604bcbc1",
      "pep-cmdb-app-service-name": "EIP AZURE KUBERNETES SERVICE PROD",
      "pep-cmdb-bus-app-id": "327967b31be36010b050c992604bcbc8",
      "pep-cmdb-bus-app-name": "AISP AZURE KUBERNETES SERVICE",
      "serviceName": "eip",
      "spn": "pep-eiap-nonprod-k8s-sp"
    }
    max_surge                     = [] #set this to [] if not using this property while AKS creation
    zones                         = [1]
    mode                          = "User"
    cluster_name                  = "pep-eiap-nonprod-eus-sbox-03-aks"
    cluster_resource_group_name   = "pep-eiap-nonprod-eus-k8s-01-rg"
    vnet_name                     = "pep-eiap-nonprod-eus-network-01-vnet"
    snet_name                     = "pep-eiap-nonprod-eus-network-01-vnet-sbox-03-aks-01-snet"
    vnet_snet_resource_group_name = "pep-eiap-nonprod-eus-network-01-rg"
    proximity_placement_group_id  = null
  }
  npchbase1z1 = {
    name                  = "npchbase1z1"
    vm_size               = "Standard_E4ds_v4"
    node_count            = 0
    enable_auto_scaling   = true
    enable_node_public_ip = false
    pod_max_pid           = ["4194304"]
    kubelet_disk_type     = "OS"
    max_count             = 4
    min_count             = 0
    node_labels = {
      "balance-group": "Couchbase01ZonedPools"
    }
    node_taints          = ["Couchbase01NodeOnly=Exists:NoSchedule"] #this is always blank for default node pool
    orchestrator_version = "1.30.9"
    os_disk_size_gb      = 128
    os_disk_type         = "Ephemeral"
    os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    os_type              = "Linux"
    tags = {
      "department": "couchbase",
      "description": "couchbase Test ORG",
      "environment": "nonprod",
      "financialTag": "H-######",
      "pep-cmdb-app-service-id": "ea7967b31be36010b050c992604bcbc1",
      "pep-cmdb-app-service-name": "EIP AZURE KUBERNETES SERVICE PROD",
      "pep-cmdb-bus-app-id": "327967b31be36010b050c992604bcbc8",
      "pep-cmdb-bus-app-name": "AISP AZURE KUBERNETES SERVICE",
      "serviceName": "eip",
      "spn": "pep-eiap-nonprod-k8s-sp"
    }
    max_surge                     = [] #set this to [] if not using this property while AKS creation
    zones                         = [1]
    mode                          = "User"
    cluster_name                  = "pep-eiap-nonprod-eus-sbox-03-aks"
    cluster_resource_group_name   = "pep-eiap-nonprod-eus-k8s-01-rg"
    vnet_name                     = "pep-eiap-nonprod-eus-network-01-vnet"
    snet_name                     = "pep-eiap-nonprod-eus-network-01-vnet-sbox-03-aks-01-snet"
    vnet_snet_resource_group_name = "pep-eiap-nonprod-eus-network-01-rg"
    proximity_placement_group_id  = null
  }
  napgrt01z1 = {
    name                  = "napgrt01z1"
    vm_size               = "Standard_D4ds_v4"
    node_count            = 0
    enable_auto_scaling   = true
    enable_node_public_ip = false
    pod_max_pid           = ["4194304"]
    kubelet_disk_type     = "OS"
    max_count             = 1
    min_count             = 0
    node_labels = {
      "balance-group": "APGRuntime01ZonedPools"
    }
    node_taints          = ["APG01RuntimeNodeOnly=Exists:NoSchedule"] #this is always blank for default node pool
    orchestrator_version = "1.30.9"
    os_disk_size_gb      = 128
    os_disk_type         = "Ephemeral"
    os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    os_type              = "Linux"
    tags = {
      "department": "apigee",
      "description": "Apigee Test ORG",
      "environment": "nonprod",
      "financialTag": "H-######",
      "pep-cmdb-app-service-id": "ea7967b31be36010b050c992604bcbc1",
      "pep-cmdb-app-service-name": "EIP AZURE KUBERNETES SERVICE PROD",
      "pep-cmdb-bus-app-id": "327967b31be36010b050c992604bcbc8",
      "pep-cmdb-bus-app-name": "AISP AZURE KUBERNETES SERVICE",
      "serviceName": "eip",
      "spn": "pep-eiap-nonprod-k8s-sp"
    }
    max_surge                     = [] #set this to [] if not using this property while AKS creation
    zones                         = [1]
    mode                          = "User"
    cluster_name                  = "pep-eiap-nonprod-eus-sbox-03-aks"
    cluster_resource_group_name   = "pep-eiap-nonprod-eus-k8s-01-rg"
    vnet_name                     = "pep-eiap-nonprod-eus-network-01-vnet"
    snet_name                     = "pep-eiap-nonprod-eus-network-01-vnet-sbox-03-aks-01-snet"
    vnet_snet_resource_group_name = "pep-eiap-nonprod-eus-network-01-rg"
    proximity_placement_group_id  = null
  }
  napgcomp01z1 = {
    name                  = "napgcomp01z1"
    vm_size               = "Standard_D4ds_v4"
    node_count            = 0
    enable_auto_scaling   = true
    enable_node_public_ip = false
    pod_max_pid           = ["4194304"]
    kubelet_disk_type     = "OS"
    max_count             = 1
    min_count             = 0
    node_labels = {
      "balance-group": "APGComp01ZonedPools"
    }
    node_taints          = ["APGComp01NodeOnly=Exists:NoSchedule"] #this is always blank for default node pool
    orchestrator_version = "1.30.9"
    os_disk_size_gb      = 128
    os_disk_type         = "Ephemeral"
    os_sku               = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    os_type              = "Linux"
    tags = {
      "department": "apigee",
      "description": "Apigee Test ORG",
      "environment": "nonprod",
      "financialTag": "H-######",
      "pep-cmdb-app-service-id": "ea7967b31be36010b050c992604bcbc1",
      "pep-cmdb-app-service-name": "EIP AZURE KUBERNETES SERVICE PROD",
      "pep-cmdb-bus-app-id": "327967b31be36010b050c992604bcbc8",
      "pep-cmdb-bus-app-name": "AISP AZURE KUBERNETES SERVICE",
      "serviceName": "eip",
      "spn": "pep-eiap-nonprod-k8s-sp"
    }
    max_surge                     = [] #set this to [] if not using this property while AKS creation
    zones                         = [1]
    mode                          = "User"
    cluster_name                  = "pep-eiap-nonprod-eus-sbox-03-aks"
    cluster_resource_group_name   = "pep-eiap-nonprod-eus-k8s-01-rg"
    vnet_name                     = "pep-eiap-nonprod-eus-network-01-vnet"
    snet_name                     = "pep-eiap-nonprod-eus-network-01-vnet-sbox-03-aks-01-snet"
    vnet_snet_resource_group_name = "pep-eiap-nonprod-eus-network-01-rg"
    proximity_placement_group_id  = null
  }
}
