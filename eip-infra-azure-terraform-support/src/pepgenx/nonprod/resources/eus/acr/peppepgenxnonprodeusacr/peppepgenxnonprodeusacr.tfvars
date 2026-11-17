container_registries = {
  peppepgenxnonprodeusacr = {
    location                      = "eastus"
    resource_group_name           = "pep-azr-pepgenx2-shared-dev-eus-01-rg"
    sku                           = "Premium"
    admin_enabled                 = false
    data_endpoint_enabled         = false
    zone_redundancy_enabled       = true
    public_network_access_enabled = false
    network_rule_bypass_option    = "None"
    georeplications = []
    retention_policy_enabled      = [true]
    retention_policy = {
      retention_policy_in_days = 7
      enabled                  = false
    }

    tags = {
      department   = "pepgenx"
      description  = "pepgenx nonprod AKS ACR"
      environment  = "nonprod"
      financialTag = "H-######"
      serviceName  = "aisp-pepgenx"
      spn          = "pep-eiap-nonprod-k8s-sp"
      pep-cmdb-bus-app-id = "7f0e42b8c3ba46d8b74985359901310f"
      pep-cmdb-bus-app-name = "DAI PEPGENX"
      pep-cmdb-app-service-id = "841e42b8c3ba46d8b7498535990131f7"
      pep-cmdb-app-service-name = "DAI PEPGENX"

    }

    identity_enabled = [] # specify as ["true"] to enable it
    identity = {
      type         = null
      identity_ids = [] #should be specified in brackets as it is a list
    }

    /* retention_policy_enabled      = [] # specify as ["true"] to enable it
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