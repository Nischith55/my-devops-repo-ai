resource "azurerm_private_endpoint" "private_endpoint" {
  provider                      = azurerm.provisioning
  for_each                      = var.private_endpoint
  name                          = each.value["private_endpoint_name"]
  location                      = each.value["private_endpoint_location"]
  resource_group_name           = each.value["private_endpoint_resource_group_name"]
  subnet_id                     = data.azurerm_subnet.subnet_name_id[each.key].id
  tags                          = each.value["tags"]
  custom_network_interface_name = each.value["custom_network_interface_name"]
  
  dynamic "private_service_connection" {
    for_each = each.value["private_service_connection_enabled"]
    content {
      name                 = each.value.private_service_connection["private_service_connection_name"]
      is_manual_connection = each.value.private_service_connection["is_manual_connection"]
      #private_connection_resource_id = data.azurerm_container_registry.acr_id[each.key].id
      private_connection_resource_id = each.value.private_service_connection["private_connection_resource_id"]
      subresource_names              = each.value.private_service_connection["subresource_names"]
    }
  }

  dynamic "private_dns_zone_group" {
    for_each = each.value["private_dns_zone_group_enabled"]
    content {
      name                 = each.value.private_dns_zone_group["name"]
      private_dns_zone_ids = each.value.private_dns_zone_group["private_dns_zone_id"]
      #private_dns_zone_ids = [data.azurerm_private_dns_zone.dns_zone_id.0.id]
    }
  }
}
