output "cluster_name_out" {
  description = "cluster name"
  value = module.aks_np_prod-dr.cluster_name
}

output "cluster_id_out" {
  description = "cluster id"
  value = module.aks_np_prod-dr.cluster_id
}

output "kube_config_out" {
  description = "kube config"
  value = module.aks_np_prod-dr.kube_config
  sensitive = true
}

output "client_key_out" {
  description = "client key"
  value = module.aks_np_prod-dr.client_key
  sensitive = true
}

output "client_certificate_out" {
  description = "client certificate"
  value = module.aks_np_prod-dr.client_certificate
  sensitive = true
}

output "cluster_ca_certificate_out" {
  description = "cluster ca certificate"
  value = module.aks_np_prod-dr.cluster_ca_certificate
  sensitive = true
}

output "cluster_host_out" {
  description = "host"
  value = module.aks_np_prod-dr.cluster_host
  sensitive = true
}

output "node_pool_name_out" {
  description = "node pool name"
  value = module.aks_np_prod-dr.node_pool_name
}

output "node_pool_id_out" {
  description = "node pool id"
  value = module.aks_np_prod-dr.node_pool_id
}

output "node_pool_cluster_assoc_out" {
  description = "aks cluster to which node pool is associated"
  value = module.aks_np_prod-dr.node_pool_cluster_assoc
}

output "node_pool_taints_out" {
  description = "client key"
  value = module.aks_np_prod-dr.node_pool_taints
}