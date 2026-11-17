resource "azurerm_user_assigned_identity" "managed_identity" {
  provider            = azurerm.provisioning
  for_each            = var.managed_ids
  location            = each.value["location"]
  name                = var.resource_name_to_create
  resource_group_name = each.value["resource_group_name"]
  tags                = each.value["tags"]  
}
