output "key_vault_certificate_id" {
  description = "Key vault certificate ID"
  value       = [ for i in azurerm_key_vault_certificate.key_vault_certificate: i.id ]
}

output "key_vault_certificate_secret_id" {
  description = "Key vault certificate secret ID"
  value       = [ for i in azurerm_key_vault_certificate.key_vault_certificate: i.secret_id ]
}