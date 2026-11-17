cluster_vnet_snet_resource_group_name   = "ess-cv-network-eus-rg"
cluster_location                        = "eastus"
cluster_vnet_name                       = "ess-cv-spoke-vnet"
cluster_snet_name                       = "pep-aks-01"
managed_identity_name                   = "pep-cmp-nonprod-dmz-eus-01-aks-01-mi"
managed_identity_resource_group_name    = "ess-cv-aks-eus-rg"
cluster_resource_group_name             = "ess-cv-aks-eus-rg"

active_directory_admin_group_object_ids = ["367dfb5d-8aed-4dcf-9366-6024024bfb94"]
private_dns_zone_id                     = "/subscriptions/463c7676-c9ae-45e7-98c7-cd83065a4fb1/resourceGroups/pep-network-privatednszone-01-rg/providers/Microsoft.Network/privateDnsZones/privatelink.eastus.azmk8s.io"
kubernetes_version                      = "1.30.7"
default_node_pool_resource_group        = "pep-cmp-nonprod-dmz-eus-01-aks-rg"


cluster_tags = {
  department   = "CMP"
  description  = "Global 01 AKS Cluster"
  environment  = "nonprod"
  financialTag = "H-######"
  serviceName  = "cmp"
  spn          = "pep-eiap-nonprod-k8s-sp"
  crosscharge_aks = "direct"
}
  
default_node_pool_tags = {
  department    = "CMP"
  description   = "Global 01 AKS Cluster"
  environment   = "nonprod"
  financialTag  = "H-######"
  serviceName   = "cmp"
  spn           = "pep-eiap-nonprod-k8s-sp"
  crosscharge_aks = "direct"
}