data "azurerm_app_service_environment_v3" "asev3_id" {
  provider                   = azurerm.provisioning
  for_each                   = var.ase_plan_ids
  name                       = each.value["asev3_name"]
  resource_group_name        = each.value["resource_group_name_ase"]
}
