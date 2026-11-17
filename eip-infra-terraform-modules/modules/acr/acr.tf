resource "azurerm_container_registry" "container_registry" {
  provider                      = azurerm.provisioning
  for_each                      = var.container_registries
  name                          = var.resource_name_to_create
  location                      = each.value["location"]
  resource_group_name           = each.value["resource_group_name"]
  sku                           = each.value["sku"]
  admin_enabled                 = each.value["admin_enabled"]
  data_endpoint_enabled         = each.value["data_endpoint_enabled"]
  zone_redundancy_enabled       = each.value["zone_redundancy_enabled"]
  public_network_access_enabled = each.value["public_network_access_enabled"]
  network_rule_bypass_option    = each.value["network_rule_bypass_option"]
  tags                          = each.value["tags"]
  retention_policy_in_days      = try(each.value["set_retention_policy_in_days"], null)
  trust_policy_enabled          = try(each.value["set_trust_policy_enabled"], null)
  network_rule_set {
    default_action  = each.value.network_rule_set["default_action"]
    ip_rule         = each.value.network_rule_set["ip_rule"]
    // virtual_network = try(each.value.network_rule_set["virtual_network"], null)
  }
  
  dynamic "identity" {
    for_each = each.value["identity_enabled"]
    content {
      type         = each.value.identity["type"]
      identity_ids = each.value.identity["identity_ids"]
    }
  }

    // dynamic "retention_policy" {
    //   for_each = each.value["retention_policy_enabled"]
    //   content {
    //     days    = each.value.retention_policy["retention_policy_in_days"]
    //     enabled = each.value.retention_policy["enabled"]
    //   }
    // }

  // dynamic "trust_policy" {
  //   for_each = each.value["trust_policy_enabled"]
  //   content {
  //     enabled = each.value.trust_policy["enabled"]
  //   }
  // }

  dynamic "georeplications" {
    for_each = each.value.georeplications
    content {
      location                  = georeplications.value.location
      zone_redundancy_enabled   = georeplications.value.zone_redundancy_enabled
      regional_endpoint_enabled = georeplications.value.regional_endpoint_enabled
    }
  }

}

