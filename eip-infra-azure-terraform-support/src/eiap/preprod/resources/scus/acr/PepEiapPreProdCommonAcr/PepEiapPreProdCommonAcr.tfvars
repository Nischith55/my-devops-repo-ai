container_registries = {
  PepEiapPreProdCommonAcr = {
    location                      = "southcentralus"
    resource_group_name           = "pep-eiap-preprod-scus-paas-01-rg"
    sku                           = "Premium"
    admin_enabled                 = false
    data_endpoint_enabled         = false
    zone_redundancy_enabled       = false
    public_network_access_enabled = false
    network_rule_bypass_option    = "AzureServices"
    georeplications               = [] 
    retention_policy_enabled      = [true]
    retention_policy = {
      retention_policy_in_days = 30
      enabled                  = false
    }

    tags = {
      department   = "EIAP"
      description  = "EIAP preprod Acr"
      environment  = "preprod"
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

    trust_policy_enabled = [] # specify as ["true"] to enable it
    trust_policy = {
      enabled = false
    }

    network_rule_set = {
      default_action = "Allow"
      ip_rule = [
        {
          action   = "Allow"
          ip_range = "165.197.0.0/16"
        },
        {
          action   = "Allow"
          ip_range = "165.198.0.0/16"
        },
        {
          action   = "Allow"
          ip_range = "28.0.0.0/8"
        }
      ]
      virtual_network = []
    }
  }
}