output "federated_credential_name_out" {
  description = "federated credential name"
  value = module.fc_prod.federated_credential_name
}

output "federated_credential_id_out" {
  description = "federated credential id"
  value = module.fc_prod.federated_credential_id
}

output "federated_credential_rg_name_out" {
  description = "federated credential resource group name"
  value = module.fc_prod.federated_credential_rg_name
}