output "logic_app_name" {
  description = "logic app name"
  value = [ for i in azurerm_logic_app_standard.logic_app: i.name ]
}

output "logic_app_id" {
  description = "logic app id"
  value = [ for i in azurerm_logic_app_standard.logic_app: i.id ]
}

output "logic_app_location" {
  description = "logic app location"
  value = [ for i in azurerm_logic_app_standard.logic_app: i.location ]
}

output "logic_app_rg_name" {
  description = "logic app resource group name"
  value = [ for i in azurerm_logic_app_standard.logic_app: i.resource_group_name ]
}