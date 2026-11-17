cluster_vnet_snet_resource_group_name   = "pep-az-eng-surya-01-rg"
cluster_location                        = "eastus"
cluster_vnet_name                       = "pep-az-eng-surya-01-vnet"
cluster_snet_name                       = "AKS_Backup"
managed_identity_name                   = "pep-infratools-backup-test-mi"
managed_identity_resource_group_name    = "pep-az-eng-surya-01-rg"
cluster_resource_group_name             = "pep-az-eng-surya-01-rg"

active_directory_admin_group_object_ids = ["367dfb5d-8aed-4dcf-9366-6024024bfb94"]
private_dns_zone_id                     = "/subscriptions/463c7676-c9ae-45e7-98c7-cd83065a4fb1/resourceGroups/pep-network-privatednszone-01-rg/providers/Microsoft.Network/privateDnsZones/privatelink.eastus.azmk8s.io"
kubernetes_version                      = "1.28.9"
default_node_pool_resource_group        = "pep-cmptest-backup-test-rg"


cluster_tags = {
  department   = "CMPTEST"
  description  = "Global 01 AKS Cluster"
  environment  = "nonprod"
  financialTag = "H-######"
  serviceName  = "cmptest"
  spn          = "pep-eiap-nonprod-k8s-sp"
  crosscharge_aks = "direct"
}
  
default_node_pool_tags = {
  department   = "CMPTEST"
  description  = "Global 01 AKS Cluster"
  environment  = "nonprod"
  financialTag = "H-######"
  serviceName  = "cmptest"
  spn          = "pep-eiap-nonprod-k8s-sp"
  crosscharge_aks = "direct"
}