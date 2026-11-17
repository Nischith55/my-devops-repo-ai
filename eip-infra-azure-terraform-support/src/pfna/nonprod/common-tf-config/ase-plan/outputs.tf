output "ase_plan_name_out" {
  description = "ase plan name"
  value = module.ase_plan_nonprod.ase_plan_name
}

output "ase_plan_id_out" {
  description = "ase plan id"
  value = module.ase_plan_nonprod.ase_plan_id
}

output "ase_plan_location_out" {
  description = "ase plan location"
  value = module.ase_plan_nonprod.ase_plan_location
}

output "ase_plan_rg_name_out" {
  description = "ase plan resource group name"
  value = module.ase_plan_nonprod.ase_plan_rg_name
}