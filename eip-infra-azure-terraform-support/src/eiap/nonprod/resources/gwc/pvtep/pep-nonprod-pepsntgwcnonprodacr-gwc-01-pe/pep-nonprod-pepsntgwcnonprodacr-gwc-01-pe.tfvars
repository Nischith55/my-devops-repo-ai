private_endpoint = {
  pep-nonprod-pepsntgwcnonprodacr-gwc-01-pe = {
    private_endpoint_name                = "pep-nonprod-pepsntgwcnonprodacr-gwc-01-pe"
    private_endpoint_location            = "germanywestcentral"
    private_endpoint_resource_group_name = "pep-eiap-nonprod-gwc-paas-01-rg"
    vnet_name                            = "pep-eiap-nonprod-gwc-network-01-vnet"
    snet_name                            = "pep-eiap-nonprod-gwc-network-01-vnet-paas-pvtlink-01-snet"
    vnet_snet_resource_group_name        = "pep-eiap-nonprod-gwc-network-01-rg"
    tags = {
      
    }
    custom_network_interface_name = ""
    private_service_connection_enabled = ["true"]
    private_service_connection = {
      private_service_connection_name = "pep-nonprod-pepsntgwcnonprodacr-gwc-01-pe_3bc8e612-385a-47e8-a651-603ba1e1bc65"
      private_connection_resource_id  = "/subscriptions/8a22bd18-1080-472c-a8af-da15be88b076/resourcegroups/pep-eiap-nonprod-gwc-paas-01-rg/providers/Microsoft.ContainerRegistry/registries/pepsntgwcnonprodacr" #resource ID of the ACR
      is_manual_connection            = false
      subresource_names               = ["registry"]
    }
    private_dns_zone_group_enabled = ["true"] #specify "true" within [] to use this property
    private_dns_zone_group = {
      name                = "default" #specify the name within "" to use this property
      private_dns_zone_id = ["/subscriptions/8a22bd18-1080-472c-a8af-da15be88b076/resourceGroups/pep-eiap-nonprod-gwc-network-01-rg/providers/Microsoft.Network/privateDnsZones/privatelink.azurecr.io"] #specify the dns zone ID within "" to use this property
    }
  }
}

