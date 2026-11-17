output "eventhub_name" {
  description = "eventhub name"
  value       = module.evh_prod.eventhub_name
}

output "eventhub_namespace_name" {
  description = "eventhub namespace name"
  value       = module.evh_prod.eventhub_namespace_name
}

output "eventhub_resource_group_name" {
  description = "eventhub resource group name"
  value       = module.evh_prod.eventhub_resource_group_name
}

output "azurerm_eventhub_authorization_rule_name" {
  description = "azurerm eventhub authorization_rule name"
  value       = module.evh_prod.azurerm_eventhub_authorization_rule_name
}
