output "private_endpoint_name" {
  description = "private endpoint name"
  value = [ for i in azurerm_private_endpoint.private_endpoint: i.name ]
}

output "private_endpoint_location" {
  description = "private endpoint location"
  value = [ for i in azurerm_private_endpoint.private_endpoint: i.location ]
}

output "private_endpoint_resource_group_name" {
  description = "private endpoint resource group name"
  value = [ for i in azurerm_private_endpoint.private_endpoint: i.resource_group_name ]
}

output "private_endpoint_subnet_id" {
  description = "private endpoint subnet id"
  value = [ for i in azurerm_private_endpoint.private_endpoint: i.subnet_id ]
}