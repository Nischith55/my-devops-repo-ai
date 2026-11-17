container_registries = {
  peppfnanonprodhhnextacr = {
    location                      = "eastus"
    resource_group_name           = "pep-pfna-nonprod-eus-paas-01-rg"
    sku                           = "Premium"
    admin_enabled                 = false
    data_endpoint_enabled         = false
    zone_redundancy_enabled       = true
    public_network_access_enabled = true
    network_rule_bypass_option    = "AzureServices"
    georeplications = []
    retention_policy_enabled      = [true]
    retention_policy = {
      retention_policy_in_days = 7
      enabled                  = false
    }

    tags = {
      environment = "nonprod"
      serviceName = "och-hhnext"
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
       {
          "action": "Allow",
          "ip_range": "103.246.37.128/32"
        },
        {
          "action": "Allow",
          "ip_range": "122.171.18.0/32"
        },
        {
          "action": "Allow",
          "ip_range": "122.171.23.176/32"
        },
        {
          "action": "Allow",
          "ip_range": "134.41.84.233/32"
        },
        {
          "action": "Allow",
          "ip_range": "165.197.181.224/27"
        },
        {
          "action": "Allow",
          "ip_range": "165.197.216.224/27"
        },
        {
          "action": "Allow",
          "ip_range": "165.197.220.224/27"
        },
        {
          "action": "Allow",
          "ip_range": "165.197.64.224/27"
        },
        {
          "action": "Allow",
          "ip_range": "165.197.73.224/27"
        },
        {
          "action": "Allow",
          "ip_range": "183.83.235.44/32"
        },
        {
          "action": "Allow",
          "ip_range": "49.37.149.51/32"
        },
        {
          "action": "Allow",
          "ip_range": "99.245.195.206/32"
        } 
        ]
    }
  }
}