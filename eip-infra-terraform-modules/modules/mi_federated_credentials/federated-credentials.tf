resource "azurerm_federated_identity_credential" "federated_credentials" {
  provider            = azurerm.provisioning
  for_each            = var.federated_credential_ids
  name                = var.resource_name_to_create
  resource_group_name = each.value["resource_group_name"]
  audience            = each.value["audience"]
  issuer              = each.value["issuer"]
  subject             = each.value["subject"]
  parent_id           = data.azurerm_user_assigned_identity.mi[each.key].id
  
}