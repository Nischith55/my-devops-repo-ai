container_registries = {
  pepnonprodeusoperationbridgeacr = {
    location                      = "eastus"
    resource_group_name           = "pep-operations-bridge-nonprod-eus-paas-01-rg"
    sku                           = "Premium"
    admin_enabled                 = false
    data_endpoint_enabled         = false
    zone_redundancy_enabled       = true
    public_network_access_enabled = false
    network_rule_bypass_option    = "AzureServices"
    georeplications = []
    retention_policy_enabled      = [true]
    retention_policy = {
      retention_policy_in_days = 7
      enabled                  = false
    }

    tags = {
      
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
      default_action  = "Allow"
      virtual_network = []
      ip_rule = [
       
        
        ]
    }
  }
}