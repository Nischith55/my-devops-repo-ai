resource "azurerm_key_vault" "key_vault" {
  provider                        = azurerm.provisioning
  for_each                        = var.key_vaults
  name                            = var.resource_name_to_create
  location                        = each.value["location"]
  resource_group_name             = each.value["resource_group_name"]
  sku_name                        = each.value["sku_name"]
  enable_rbac_authorization       = each.value["enable_rbac_authorization"]   
  enabled_for_deployment          = each.value["enabled_for_deployment"]
  enabled_for_disk_encryption     = each.value["enabled_for_disk_encryption"]
  enabled_for_template_deployment = each.value["enabled_for_template_deployment"]
  purge_protection_enabled        = each.value["purge_protection_enabled"]
  public_network_access_enabled   = each.value["public_network_access_enabled"]
  soft_delete_retention_days      = each.value["soft_delete_retention_days"]
  tags                            = each.value["tags"]
  tenant_id                       = var.tenantid

  network_acls {
    bypass                     = each.value.network_acls["bypass"]
    default_action             = each.value.network_acls["default_action"]
    ip_rules                   = each.value.network_acls["ip_rules"]
    virtual_network_subnet_ids = each.value.network_acls["virtual_network_subnet_ids"]
  }

  dynamic "access_policy" {
    for_each = each.value.access_policies
    content {
      tenant_id               = access_policy.value.tenant_id
      object_id               = access_policy.value.object_id
      key_permissions         = access_policy.value.key_permissions
      secret_permissions      = access_policy.value.secret_permissions
      certificate_permissions = access_policy.value.certificate_permissions
      storage_permissions     = access_policy.value.storage_permissions
    }
  }
}