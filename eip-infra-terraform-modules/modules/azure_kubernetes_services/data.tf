data "azurerm_client_config" "current" {
  provider = azurerm.provisioning
}
data "azurerm_subnet" "aks_vnet_snet_assoc" {
  provider             = azurerm.provisioning
  name                 = var.cluster_snet_name
  virtual_network_name = var.cluster_vnet_name
  resource_group_name  = var.cluster_vnet_snet_resource_group_name
}
data "azurerm_user_assigned_identity" "mi" {
  provider            = azurerm.provisioning
  name                = var.managed_identity_name
  resource_group_name = var.managed_identity_resource_group_name
}

data "azurerm_subnet" "vnet_snet_assoc" {
  provider             = azurerm.provisioning
  for_each             = var.node_pools
  name                 = each.value["snet_name"]
  virtual_network_name = each.value["vnet_name"]
  resource_group_name  = each.value["vnet_snet_resource_group_name"]
}
