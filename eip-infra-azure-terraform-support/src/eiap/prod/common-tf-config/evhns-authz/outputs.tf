output "eventhub_namespace_authorization_rule_name" {
  description = "eventhub namespace authorization rule name"
  value       = module.evhns_authz_prod.eventhub_namespace_authorization_rule_name
}

output "eventhub_namespace_authorization_rule_namespace_name" {
  description = "eventhub namespace authorization rule namespace name"
  value       = module.evhns_authz_prod.eventhub_namespace_authorization_rule_namespace_name
}

output "eventhub_namespace_authorization_rule_resource_group_name" {
  description = "eventhub namespace authorization rule resource group name"
  value       = module.evhns_authz_prod.eventhub_namespace_authorization_rule_resource_group_name
}