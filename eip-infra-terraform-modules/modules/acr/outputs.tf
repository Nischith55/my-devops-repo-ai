output "container_registry_name" {
  description = "container registry name"
  value = [ for i in azurerm_container_registry.container_registry: i.name ]
}

output "container_registry_rg_name" {
  description = "container registry resource group name"
  value = [ for i in azurerm_container_registry.container_registry: i.resource_group_name ]
}

output "container_registry_location" {
  description = "container registry location"
  value = [for i in azurerm_container_registry.container_registry: i.location ]
}

output "container_registry_network_rule_set" {
  description = "container registry network rule set"
  value = [ for i in azurerm_container_registry.container_registry: i.network_rule_set ]
}

