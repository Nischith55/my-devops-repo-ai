output "storage_account_name_out" {
  description = "storage account name"
  value = module.sa_preprod.storage_account_name
}

output "storage_account_resource_group_name_out" {
  description = "storage account resource group name"
  value = module.sa_preprod.storage_account_rg_name
}

output "storage_container_name_out" {
  description = "storage container name"
  value = module.sa_preprod.storage_container_name
}

output "storage_account_network_rules_out" {
  description = "storage account network rules"
  value = module.sa_preprod.storage_account_network_rules
}

output "storage_share_name_out" {
  description = "storage share name"
  value = module.sa_preprod.storage_share_name
}

output "storage_encryption_scope_name_out" {
  description = "storage encryption scope name"
  value = module.sa_preprod.storage_encryption_scope_name
}

output "infrastructure_encryption_enabled_out" {
  description = "whether infrastructure encryption is enabled in encryption scope?"
  value = module.sa_preprod.infrastructure_encryption_enabled
}

output "storage_queue_name_out" {
  description = "storage queue name"
  value = module.sa_preprod.storage_queue_name
}

output "storage_table_name_out" {
  description = "storage table name"
  value = module.sa_preprod.storage_table_name
}