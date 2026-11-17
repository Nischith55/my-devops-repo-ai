private_endpoint = {
  PepEiapProdCommonAcr-01-pvtep = {
    private_endpoint_name                = "PepEiapProdCommonAcr-01-pvtep"
    private_endpoint_location            = "southcentralus"
    private_endpoint_resource_group_name = "pep-eiap-prod-scus-paas-01-rg"
    vnet_name                            = "pep-eiap-prod-scus-network-01-vnet"
    snet_name                            = "pep-eiap-prod-scus-network-01-vnet-paas-pvtlink-01-snet"
    vnet_snet_resource_group_name        = "pep-eiap-prod-scus-network-01-rg"
    tags = {
      CreateData   = "{\"ExecuteHost\": \"PEPWUL146726\", \"TimeStamp\": \"2021-06-16T18:24:48\", \"User\": \"09261927\"}"
      department   = "EIAP"
      environment  = "prod"
      financialTag = "H-######"
      module       = "PrivateEndpoint"
      serviceName  = "EIAP"
    }
    custom_network_interface_name         = ""
    private_service_connection_enabled = ["true"]
    private_service_connection = {
      private_service_connection_name        = "PepEiapProdCommonAcr-01-pvtep"
      private_connection_resource_id         = "/subscriptions/72d4c1b3-fd6e-432a-b18a-89eec2c10a6b/resourceGroups/pep-eiap-prod-scus-paas-01-rg/providers/Microsoft.ContainerRegistry/registries/PepEiapProdCommonAcr"
      is_manual_connection                   = false
      subresource_names                      = ["registry"]
    }
    private_dns_zone_group_enabled = ["true"] #specify "" within [] to disable this property
    private_dns_zone_group = {
      name                = "acr-dnszg" #specify "" to disable this property
      private_dns_zone_id = ["/subscriptions/72d4c1b3-fd6e-432a-b18a-89eec2c10a6b/resourceGroups/pep-eiap-prod-scus-network-01-rg/providers/Microsoft.Network/privateDnsZones/privatelink.azurecr.io"]
    }
  }
}
