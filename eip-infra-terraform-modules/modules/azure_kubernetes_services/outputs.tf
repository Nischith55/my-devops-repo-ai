output "cluster_name" {
  description = "cluster name"
  value = [ for i in azurerm_kubernetes_cluster.aks_cluster: i.name ]
}

output "cluster_id" {
  description = "cluster id"
  value = [ for i in azurerm_kubernetes_cluster.aks_cluster: i.id ]
}

output "kube_config" {
  description = "kube config"
  value = [ for i in azurerm_kubernetes_cluster.aks_cluster: i.kube_config_raw ]
  sensitive = true
}

output "client_key" {
  description = "client key"
  value = [ for i in azurerm_kubernetes_cluster.aks_cluster: i.kube_config.0.client_key ]
  sensitive = true
}

output "client_certificate" {
  description = "client certificate"
  value = [ for i in azurerm_kubernetes_cluster.aks_cluster: i.kube_config.0.client_certificate ]
  sensitive = true
}

output "cluster_ca_certificate" {
  description = "cluster ca certificate"
  value = [ for i in azurerm_kubernetes_cluster.aks_cluster: i.kube_config.0.cluster_ca_certificate ]
  sensitive = true
}

output "cluster_host" {
  description = "cluster host"
  value = [ for i in azurerm_kubernetes_cluster.aks_cluster: i.kube_config.0.host ]
  sensitive = true
}

output "node_pool_name" {
  description = "node pool name"
  value = [ for i in azurerm_kubernetes_cluster_node_pool.aks_node_pools: i.name ]
}

output "node_pool_id" {
  description = "node pool id"
  value = [ for i in azurerm_kubernetes_cluster_node_pool.aks_node_pools: i.id ]
}

output "node_pool_cluster_assoc" {
  description = "aks cluster to which node pool is associated"
  value = [ for i in azurerm_kubernetes_cluster_node_pool.aks_node_pools: i.kubernetes_cluster_id ]
}

output "node_pool_taints" {
  description = "node pool taints applied"
  value = [ for i in azurerm_kubernetes_cluster_node_pool.aks_node_pools: i.node_taints ]
}
