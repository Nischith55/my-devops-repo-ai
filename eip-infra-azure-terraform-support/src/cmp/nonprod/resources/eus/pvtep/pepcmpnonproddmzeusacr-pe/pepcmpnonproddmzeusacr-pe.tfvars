private_endpoint = {
  pepcmpnonproddmzeusacr-pe = {
    private_endpoint_name                = "pepcmpnonproddmzeusacr-pe"
    private_endpoint_location            = "eastus"
    private_endpoint_resource_group_name = "ess-cv-aks-paas-eus-rg"
    vnet_name                            = "ess-cv-spoke-vnet"
    snet_name                            = "pe-subnet"
    vnet_snet_resource_group_name        = "ess-cv-network-eus-rg"
    tags = {
      
    }
    custom_network_interface_name = "pepcmpnonproddmzeusacr-pe-nic"
    private_service_connection_enabled = ["true"]
    private_service_connection = {
      private_service_connection_name = "pepcmpnonproddmzeusacr-pe"
      private_connection_resource_id  = "/subscriptions/dcae03ca-ca66-40ff-a58e-a8585fd62d6d/resourceGroups/ess-cv-aks-paas-eus-rg/providers/Microsoft.ContainerRegistry/registries/pepcmpnonproddmzeusacr" #resource ID of the ACR
      is_manual_connection            = false
      subresource_names               = ["registry"]
    }
    private_dns_zone_group_enabled = ["true"] #specify "true" within [] to use this property
    private_dns_zone_group = {
      name                = "default" #specify the name within "" to use this property
      private_dns_zone_id = ["/subscriptions/dcae03ca-ca66-40ff-a58e-a8585fd62d6d/resourceGroups/ess-cv-network-eus-rg/providers/Microsoft.Network/privateDnsZones/privatelink.azurecr.io"] #specify the dns zone ID within "" to use this property
    }
  }
}

