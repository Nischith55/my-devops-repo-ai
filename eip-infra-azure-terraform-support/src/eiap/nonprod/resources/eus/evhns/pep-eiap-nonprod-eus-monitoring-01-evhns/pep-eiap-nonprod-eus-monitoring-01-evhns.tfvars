evhns_ids = {
  pep-eiap-nonprod-eus-monitoring-01-evhns = {
    name                          = "pep-eiap-nonprod-eus-monitoring-01-evhns"
    location                      = "eastus"
    resource_group_name           = "pep-eiap-nonprod-eus-paas-01-rg"
    sku                           = "Standard"
    capacity                      = 20
    auto_inflate_enabled          = true
    local_authentication_enabled  = false
    maximum_throughput_units      = 20
    minimum_tls_version           = "1.2"
    public_network_access_enabled = true
    tags = {
      CreateData = "{\"User\": \"siva1712\", \"TimeStamp\": \"2023-03-19T23:45:32\", \"ExecuteHost\": \"USPF39VEQS\"}"
      department = "EIAP"
      environment = "nonprod"
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
      default_action                 = "Allow"
      public_network_access_enabled  = true
      trusted_service_access_enabled = true
      ip_rule                        = [
        {
          action = "Allow"
          ip_mask = "165.197.0.0/16"
        },
        {
          action = "Allow"
          ip_mask = "165.198.0.0/16"
        },
        {
          action = "Allow"
          ip_mask = "28.0.0.0/8"
        }
      ]
      virtual_network_rule           = [
        {
          ignore_missing_virtual_network_service_endpoint = true
          subnet_id = "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-eus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-eus-network-01-vnet/subnets/pep-eiap-nonprod-eus-network-01-vnet-global-01-aks-01-snet"
        },
        {
          ignore_missing_virtual_network_service_endpoint = true
          subnet_id = "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-eus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-eus-network-01-vnet/subnets/pep-eiap-nonprod-eus-network-01-vnet-infra-02-aks-01-snet"
        },
        {
          ignore_missing_virtual_network_service_endpoint = true
          subnet_id = "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-eus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-eus-network-01-vnet/subnets/pep-eiap-nonprod-eus-network-01-vnet-infra-core-01-snet"
        },
        {
          ignore_missing_virtual_network_service_endpoint = true
          subnet_id = "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-eus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-eus-network-01-vnet/subnets/pep-eiap-nonprod-eus-network-01-vnet-infra-services-02-snet"
        },
        {
          ignore_missing_virtual_network_service_endpoint = true
          subnet_id = "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-eus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-eus-network-01-vnet/subnets/pep-eiap-nonprod-eus-network-01-vnet-sbox-03-aks-01-snet"
        }
      ]
    }
  }
}








