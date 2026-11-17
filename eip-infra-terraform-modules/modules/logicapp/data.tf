data "azurerm_storage_account" "storage_account_key" {
  provider                   = azurerm.provisioning
  for_each                   = var.logicapp_ids
  name                       = each.value["storage_account_name"]
  resource_group_name        = each.value["resource_group_name"]
}

data "azurerm_service_plan" "service_plan_id" {
  provider                   = azurerm.provisioning
  for_each                   = var.logicapp_ids
  name                       = each.value["ase_plan_name"]
  resource_group_name        = each.value["resource_group_name"]
}
