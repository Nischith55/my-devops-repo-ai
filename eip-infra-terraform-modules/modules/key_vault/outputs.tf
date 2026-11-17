output "key_vault_name" {
  description = "key vault name"
  value       = [ for i in azurerm_key_vault.key_vault: i.name ]
}

output "key_vault_rg_name" {
  description = "key vault resource group name"
  value = [ for i in azurerm_key_vault.key_vault: i.resource_group_name ]
}

output "key_vault_location"{
  description = "key vault location"
  value = [ for i in azurerm_key_vault.key_vault: i.location]
}

output "key_vault_network_acls" {
  description = "key vault network acls"
  value = [ for i in azurerm_key_vault.key_vault: i.network_acls ]
}