cluster_resource_group_name             = "pep-dr-apigee-prod-scus-k8s-01-rg"
cluster_location                        = "South Central US"
cluster_vnet_snet_resource_group_name   = "pep-network-sharedservice-dr-scus-01-rg"
cluster_vnet_name                       = "pep-sharedservice-dr-01-scus-vnet"
cluster_snet_name                       = "pep-aks-01-subnet"
managed_identity_name                   = "pep-pbna-apigee-prod-scus-dr-01-aks-01-mi"
managed_identity_resource_group_name    = "pep-dr-apigee-prod-scus-k8s-01-rg"
active_directory_admin_group_object_ids = ["367dfb5d-8aed-4dcf-9366-6024024bfb94"]
private_dns_zone_id                     = "/subscriptions/463c7676-c9ae-45e7-98c7-cd83065a4fb1/resourceGroups/pep-network-privatednszone-01-rg/providers/Microsoft.Network/privateDnsZones/privatelink.southcentralus.azmk8s.io"
kubernetes_version                      = "1.33.6"
default_node_pool_resource_group        = "pep-apigee-prod-scus-dr-01-aks-rg"
cluster_tags = {
  department      = "pbna"
  description     = "PBNA Apigee scus prod DR 01 AKS Cluster"
  environment     = "prod-dr"
  financialTag    = "H-007819"
  serviceName     = "pbna"
  spn             = "pep-eiap-prod-k8s-sp"
  crosscharge_aks = "direct"
}
default_node_pool_tags = {
  department   = "apigee"
  description  = "PBNA Apigee scus prod DR 01 AKS Cluster"
  environment  = "prod-dr"
  financialTag = "H-007819"
  serviceName  = "apigee"
  spn          = "pep-eiap-prod-k8s-sp"
}
