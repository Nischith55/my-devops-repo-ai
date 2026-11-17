resource "azurerm_eventhub" "evh" {
  provider            = azurerm.provisioning
  for_each            = var.evh_ids
  name                = var.resource_name_to_create
  namespace_name      = each.value["namespace_name"]
  resource_group_name = each.value["resource_group_name"]
  partition_count     = each.value["partition_count"]
  message_retention   = each.value["message_retention"]
}

resource "azurerm_eventhub_authorization_rule" "evh_authorization_rule" {
  for_each            = var.evh_authorization_rule
  name                = each.value["name"]
  namespace_name      = each.value["namespace_name"]
  eventhub_name       = each.value["eventhub_name"]
  resource_group_name = each.value["resource_group_name"]
  listen              = each.value["listen"]
  send                = each.value["send"]
  manage              = each.value["manage"]
  depends_on          = [ azurerm_eventhub.evh ]
}