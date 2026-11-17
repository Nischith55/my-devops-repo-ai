output "ase_plan_name" {
  description = "ase plan name"
  value = [ for i in azurerm_service_plan.ase_plan: i.name ]
}

output "ase_plan_id" {
  description = "ase plan_id"
  value = [ for i in azurerm_service_plan.ase_plan: i.id ]
}

output "ase_plan_location" {
  description = "ase plan location"
  value = [ for i in azurerm_service_plan.ase_plan: i.location ]
}

output "ase_plan_rg_name" {
  description = "ase plan resource group name"
  value = [ for i in azurerm_service_plan.ase_plan: i.resource_group_name ]
}