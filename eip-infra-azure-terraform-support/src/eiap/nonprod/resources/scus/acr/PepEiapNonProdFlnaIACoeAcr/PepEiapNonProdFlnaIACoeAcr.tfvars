container_registries = {
  PepEiapNonProdFlnaIACoeAcr = {
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
      AzRegion           = "southcentralus"
      CreatedByUser      = "80213871"
      CreatedExecuteHost = "INPC18PADJ"
      CreatedTimeStamp   = "2020-10-19T19:10:01"
      Environment        = "nonprod"
      ModifiedData       = "{\"ExecuteHost\": \"INPC1F23KR\", \"TimeStamp\": \"2022-04-01T13:56:15\", \"User\": \"chaitanya\"}"
      Module             = "ACR"
      SP                 = "pep-eiap-nonprod-paas-sp"
      department         = "EIAP"
      description        = "EIAP NonProd FLNA IACOE Acr"
      environment        = "nonprod"
      financialTag       = "H-######"
      serviceName        = "EIAP"
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
      ip_rule         = []
      virtual_network = []
    }
  }
}