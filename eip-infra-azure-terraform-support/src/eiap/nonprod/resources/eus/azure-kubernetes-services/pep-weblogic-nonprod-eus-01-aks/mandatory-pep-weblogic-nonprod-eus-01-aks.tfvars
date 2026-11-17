cluster_vnet_snet_resource_group_name   = "pep-eiap-nonprod-eus-network-01-rg"
cluster_vnet_name                       = "pep-eiap-nonprod-eus-network-01-vnet"
cluster_snet_name                       = "pep-eiap-nonprod-eus-network-01-vnet-weblogic-01-aks-01-snet"
managed_identity_name                   = "pep-weblog-nonprod-eus-global-01-aks-01-mi"
managed_identity_resource_group_name    = "pep-eiap-nonprod-eus-sqldba-01-rg"
cluster_resource_group_name             = "pep-eiap-nonprod-eus-sqldba-01-rg"
cluster_location                        = "eastus"
active_directory_admin_group_object_ids = ["367dfb5d-8aed-4dcf-9366-6024024bfb94"]
private_dns_zone_id                     = "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-eus-network-01-rg/providers/Microsoft.Network/privateDnsZones/privatelink.eastus.azmk8s.io"
kubernetes_version                      = "1.26.6"
default_node_pool_resource_group        = "pep-weblogic-nonprod-eus-01-aks-rg" 

cluster_tags = {
  CreateData    = "{\"User\": \"naren\", \"TimeStamp\": \"2023-04-28T18:22:44\", \"ExecuteHost\": \"PEPWUL165761\"}"
  ModifiedData  = "{\"User\": \"80303850\", \"TimeStamp\": \"2023-07-11T12:50:34\", \"ExecuteHost\": \"USC02DVADXML85\"}"
  department    = "weblogic"
  description   = "Global 01 AKS Cluster"
  environment   = "nonprod"
  financialTag  = "H-######"
  serviceName   = "eip"
  spn           = "pep-eiap-nonprod-k8s-sp"
  crosscharge_aks = "crosscharge"
}

default_node_pool_tags = {
  ModifiedData  = "{\"User\": \"80303850\", \"TimeStamp\": \"2023-07-11T13:27:59\", \"ExecuteHost\": \"USC02DVADXML85\"}"
  department    = "weblogic"
  description   = "Global 01 AKS Cluster"
  environment   = "nonprod"
  financialTag  = "H-######"
  serviceName   = "weblogic"
  spn           = "pep-eiap-nonprod-k8s-sp"
}