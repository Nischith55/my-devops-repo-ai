resource "azurerm_eventhub_namespace_authorization_rule" "evhns_authorization_rule" {
  provider              = azurerm.provisioning
  for_each              = var.evhns_authorization_rule
  name                  = var.resource_name_to_create
  namespace_name        = each.value["namespace_name"]
  resource_group_name   = each.value["resource_group_name"]
  manage                = each.value["manage"]
  listen                = each.value["listen"]
  send                  = each.value["send"]
}
