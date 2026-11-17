container_registries = {
  PepEiapProdCommonAcr = {
    location                      = "southcentralus"
    resource_group_name           = "pep-eiap-prod-scus-paas-01-rg"
    sku                           = "Premium"
    admin_enabled                 = false
    data_endpoint_enabled         = false
    zone_redundancy_enabled       = true
    public_network_access_enabled = true
    network_rule_bypass_option    = "AzureServices"
    
    retention_policy_enabled      = [true]
    retention_policy = {
      retention_policy_in_days = 30
      enabled                  = false
    }

    tags = {   
      department = "EIAP"
      environment = "prod"
      financialTag = "H-######"
      serviceName = "EIAP"
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

    network_rule_set = {
      default_action  = "Deny"
      ip_rule         = [
        {
          action = "Allow"
          ip_range = "106.76.194.217/32"
        },
        {
          action = "Allow"
          ip_range = "122.164.86.1/32"
        },
        {
          action = "Allow"
          ip_range = "148.64.4.117/32"
        },
        {
          action = "Allow"
          ip_range = "148.64.4.70/32"
        },
        {
          action = "Allow"
          ip_range = "49.37.132.225/32"
        },
        {
          action = "Allow"
          ip_range = "49.37.147.171/32"
        }
      ]
      virtual_network = []
    }

    trust_policy_enabled = [] # specify as ["true"] to enable it
    trust_policy = {
      enabled = false
    }

    georeplications = [
      {
        location = "southeastasia"
        regional_endpoint_enabled = true
        zone_redundancy_enabled = true
      },
      {
        location = "uksouth"
        regional_endpoint_enabled = true
        zone_redundancy_enabled = true
      }
    ]
  }
}

