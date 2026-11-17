output "private_endpoint_name" {
  description = "private endpoint name"
  value       = module.pvtep_prod.private_endpoint_name
}

output "private_endpoint_location" {
  description = "private endpoint location"
  value       = module.pvtep_prod.private_endpoint_location
}

output "private_endpoint_resource_group_name" {
  description = "private endpoint resource group name"
  value       = module.pvtep_prod.private_endpoint_resource_group_name
}

output "private_endpoint_subnet_id" {
  description = "private endpoint subnet id"
  value       = module.pvtep_prod.private_endpoint_subnet_id
}
