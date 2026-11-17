evhns_ids = {
  pep-eiap-prod-scus-monitoring-01-evhns = {
    name                          = "pep-eiap-prod-scus-monitoring-01-evhns"
    location                      = "southcentralus"
    resource_group_name           = "pep-eiap-prod-scus-paas-01-rg"
    sku                           = "Standard"
    capacity                      = 9
    auto_inflate_enabled          = true
    local_authentication_enabled  = true
    maximum_throughput_units      = 20
    minimum_tls_version           = "1.0"
    public_network_access_enabled = true
    tags = {
        CreateData = "{\"ExecuteHost\": \"PEPWUL146726\", \"TimeStamp\": \"2021-05-25T10:09:41\", \"User\": \"09261927\"}"
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
          subnet_id = "/subscriptions/72d4c1b3-fd6e-432a-b18a-89eec2c10a6b/resourceGroups/pep-eiap-prod-scus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-prod-scus-network-01-vnet/subnets/pep-eiap-prod-scus-network-01-vnet-global-01-aks-01-snet"
        },
        {
          ignore_missing_virtual_network_service_endpoint = true
          subnet_id = "/subscriptions/72d4c1b3-fd6e-432a-b18a-89eec2c10a6b/resourceGroups/pep-eiap-prod-scus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-prod-scus-network-01-vnet/subnets/pep-eiap-prod-scus-network-01-vnet-infra-02-aks-01-snet"
        },
        {
          ignore_missing_virtual_network_service_endpoint = true
          subnet_id = "/subscriptions/72d4c1b3-fd6e-432a-b18a-89eec2c10a6b/resourceGroups/pep-eiap-prod-scus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-prod-scus-network-01-vnet/subnets/pep-eiap-prod-scus-network-01-vnet-infra-core-01-snet"
        },
        {
          ignore_missing_virtual_network_service_endpoint = true
          subnet_id = "/subscriptions/72d4c1b3-fd6e-432a-b18a-89eec2c10a6b/resourceGroups/pep-eiap-prod-scus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-prod-scus-network-01-vnet/subnets/pep-eiap-prod-scus-network-01-vnet-paas-pvtlink-01-snet"
        },
        {
          ignore_missing_virtual_network_service_endpoint = true
          subnet_id = "/subscriptions/72d4c1b3-fd6e-432a-b18a-89eec2c10a6b/resourceGroups/pep-eiap-prod-scus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-prod-scus-network-01-vnet/subnets/pep-eiap-prod-scus-network-01-vnet-pcfpas-01-snet"
        },
        {
          ignore_missing_virtual_network_service_endpoint = true
          subnet_id = "/subscriptions/72d4c1b3-fd6e-432a-b18a-89eec2c10a6b/resourceGroups/pep-eiap-prod-scus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-prod-scus-network-01-vnet/subnets/pep-eiap-prod-scus-network-01-vnet-pcfservices-01-snet"
        }
      ]
    }
  }
}




