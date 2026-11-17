output "eventhub_namespace_name" {
  description = "eventhub_namespace_name"
  value = module.evhns_nonprod.eventhub_namespace_name
}

output "eventhub_namespace_location" {
  description = "eventhub namespace location"
  value = module.evhns_nonprod.eventhub_namespace_location
}

output "eventhub_namespace_resource_group_name" {
  description = "eventhub namespace resource group name"
  value = module.evhns_nonprod.eventhub_namespace_resource_group_name
}

output "eventhub_namespace_network_rulesets" {
  description = "eventhubnamespace network rules sets"
  value = module.evhns_nonprod.eventhub_namespace_network_rulesets
}