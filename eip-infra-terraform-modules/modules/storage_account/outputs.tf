output "storage_account_name" {
  description = "storage account name"
  value = [ for i in azurerm_storage_account.storage_account: i.name ]
}

output "storage_account_rg_name" {
  description = "storage account resource group name"
  value = [ for i in azurerm_storage_account.storage_account: i.resource_group_name ]
}


output "storage_container_name" {
  description = "storage container name"
  value = [ for i in azurerm_storage_container.storage_container: i.name ]
}

output "storage_account_network_rules" {
  description = "storage account network rules"
  value = [ for i in azurerm_storage_account.storage_account: i.network_rules ]
}

output "storage_share_name" {
  description = "storage share name"
  value = [ for i in azurerm_storage_share.storage_share: i.name ]
}

output "storage_encryption_scope_name" {
  description = "storage encryption scope name"
  value = [ for i in azurerm_storage_encryption_scope.storage_encrypt_scope: i.name ]
}

output "infrastructure_encryption_enabled" {
  description = "whether infrastructure encryption is enabled in encryption scope?"
  value = [ for i in azurerm_storage_encryption_scope.storage_encrypt_scope: i.infrastructure_encryption_enabled ]
}

output "storage_queue_name" {
  description = "storage queue name"
  value = [ for i in azurerm_storage_queue.storage_queue: i.name ]
}

output "storage_table_name" {
  description = "storage table name"
  value = [ for i in azurerm_storage_table.storage_table: i.name ]
}