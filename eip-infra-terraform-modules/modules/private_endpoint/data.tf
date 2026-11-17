data "azurerm_subnet" "subnet_name_id" {
  provider             = azurerm.provisioning
  for_each             = var.private_endpoint
  name                 = each.value["snet_name"]
  virtual_network_name = each.value["vnet_name"]
  resource_group_name  = each.value["vnet_snet_resource_group_name"]
}
