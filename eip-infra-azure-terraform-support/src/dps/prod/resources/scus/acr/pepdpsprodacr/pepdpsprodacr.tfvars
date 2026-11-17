container_registries = {
  pepdpsprodacr = {
    location                      = "southcentralus"
    resource_group_name           = "pep-dps-paas-prod-scus-01-rg"
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
      department     = "dps"
      environment    = "prod"
      financialTag   = "H-######"
      serviceName    = "dps-acr"
      spn            = "pep-eiap-nonprod-paas-sp"
      pep-cmdb-app-service-id   = "e7288b75c3047250476a900f050131ee" 
      pep-cmdb-app-service-name = "DSX_DEVOPS_PROD" 
      pep-cmdb-bus-app-id       = "f0624479c3cc7e107e0cfbdf050131fd"
      pep-cmdb-bus-app-name     = "DIGITAL SERVICES ACCELERATOR (DSX)"
      serviceName              = "dps-acr"
    }

    identity_enabled = [] # specify as ["true"] to enable it
    identity = {
      type         = null
      identity_ids = [] #should be specified in brackets as it is a list
    }

    network_rule_set = {
      default_action  = "Deny"
      ip_rule         = [
              ]
      virtual_network = []
    }

    trust_policy_enabled = [] # specify as ["true"] to enable it
    trust_policy = {
      enabled = false
    }

    georeplications = [
      {
        location = "uksouth"
        regional_endpoint_enabled = true
        zone_redundancy_enabled = true
      },
      {
        location = "southeastasia"
        regional_endpoint_enabled = true
        zone_redundancy_enabled = true
      }
    ]
  }
}

