data "azurerm_storage_account" "storage_account_id" {
  provider            = azurerm.provisioning
  for_each            = var.storage_encyptions
  name                = each.value["storage_account_name"]
  resource_group_name = each.value["storage_account_resource_group_name"]
  depends_on          = [azurerm_storage_account.storage_account]
}
data "azurerm_storage_account" "sa_id" {
  provider            = azurerm.provisioning
  for_each            = var.management_policies
  name                = each.value["storage_account_name"]
  resource_group_name = each.value["storage_account_resource_group_name"]
  depends_on          = [azurerm_storage_account.storage_account]
}