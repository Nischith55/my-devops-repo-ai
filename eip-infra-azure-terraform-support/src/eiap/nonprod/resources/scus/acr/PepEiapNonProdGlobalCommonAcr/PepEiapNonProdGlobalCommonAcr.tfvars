container_registries = {
  PepEiapNonProdGlobalCommonAcr = {
    location                      = "southcentralus"
    resource_group_name           = "pep-eiap-nonprod-scus-paas-01-rg"
    sku                           = "Premium"
    admin_enabled                 = false
    data_endpoint_enabled         = false
    zone_redundancy_enabled       = false
    public_network_access_enabled = true
    network_rule_bypass_option    = "AzureServices"
    georeplications               = [] 
    retention_policy_enabled = ["true"] # specify as ["true"] to enable it
    retention_policy = {
      retention_policy_in_days = 5
      enabled                  = true
    }

    trust_policy_enabled = [] # specify as ["true"] to enable it
    trust_policy = {
      enabled = false
    }

    tags = {
      department   = "EIAP"
      description  = "EIAP Common Global NonProd Acr"
      environment  = "nonprod"
      financialTag = "H-######"
      serviceName  = "eip"
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
      default_action = "Deny"
      ip_rule = [
        {
          action   = "Allow"
          ip_range = "104.56.175.141/32"
        },
        {
          action   = "Allow"
          ip_range = "136.226.244.104/32"
        },
        {
          action   = "Allow"
          ip_range = "136.226.252.84/32"
        },
        {
          action   = "Allow"
          ip_range = "148.64.4.91/32"
        },
        {
          action   = "Allow"
          ip_range = "181.87.201.243/32"
        },
        {
          action   = "Allow"
          ip_range = "186.108.198.134/32"
        },
        {
          action   = "Allow"
          ip_range = "20.253.85.24/32"
        },
        {
          action   = "Allow"
          ip_range = "47.54.57.88/32"
        }
      ]
      virtual_network = []
    }
  }
}