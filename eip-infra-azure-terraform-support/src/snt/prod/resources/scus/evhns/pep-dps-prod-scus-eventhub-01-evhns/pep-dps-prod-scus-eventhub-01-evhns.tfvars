evhns_ids = {
  pep-dps-prod-scus-eventhub-01-evhns = {
    name                          = "pep-dps-prod-scus-eventhub-01-evhns"
    location                      = "southcentralus"
    resource_group_name           = "pep-snt-b2bso-prod-scus-01-rg"
    sku                           = "Standard"
    capacity                      = 1
    auto_inflate_enabled          = false
    local_authentication_enabled  = true
    maximum_throughput_units      = 0
    minimum_tls_version           = "1.2"
    public_network_access_enabled = false
    tags = {
      #AzRegion = "eastus"
      #CreateData = "{\"ExecuteHost\": \"PEPWUL146726\", \"TimeStamp\": \"2020-11-24T16:57:26\", \"User\": \"09261927\"}"
      #Environment = "nonprod"
      #Module = "EventHub Namespace"
      #financialTag = "H-######"
      #serviceName = "EIAP"
    }
    dedicated_cluster_id = null  # specify the cluster id within "" to use this property
    zone_redundant       = true # default value
    identity_enabled     = []    # specify as true within "" if the property is to be used
    identity = {
      type         = null
      identity_ids = [] #should be specified in brackets as it is a list
    }

    network_rulesets_enabled = [] # specify as true within "" if the property is to be used
    network_rulesets = {
      default_action                 = "Allow"
      public_network_access_enabled  = false
      trusted_service_access_enabled = true
      ip_rule                        = []
      virtual_network_rule           = []
    }
  }
}