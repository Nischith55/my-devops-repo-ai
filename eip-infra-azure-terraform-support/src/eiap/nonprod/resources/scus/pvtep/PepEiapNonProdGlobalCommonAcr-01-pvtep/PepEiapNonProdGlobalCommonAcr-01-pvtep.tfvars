private_endpoint = {
  PepEiapNonProdGlobalCommonAcr-01-pvtep = {
    private_endpoint_name                = "PepEiapNonProdGlobalCommonAcr-01-pvtep"
    private_endpoint_location            = "southcentralus"
    private_endpoint_resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    vnet_name                            = "pep-eiap-nonprod-scus-network-01-vnet"
    snet_name                            = "pep-eiap-nonprod-scus-network-01-vnet-paas-pvtlink-01-snet"
    vnet_snet_resource_group_name        = "pep-eiap-nonprod-scus-network-01-rg"
    tags = {
      CreateData   = "{\"User\": \"neipd999\", \"TimeStamp\": \"2023-06-28T07:57:20\", \"ExecuteHost\": \"pepsico-eip-global-devsecops-agent-batchjob-srcm9-br9dh\", \"build\": \"1795787\"}"
      department   = "EIAP"
      environment  = "nonprod"
      financialTag = "H-######"
      serviceName  = "eip"
    }
    custom_network_interface_name      = "" #specify the name within "" to use this property
    private_service_connection_enabled = ["true"]
    private_service_connection = {
      private_service_connection_name = "PepEiapNonProdGlobalCommonAcr-01-pvtep"
      private_connection_resource_id  = "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-scus-paas-01-rg/providers/Microsoft.ContainerRegistry/registries/PepEiapNonProdGlobalCommonAcr" #resource ID of the ACR
      is_manual_connection            = false
      subresource_names               = ["registry"]
    }
    private_dns_zone_group_enabled = [] #specify "true" within [] to use this property
    private_dns_zone_group = {
      name                = "" #specify the name within "" to use this property
      private_dns_zone_id = [""] #specify the dns zone ID within "" to use this property
    }
  }
}

