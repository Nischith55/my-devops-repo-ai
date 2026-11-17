container_registries = {
  pepdpsnonprodacr = {
    location                      = "eastus"
    resource_group_name           = "pep-dps-paas-dev-eus-01-rg"
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
      department         = "dps"
      AzRegion           = "eastus"
      environment        = "nonprod"
      description        = "dps acr"
      financialTag       = "H-######"
      serviceName        = "dps-acr"
      spn                = "pep-eiap-nonprod-paas-sp"
      pep-cmdb-app-service-id   = "3D86f547f5838c3250f132cfefeeaad30d" 
      pep-cmdb-app-service-name = "DSX_DEVOPS_NON-PROD" 
      pep-cmdb-bus-app-id       = "f0624479c3cc7e107e0cfbdf050131fd"
      pep-cmdb-bus-app-name     = "DIGITAL SERVICES ACCELERATOR (DSX)"
      serviceName              = "dps-acr"
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
        ]
    }
  }
}