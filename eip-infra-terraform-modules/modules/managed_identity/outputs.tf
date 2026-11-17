output "managed_identity_name" {
  description = "managed identity name"
  value = [ for i in azurerm_user_assigned_identity.managed_identity: i.name ]
}

output "managed_identity_id" {
  description = "managed_identity_id"
  value = [ for i in azurerm_user_assigned_identity.managed_identity: i.id ]
}

output "managed_identity_location" {
  description = "managed identity location"
  value = [ for i in azurerm_user_assigned_identity.managed_identity: i.location ]
}

output "managed_identity_rg_name" {
  description = "managed identity resource group name"
  value = [ for i in azurerm_user_assigned_identity.managed_identity: i.resource_group_name ]
}