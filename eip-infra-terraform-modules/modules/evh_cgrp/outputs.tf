output "eventhub_consumer_group_name" {
  description = "eventhub consumer group name"
  value       = [for i in azurerm_eventhub_consumer_group.evh_consumer_group : i.name]
}

output "eventhub_consumer_group_namespace" {
  description = "eventhub consumer group namespace name"
  value       = [for i in azurerm_eventhub_consumer_group.evh_consumer_group : i.namespace_name]
}

output "eventhub_consumer_group_resource_group_name" {
  description = "eventhub consumer group resource group name"
  value       = [for i in azurerm_eventhub_consumer_group.evh_consumer_group : i.resource_group_name]
}

output "eventhub_consumer_group_eventhub_name" {
  description = "eventhub consumer group eventhub name"
  value       = [for i in azurerm_eventhub_consumer_group.evh_consumer_group : i.eventhub_name]
}
