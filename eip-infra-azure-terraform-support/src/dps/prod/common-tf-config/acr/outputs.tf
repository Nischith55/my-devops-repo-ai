output "container_registry_name_out" {
  description = "container registry name"
  value       = module.acr_prod.container_registry_name
}

output "container_registry_rg_name_out" {
  description = "container registry resource group name"
  value       = module.acr_prod.container_registry_rg_name
}

output "container_registry_location" {
  description = "container registry location"
  value = module.acr_prod.container_registry_location
}

output "container_registry_network_rule_set_out" {
  description = "container registry network rule set"
  value       = module.acr_prod.container_registry_network_rule_set
}
