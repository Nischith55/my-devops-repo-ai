output "eventhub_namespace_authorization_rule_name" {
  description = "eventhub namespace authorization rule name"
  value       = [for i in azurerm_eventhub_namespace_authorization_rule.evhns_authorization_rule : i.name]
}

output "eventhub_namespace_authorization_rule_namespace_name" {
  description = "eventhub namespace authorization rule namespace name"
  value       = [for i in azurerm_eventhub_namespace_authorization_rule.evhns_authorization_rule : i.namespace_name]
}


output "eventhub_namespace_authorization_rule_resource_group_name" {
  description = "eventhub namespace authorization rule resource group name"
  value       = [for i in azurerm_eventhub_namespace_authorization_rule.evhns_authorization_rule : i.resource_group_name]
}




