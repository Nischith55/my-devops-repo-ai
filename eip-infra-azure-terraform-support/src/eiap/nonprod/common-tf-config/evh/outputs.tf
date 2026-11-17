output "eventhub_name" {
  description = "eventhub name"
  value       = module.evh_nonprod.eventhub_name
}

output "eventhub_namespace_name" {
  description = "eventhub namespace name"
  value       = module.evh_nonprod.eventhub_namespace_name
}

output "eventhub_resource_group_name" {
  description = "eventhub resource group name"
  value       = module.evh_nonprod.eventhub_resource_group_name
}

output "azurerm_eventhub_authorization_rule_name" {
  description = "azurerm eventhub authorization_rule name"
  value       = module.evh_nonprod.azurerm_eventhub_authorization_rule_name
}
