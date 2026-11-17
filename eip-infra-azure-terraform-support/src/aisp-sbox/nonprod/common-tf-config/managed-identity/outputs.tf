output "managed_identity_name_out" {
  description = "managed identity name"
  value = module.mi_nonprod.managed_identity_name
}

output "managed_identity_id_out" {
  description = "managed identity id"
  value = module.mi_nonprod.managed_identity_id
}

output "managed_identity_location_out" {
  description = "managed identity location"
  value = module.mi_nonprod.managed_identity_location
}

output "managed_identity_rg_name_out" {
  description = "managed identity resource group name"
  value = module.mi_nonprod.managed_identity_rg_name
}