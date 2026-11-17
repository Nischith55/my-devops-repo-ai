container_registries = {
  PepEiapNonProdFlnaCouchbaseAcr = {
    location                      = "southcentralus"
    resource_group_name           = "pep-eiap-nonprod-scus-paas-01-rg"
    sku                           = "Premium"
    admin_enabled                 = true
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
      CreateData   = "{\"ExecuteHost\": \"INPC18PADJ\", \"TimeStamp\": \"2021-04-16T18:15:47\", \"User\": \"80213871\"}"
      department   = "EIAP"
      description  = "ACR for FLNA Couchbase"
      environment  = "nonprod"
      financialTag = "H-######"
      serviceName  = "EIAP"
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
      default_action  = "Allow"
      ip_rule         = []
      virtual_network = []
    }
  }
}