resource "azurerm_eventhub_consumer_group" "evh_consumer_group" {
  provider            = azurerm.provisioning
  for_each            = var.evh_consumer_group
  name                = var.resource_name_to_create
  namespace_name      = each.value["namespace_name"]
  resource_group_name = each.value["resource_group_name"]
  eventhub_name       = each.value["eventhub_name"]
  user_metadata       = each.value["user_metadata"]
}