output "key_vault_name" {
  description = "key vault name"
  value = module.kv_prod.key_vault_name
}

output "key_vault_rg_name" {
  description = "key vault resource group name"
  value = module.kv_prod.key_vault_rg_name
}

output "key_vault_location" {
  description = "key vault location"
  value = module.kv_prod.key_vault_location
}

output "key_vault_network_acls" {
  description = "key vault network acls"
  value = module.kv_prod.key_vault_network_acls
}