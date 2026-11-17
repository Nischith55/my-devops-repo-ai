private_endpoint = {
  pep-nonprod-pepweblogicnonprodacr-eus-01-pe = {
    private_endpoint_name                = "pep-nonprod-pepweblogicnonprodacr-eus-01-pe"
    private_endpoint_location            = "eastus"
    private_endpoint_resource_group_name = "pep-eiap-nonprod-eus-sqldba-01-rg"
    vnet_name                            = "pep-eiap-nonprod-eus-network-01-vnet"
    snet_name                            = "pep-eiap-nonprod-eus-network-01-vnet-paas-pvtlink-01-snet"
    vnet_snet_resource_group_name        = "pep-eiap-nonprod-eus-network-01-rg"
    tags = {
      
    }
    custom_network_interface_name = "pep-nonprod-pepweblogicnonprodacr-eus-01-pe-nic"
    private_service_connection_enabled = ["true"]
    private_service_connection = {
      private_service_connection_name = "pep-nonprod-pepweblogicnonprodacr-eus-01-pe"
      private_connection_resource_id  = "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-eus-sqldba-01-rg/providers/Microsoft.ContainerRegistry/registries/pepweblogicnonprodacr" #resource ID of the ACR
      is_manual_connection            = false
      subresource_names               = ["registry"]
    }
    private_dns_zone_group_enabled = ["true"] #specify "true" within [] to use this property
    private_dns_zone_group = {
      name                = "default" #specify the name within "" to use this property
      private_dns_zone_id = ["/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-eus-network-01-rg/providers/Microsoft.Network/privateDnsZones/privatelink.azurecr.io"] #specify the dns zone ID within "" to use this property
    }
  }
}

