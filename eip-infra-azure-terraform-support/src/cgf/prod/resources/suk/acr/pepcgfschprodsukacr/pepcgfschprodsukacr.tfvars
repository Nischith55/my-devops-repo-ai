container_registries = {
  pepcgfschprodsukacr = {
    location                      = "uksouth"
    resource_group_name           = "pep-cgf-sch-prod-suk-paas-01-rg"
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
      department   = "CGF"
      description  = "SCH SUK ACR"
      environment  = "prod"
      financialTag = "H-######"
      serviceName  = "sch"
      spn          = "pep-eiap-prod-k8s-sp"
      pep-cmdb-bus-app-id = "327967b31be36010b050c992604bcbc8"
      pep-cmdb-bus-app-name = "EIP AZURE KUBERNETES SERVICE"
      pep-cmdb-app-service-id = "ea7967b31be36010b050c992604bcbc1"
      pep-cmdb-app-service-name = "EIP AZURE KUBERNETES SERVICE PROD"

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