output "federated_credential_name" {
  description = "federated credential name"
  value = [ for i in azurerm_federated_identity_credential.federated_credentials: i.name ]
}

output "federated_credential_id" {
  description = "federated credential_id"
  value = [ for i in azurerm_federated_identity_credential.federated_credentials: i.id ]
}

output "federated_credential_rg_name" {
  description = "federated credential resource group name"
  value = [ for i in azurerm_federated_identity_credential.federated_credentials: i.resource_group_name ]
}