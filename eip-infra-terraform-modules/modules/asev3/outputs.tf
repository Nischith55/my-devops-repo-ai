output "asev3_name" {
  description = "asev3 name"
  value = [ for i in azurerm_app_service_environment_v3.asev3: i.name ]
}

output "asev3_id" {
  description = "asev3 _id"
  value = [ for i in azurerm_app_service_environment_v3.asev3: i.id ]
}

output "asev3_location" {
  description = "asev3 location"
  value = [ for i in azurerm_app_service_environment_v3.asev3: i.location ]
}

output "asev3_rg_name" {
  description = "asev3 resource group name"
  value = [ for i in azurerm_app_service_environment_v3.asev3: i.resource_group_name ]
}