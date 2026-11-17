data "azurerm_user_assigned_identity" "mi" {
  provider            = azurerm.provisioning
  for_each            = var.federated_credential_ids
  name                = each.value["mi_name"]
  resource_group_name = each.value["resource_group_name"]
}
