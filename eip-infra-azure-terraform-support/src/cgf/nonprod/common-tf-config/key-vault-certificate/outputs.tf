output "key_vault_certificate_id" {
  description = "Key vault certificate ID"
  value       = module.kvc_nonprod.key_vault_certificate_id
}

output "key_vault_certificate_secret_id" {
  description = "Key vault certificate secret ID"
  value       = module.kvc_nonprod.key_vault_certificate_secret_id
}