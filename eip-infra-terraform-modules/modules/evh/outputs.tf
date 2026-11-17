output "eventhub_name" {
  description = "eventhub name"
  value       = [for i in azurerm_eventhub.evh : i.name]
}

output "eventhub_namespace_name" {
  description = "eventhub namespace name"
  value       = [for i in azurerm_eventhub.evh : i.namespace_name]
}

output "eventhub_resource_group_name" {
  description = "eventhub resource group name"
  value       = [for i in azurerm_eventhub.evh : i.resource_group_name]
}

output "azurerm_eventhub_authorization_rule_name" {
  description = "azurerm eventhub authorization_rule name"
  value       = [for i in azurerm_eventhub_authorization_rule.evh_authorization_rule : i.name]
}
