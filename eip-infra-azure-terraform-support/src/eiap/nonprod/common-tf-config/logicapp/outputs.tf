output "logic_app_name_out" {
  description = "logic app name"
  value = module.logicapp_nonprod.logic_app_name
}

output "logic_app_id_out" {
  description = "logic app id"
  value = module.logicapp_nonprod.logic_app_id
}

output "logic_app_location_out" {
  description = "logic app location"
  value = module.logicapp_nonprod.logic_app_location
}

output "logic_app_rg_name_out" {
  description = "logic app resource group name"
  value = module.logicapp_nonprod.logic_app_rg_name
}