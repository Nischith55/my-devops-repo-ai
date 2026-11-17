resource "azurerm_app_service_environment_v3" "asev3" {
  provider            = azurerm.provisioning
  for_each            = var.asev3_ids
  name                = var.resource_name_to_create
  resource_group_name = each.value["resource_group_name"]
  subnet_id           = each.value["subnet_id"]

  internal_load_balancing_mode = "Web, Publishing"
  zone_redundant      = each.value["zone_redundant"]
  tags                = each.value["tags"]
  allow_new_private_endpoint_connections = each.value["allow_new_private_endpoint_connections"]
}
