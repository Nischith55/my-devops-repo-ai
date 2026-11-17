resource "azurerm_key_vault_certificate" "key_vault_certificate" {
  provider = azurerm.provisioning
  for_each = var.key_vault_certs
  name     = var.resource_name_to_create

  key_vault_id = data.azurerm_key_vault.key_vault_id[each.key].id

  certificate {
    contents = filebase64(each.value.certificate["contents"])
    password = each.value.certificate["password"]
  }

  tags = each.value["tags"]
}