container_registries = {
  PepEiapNonProdGlobalTestAcr = {
    location                      = "southcentralus"
    resource_group_name           = "pep-eiap-nonprod-scus-paas-01-rg"
    sku                           = "Premium"
    admin_enabled                 = false
    data_endpoint_enabled         = false
    zone_redundancy_enabled       = false
    public_network_access_enabled = true
    network_rule_bypass_option    = "AzureServices"
    georeplications               = [] 
    retention_policy_enabled      = [true]
    retention_policy = {
      retention_policy_in_days = 30
      enabled                  = false
    }

    tags = {
      
      department   = "EIAP"
      description  = "ACR for Testing"
      environment  = "nonprod"
      financialTag = "H-######"
      serviceName  = "EIAP"
      pep-cmdb-app-service-id   = "ea7967b31be36010b050c992604bcbc1" 
      pep-cmdb-app-service-name = "EIP AZURE KUBERNETES SERVICE PROD" 
      pep-cmdb-bus-app-id       = "327967b31be36010b050c992604bcbc8"
      pep-cmdb-bus-app-name     = "EIP AZURE KUBERNETES SERVICE"
      serviceName              = "EIAP"
      
    }

    identity_enabled = [] # specify as ["true"] to enable it
    identity = {
      type         = null
      identity_ids = [] #should be specified in brackets as it is a list
    }

    retention_policy_enabled      = ["true"] # specify as ["true"] to enable it
    retention_policy = {
      retention_policy_in_days = 30
      enabled                  = false
    }

    trust_policy_enabled = [] # specify as ["true"] to enable it
    trust_policy = {
      enabled = false
    }

    network_rule_set = {
      default_action = "Deny"
      ip_rule = [
        {
          action   = "Allow"
          ip_range = "168.149.152.104/32"
        },
        {
          action = "Allow"
          ip_range = "49.207.232.104/32"
        },
        {
          action   = "Allow"
          ip_range = "49.37.152.54/32"
        },
        {
          action   = "Allow"
          ip_range = "52.183.220.118/32"
        },
        {
          action   = "Allow"
          ip_range = "52.183.220.121/32"
        }
      ]
      virtual_network = []
    }
  }
}