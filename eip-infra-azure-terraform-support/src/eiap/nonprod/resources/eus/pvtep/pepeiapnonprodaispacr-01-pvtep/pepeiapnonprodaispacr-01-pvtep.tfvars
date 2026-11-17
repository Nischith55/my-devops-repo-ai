private_endpoint = {
  pepeiapnonprodaispacr-01-pvtep = {
    private_endpoint_name                = "pepeiapnonprodaispacr-01-pvtep"
    private_endpoint_location            = "eastus"
    private_endpoint_resource_group_name = "pep-eiap-nonprod-eus-k8s-dmz-01-rg"
    vnet_name                            = "pep-eiap-nonprod-eus-network-01-vnet"
    snet_name                            = "pep-privateendpoint-01-subnet"
    vnet_snet_resource_group_name        = "pep-eiap-nonprod-eus-network-01-rg"
    tags = {
      department   = "EIAP"
      environment  = "nonprod"
      financialTag = "H-######"
      module       = "PrivateEndpoint"
      serviceName  = "EIAP"
    }
    custom_network_interface_name         = ""
    private_service_connection_enabled = ["true"]
    private_service_connection = {
      private_service_connection_name        = "pepeiapnonprodaispacr-01-pvtep"
      private_connection_resource_id         = "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-eus-k8s-dmz-01-rg/providers/Microsoft.ContainerRegistry/registries/pepeiapeusnonprodaispacr"
      is_manual_connection                   = false
      subresource_names                      = ["registry"]
    }
    private_dns_zone_group_enabled = ["true"] #specify "" within [] to disable this property
    private_dns_zone_group = {
      name                = "acr-aisp" #specify "" to disable this property
      private_dns_zone_id = ["/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-eus-network-01-rg/providers/Microsoft.Network/privateDnsZones/privatelink.azurecr.io"]
    }
  }
}
