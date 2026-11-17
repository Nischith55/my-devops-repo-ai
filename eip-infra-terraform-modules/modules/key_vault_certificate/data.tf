data "azurerm_key_vault" "key_vault_id" {
  provider                   = azurerm.provisioning
  for_each                   = var.key_vault_certs
  name                       = each.value["key_vault_name"]
  resource_group_name        = each.value["resource_group_name"]
}