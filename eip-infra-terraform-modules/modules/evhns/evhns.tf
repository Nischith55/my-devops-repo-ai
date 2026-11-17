resource "azurerm_eventhub_namespace" "evhns" {
  provider            = azurerm.provisioning
  for_each                        = var.evhns_ids
  name                            = var.resource_name_to_create
  location                        = each.value["location"]
  resource_group_name             = each.value["resource_group_name"]
  sku                             = each.value["sku"]
  capacity                        = each.value["capacity"]
  auto_inflate_enabled            = each.value["auto_inflate_enabled"]
  local_authentication_enabled    = each.value["local_authentication_enabled"]
  maximum_throughput_units        = each.value["maximum_throughput_units"]
  minimum_tls_version             = each.value["minimum_tls_version"]
  dedicated_cluster_id            = each.value["dedicated_cluster_id"]
  // zone_redundant                  = each.value["zone_redundant"]
  tags                            = each.value["tags"]
  public_network_access_enabled   = each.value["public_network_access_enabled"]
  
  dynamic "identity" {
    for_each = each.value["identity_enabled"]
    content {
      type         = each.value.identity["type"]
      identity_ids = each.value.identity["identity_ids"]
    }
  }

  dynamic "network_rulesets" {
    for_each = each.value["network_rulesets_enabled"]
    content {
      default_action = each.value.network_rulesets["default_action"]
      public_network_access_enabled = each.value.network_rulesets["public_network_access_enabled"]
      trusted_service_access_enabled= each.value.network_rulesets["trusted_service_access_enabled"]
      ip_rule = each.value.network_rulesets["ip_rule"]
      virtual_network_rule = each.value.network_rulesets["virtual_network_rule"]
    }
  }
}









    
