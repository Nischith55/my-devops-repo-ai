private_endpoint = {
  PepEiapPreProdCommonAcr-01-pvtep = {
    private_endpoint_name                = "PepEiapPreProdCommonAcr-01-pvtep"
    private_endpoint_location            = "southcentralus"
    private_endpoint_resource_group_name = "pep-eiap-preprod-scus-paas-01-rg"
    vnet_name                            = "pep-eiap-preprod-scus-network-01-vnet"
    snet_name                            = "pep-eiap-preprod-scus-network-01-vnet-paas-pvtlink-01-snet"
    vnet_snet_resource_group_name        = "pep-eiap-preprod-scus-network-01-rg"
    tags = {
      CreateData   = "{\"ExecuteHost\": \"PEPWUL146726\", \"TimeStamp\": \"2021-03-22T00:24:11\", \"User\": \"09261927\"}"
      department   = "EIAP"
      environment  = "preprod"
      financialTag = "H-######"
      module       = "PrivateEndpoint"
      serviceName  = "EIAP"
    }
    custom_network_interface_name      = "" #specify the name within "" to use this property
    private_service_connection_enabled = ["true"]
    private_service_connection = {
      private_service_connection_name = "PepEiapPreProdCommonAcr-01-pvtep"
      private_connection_resource_id  = "/subscriptions/8a22bd18-1080-472c-a8af-da15be88b076/resourceGroups/pep-eiap-preprod-scus-paas-01-rg/providers/Microsoft.ContainerRegistry/registries/PepEiapPreProdCommonAcr" #resource ID of the ACR
      is_manual_connection            = false
      subresource_names               = ["registry"]
    }
    private_dns_zone_group_enabled = ["true"]
    private_dns_zone_group = {
      name                = "acr-dnszg"
      private_dns_zone_id = ["/subscriptions/8a22bd18-1080-472c-a8af-da15be88b076/resourceGroups/pep-eiap-preprod-scus-network-01-rg/providers/Microsoft.Network/privateDnsZones/privatelink.azurecr.io"] #specify the dns zone ID within "" to use this property
    }
  }
}

