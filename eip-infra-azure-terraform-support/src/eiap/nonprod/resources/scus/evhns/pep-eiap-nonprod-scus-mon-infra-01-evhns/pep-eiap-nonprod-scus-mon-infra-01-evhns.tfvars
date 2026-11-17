evhns_ids = {
  pep-eiap-nonprod-scus-mon-infra-01-evhns = {
    name                          = "pep-eiap-nonprod-scus-mon-infra-01-evhns"
    location                      = "southcentralus"
    resource_group_name           = "pep-eiap-nonprod-scus-k8s-01-rg"
    sku                           = "Standard"
    capacity                      = 1
    auto_inflate_enabled          = true
    local_authentication_enabled  = true
    maximum_throughput_units      = 20
    minimum_tls_version           = "1.0"
    public_network_access_enabled = true
    tags = {
      AzRegion           = "southcentralus"
      CreatedByUser      = "09261927"
      CreatedExecuteHost = "PEPWUL146726"
      CreatedTimeStamp   = "2020-07-26T18:29:33"
      Department         = "EIAP"
      Environment        = "nonprod"
      Module             = "EventHub Namespace"
      Organization       = "CTO"
      Sector             = "Global Implementation"
      ServicePrincipal   = "pep-eiap-nonprod-k8s-sp"
      costCenter         = "EIAP"
      financialTag       = "H-######"
      serviceName        = "EIP"
    }
    dedicated_cluster_id = null # specify the cluster id within "" to use this property
    zone_redundant       = false
    identity_enabled     = [] # specify as true within "" if the property is to be used
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




