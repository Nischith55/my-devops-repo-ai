evhns_ids = {
  pep-eiap-prod-suk-monitoring-01-evhns = {
    name                          = "pep-eiap-prod-suk-monitoring-01-evhns"
    location                      = "uksouth"
    resource_group_name           = "pep-eiap-prod-suk-paas-01-rg"
    sku                           = "Standard"
    capacity                      = 20
    auto_inflate_enabled          = true
    local_authentication_enabled  = true
    maximum_throughput_units      = 20
    minimum_tls_version           = "1.0"
    public_network_access_enabled = true
    tags = {
        CreateData = "{\"ExecuteHost\": \"INPC18PADJ\", \"TimeStamp\": \"2021-12-09T12:02:51\", \"User\": \"80213871\"}"
        department = "EIAP"
        environment = "prod"
        financialTag = "H-######"
        serviceName = "EIAP"
    }
    dedicated_cluster_id = null  # specify the cluster id within "" to use this property
    zone_redundant       = true
    identity_enabled     = []    # specify as true within "" if the property is to be used
    identity = {
      type         = null
      identity_ids = [] #should be specified in brackets as it is a list
    }

    network_rulesets_enabled = ["true"] # specify as true within "" if the property is to be used
    network_rulesets = {
      default_action                 = "Deny"
      public_network_access_enabled  = true
      trusted_service_access_enabled = true
      ip_rule                        = []
      virtual_network_rule           = [
        {
          ignore_missing_virtual_network_service_endpoint = true
          subnet_id = "/subscriptions/72d4c1b3-fd6e-432a-b18a-89eec2c10a6b/resourceGroups/pep-eiap-prod-suk-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-prod-suk-network-01-vnet/subnets/pep-eiap-prod-suk-network-01-vnet-global-01-aks-01-snet"
        },
        {
          ignore_missing_virtual_network_service_endpoint = true
          subnet_id = "/subscriptions/72d4c1b3-fd6e-432a-b18a-89eec2c10a6b/resourceGroups/pep-eiap-prod-suk-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-prod-suk-network-01-vnet/subnets/pep-eiap-prod-suk-network-01-vnet-infra-02-aks-01-snet"
        }
      ]
    }
  }
}




