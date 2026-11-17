resource "azurerm_logic_app_standard" "logic_app" {
  provider                   = azurerm.provisioning
  for_each                   = var.logicapp_ids
  name                       = var.resource_name_to_create
  location                   = each.value["location"]
  resource_group_name        = each.value["resource_group_name"]
  app_service_plan_id        = data.azurerm_service_plan.service_plan_id[each.key].id
  storage_account_name       = each.value["storage_account_name"]
  storage_account_access_key = data.azurerm_storage_account.storage_account_key[each.key].primary_access_key
  app_settings               = each.value["app_settings"]
  client_affinity_enabled    = each.value["client_affinity_enabled"]
  client_certificate_mode    = each.value["client_certificate_mode"]
  tags                       = each.value["tags"]
  enabled                    = each.value["enabled"]
  https_only                 = each.value["https_only"]
    identity {
    type = "SystemAssigned" 
  }
}