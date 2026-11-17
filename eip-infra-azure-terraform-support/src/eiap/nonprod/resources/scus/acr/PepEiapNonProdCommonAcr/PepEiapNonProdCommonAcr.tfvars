container_registries = {
  PepEiapNonProdCommonAcr = {
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
      AzRegion           = "southcentralus"
      CreatedByUser      = "09261927"
      CreatedExecuteHost = "PEPWUL146726"
      CreatedTimeStamp   = "2020-06-24T22:11:33"
      Department         = "EIAP"
      Environment        = "nonprod"
      Module             = "ACR"
      Organization       = "CTO"
      SP                 = "pep-eiap-nonprod-paas-sp"
      costCenter         = "EIAP"
      department         = "EIAP"
      description        = "EIAP Common NonProd Acr"
      environment        = "nonprod"
      financialTag       = "H-######"
      sector             = "Global Implementation"
      serviceName        = "EIP"
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

    retention_policy_enabled      = [] # specify as ["true"] to enable it
    retention_policy = {
      retention_policy_in_days = 7
      enabled                  = false
    }

    trust_policy_enabled = [] # specify as ["true"] to enable it
    trust_policy = {
      enabled = false
    }
    
    network_rule_set = {
      default_action  = "Deny"
      virtual_network = []
      ip_rule = [
        {
            action   = "Allow"
            ip_range = "103.246.37.128/32"
        },
        {
            action   = "Allow"
            ip_range = "49.37.149.51/32"  
        }
        ]
    }
  }
}