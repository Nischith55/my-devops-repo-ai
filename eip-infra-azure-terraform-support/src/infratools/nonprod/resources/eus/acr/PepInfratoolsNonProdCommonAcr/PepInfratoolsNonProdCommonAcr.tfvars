container_registries = {
  PepInfratoolsNonProdCommonAcr = {
    location                      = "eastus"
    resource_group_name           = "pep-paas-infratools-nonprod-eus-paas-01-rg"
    sku                           = "Premium"
    admin_enabled                 = false
    data_endpoint_enabled         = false
    zone_redundancy_enabled       = false
    public_network_access_enabled = false
    network_rule_bypass_option    = "AzureServices"
    georeplications = []
    retention_policy_enabled      = [true]
    retention_policy = {
      retention_policy_in_days = 30
      enabled                  = false
    }

    tags = {
      CreateData  = "{\"User\": \"neipd999\", \"TimeStamp\": \"2023-09-22T11:21:40\", \"ExecuteHost\": \"pepsico-eip-global-devsecops-agent-batchjob-tgwfq-xzz7s\", \"build\": \"2089333\"}"
      department  = "infratools"
      description = "Infratools Common NonProd Acr"
      environment = "nonprod"
      financialTag = "H-######"
      serviceName = "eip"
    }

    identity_enabled = [] # specify as ["true"] to enable it
    identity = {
      type         = null
      identity_ids = [] #should be specified in brackets as it is a list
    }

    /*retention_policy_enabled      = [] # specify as ["true"] to enable it
    retention_policy = {
      retention_policy_in_days = 7
      enabled                  = false
    } */

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