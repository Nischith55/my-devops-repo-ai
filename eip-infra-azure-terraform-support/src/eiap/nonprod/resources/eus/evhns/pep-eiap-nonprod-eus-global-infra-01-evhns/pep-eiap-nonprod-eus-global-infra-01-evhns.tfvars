evhns_ids = {
  pep-eiap-nonprod-eus-global-infra-01-evhns = {
    name                          = "pep-eiap-nonprod-eus-global-infra-01-evhns"
    location                      = "eastus"
    resource_group_name           = "pep-eiap-nonprod-eus-paas-01-rg"
    sku                           = "Standard"
    capacity                      = 10
    auto_inflate_enabled          = true
    local_authentication_enabled  = true
    maximum_throughput_units      = 10
    minimum_tls_version           = "1.0"
    public_network_access_enabled = true
    tags = {
      AzRegion = "eastus"
      CreateData = "{\"ExecuteHost\": \"PEPWUL146726\", \"TimeStamp\": \"2020-11-24T16:57:26\", \"User\": \"09261927\"}"
      Environment = "nonprod"
      Module = "EventHub Namespace"
      financialTag = "H-######"
      serviceName = "EIAP"
    }
    dedicated_cluster_id = null  # specify the cluster id within "" to use this property
    zone_redundant       = false # default value
    identity_enabled     = []    # specify as true within "" if the property is to be used
    identity = {
      type         = null
      identity_ids = [] #should be specified in brackets as it is a list
    }

    network_rulesets_enabled = ["true"] # specify as true within "" if the property is to be used
    network_rulesets = {
      default_action                 = "Allow"
      public_network_access_enabled  = true
      trusted_service_access_enabled = false
      ip_rule                        = []
      virtual_network_rule           = []
    }
  }
}








