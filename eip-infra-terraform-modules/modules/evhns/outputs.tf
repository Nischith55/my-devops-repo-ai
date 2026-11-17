output "eventhub_namespace_name" {
  description = "eventhub namespace name"
  value       = [for i in azurerm_eventhub_namespace.evhns : i.name]
}

output "eventhub_namespace_location" {
  description = "eventhub namespace location"
  value       = [for i in azurerm_eventhub_namespace.evhns : i.location]
}

output "eventhub_namespace_resource_group_name" {
  description = "eventhub namespace resource group name"
  value       = [for i in azurerm_eventhub_namespace.evhns : i.resource_group_name]
}

output "eventhub_namespace_network_rulesets" {
  description = "eventhubnamespace network rules sets"
  value       = [for i in azurerm_eventhub_namespace.evhns : i.network_rulesets]
}
