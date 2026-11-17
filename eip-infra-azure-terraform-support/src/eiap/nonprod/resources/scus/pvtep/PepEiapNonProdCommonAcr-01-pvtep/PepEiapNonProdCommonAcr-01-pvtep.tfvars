private_endpoint = {
  PepEiapNonProdCommonAcr-01-pvtep = {
    private_endpoint_name                = "PepEiapNonProdCommonAcr-01-pvtep"
    private_endpoint_location            = "southcentralus"
    private_endpoint_resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    vnet_name                            = "pep-eiap-nonprod-scus-network-01-vnet"
    snet_name                            = "pep-eiap-nonprod-scus-network-01-vnet-paas-pvtlink-01-snet"
    vnet_snet_resource_group_name        = "pep-eiap-nonprod-scus-network-01-rg"
    tags = {
      ModifiedData = "{\"ExecuteHost\": \"INPC1F23KR\", \"TimeStamp\": \"2022-03-16T18:32:41\", \"User\": \"test\"}"
      department   = "EIAP"
      environment  = "nonprod"
      financialTag = "H-######"
      serviceName  = "EIAP"
    }
    custom_network_interface_name      = "" #specify the name within "" to use this property
    private_service_connection_enabled = ["true"]
    private_service_connection = {
      private_service_connection_name = "PepEiapNonProdCommonAcr-01-pvtep"
      private_connection_resource_id  = "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-scus-paas-01-rg/providers/Microsoft.ContainerRegistry/registries/PepEiapNonProdCommonAcr" #resource ID of the ACR
      is_manual_connection            = false
      subresource_names               = ["registry"]
    }
    private_dns_zone_group_enabled = [] #specify "true" within [] to use this property
    private_dns_zone_group = {
      name                = ""   #specify the name within "" to use this property
      private_dns_zone_id = [""] #specify the dns zone ID within "" to use this property
    }
  }
}

