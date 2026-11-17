output "eventhub_consumer_group_name" {
  description = "eventhub consumer group name"
  value       = module.evh_cg_prod.eventhub_consumer_group_name
}

output "eventhub_consumer_group_namespace" {
  description = "eventhub consumer group namespace name"
  value       = module.evh_cg_prod.eventhub_consumer_group_namespace
}

output "eventhub_consumer_group_resource_group_name" {
  description = "eventhub consumer group resource group name"
  value       = module.evh_cg_prod.eventhub_consumer_group_resource_group_name
}

output "eventhub_consumer_group_eventhub_name" {
  description = "eventhub consumer group eventhub name"
  value       = module.evh_cg_prod.eventhub_consumer_group_eventhub_name
}