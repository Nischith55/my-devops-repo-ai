resource "azurerm_storage_account" "storage_account" {
  provider                        = azurerm.provisioning
  for_each                        = var.storage_accounts
  name                            = var.resource_name_to_create
  account_kind                    = each.value["account_kind"]
  location                        = each.value["location"]
  resource_group_name             = each.value["resource_group_name"]
  account_replication_type        = each.value["account_replication_type"]
  account_tier                    = each.value["account_tier"]
  tags                            = each.value["tags"]
  allow_nested_items_to_be_public = each.value["allow_nested_items_to_be_public"]
  is_hns_enabled                  = each.value["is_hns_enabled"]
  large_file_share_enabled        = each.value["large_file_share_enabled"]
  min_tls_version                 = "TLS1_2" #hardcoding the value as per suggestion from snyk
  network_rules {
    bypass                     = each.value.network_rules["bypass"]
    default_action             = each.value.network_rules["default_action"]
    ip_rules                   = each.value.network_rules["ip_rules"]
    virtual_network_subnet_ids = each.value.network_rules["virtual_network_subnet_ids"]
  }
  https_traffic_only_enabled = try(each.value["enable_https_traffic_only"], null)
  cross_tenant_replication_enabled = try(each.value["cross_tenant_replication_enabled"], true)
  dynamic "identity" {
    for_each = each.value["identity_enabled"]
    content {
      type         = each.value.identity["type"]
      identity_ids = each.value.identity["identity_ids"]
    }
  }
  access_tier = each.value["access_tier"]
  dynamic "azure_files_authentication" {
    for_each = each.value["azure_files_authentication_enabled"]
    content {
      directory_type = each.value.azure_files_authentication["directory_type"]
      dynamic "active_directory" {
        for_each = each.value.azure_files_authentication["directory_type"] == "AD" ? ["1"] : []
        content {
          storage_sid         = each.value.azure_files_authentication["storage_sid"]
          domain_name         = each.value.azure_files_authentication["domain_name"]
          domain_sid          = each.value.azure_files_authentication["domain_sid"]
          domain_guid         = each.value.azure_files_authentication["domain_guid"]
          forest_name         = each.value.azure_files_authentication["forest_name"]
          netbios_domain_name = each.value.azure_files_authentication["netbios_domain_name"]
        }
      }

    }
  }
  dynamic "custom_domain" {
    for_each = each.value["custom_domain_enabled"]
    content {
      name = each.value.custom_domain["name"]
    }
  }
  nfsv3_enabled = each.value["nfsv3_enabled"]
  dynamic "routing" {
    for_each = each.value["routing_enabled"]
    content {
      publish_internet_endpoints  = each.value.routing["publish_internet_endpoints"]
      publish_microsoft_endpoints = each.value.routing["publish_microsoft_endpoints"]
      choice                      = each.value.routing["choice"]
    }
  }
  dynamic "blob_properties" {
    for_each = each.value["blob_properties_enabled"]
    content {
      change_feed_enabled           = each.value.blob_properties["change_feed_enabled"]
      change_feed_retention_in_days = each.value.blob_properties["change_feed_retention_in_days"]
      dynamic "cors_rule" {
        for_each = each.value.blob_properties["cors_rule_enabled"]
        content {
          allowed_headers    = each.value.blob_properties.cors_rule["allowed_headers"]
          allowed_methods    = each.value.blob_properties.cors_rule["allowed_methods"]
          allowed_origins    = each.value.blob_properties.cors_rule["allowed_origins"]
          exposed_headers    = each.value.blob_properties.cors_rule["exposed_headers"]
          max_age_in_seconds = each.value.blob_properties.cors_rule["max_age_in_seconds"]
        }
      }
      dynamic "container_delete_retention_policy" {
        for_each = each.value.blob_properties["container_delete_retention_policy_enabled"]
        content {
          days = each.value.blob_properties["container_delete_retention_policy_in_days"]
        }
      }
      dynamic "delete_retention_policy" {
        for_each = each.value.blob_properties["delete_retention_policy_enabled"]
        content {
          days = each.value.blob_properties["delete_retention_policy_in_days"]
        }
      }
      last_access_time_enabled = each.value.blob_properties["last_access_time_enabled"]
      dynamic "restore_policy" {
        for_each = each.value.blob_properties["restore_policy_enabled"]
        content {
          days = each.value.blob_properties["restore_policy_in_days"]
        }
      }
      versioning_enabled = each.value.blob_properties["versioning_enabled"]
    }
  }
}

resource "azurerm_storage_container" "storage_container" {
  provider              = azurerm.provisioning
  for_each              = var.storage_containers
  name                  = each.value["name"]
  storage_account_name  = each.value["storage_account_name"]
  container_access_type = "private" #hardcoding the value as per suggestion from snyk
  metadata              = each.value["metadata"]
  depends_on            = [azurerm_storage_account.storage_account]
}

resource "azurerm_storage_share" "storage_share" {
  provider             = azurerm.provisioning
  for_each             = var.storage_shares
  name                 = each.value["share_name"]
  storage_account_name = each.value["storage_account_name"]
  quota                = each.value["share_quota"]
  access_tier          = each.value["access_tier"]
  metadata             = each.value["metadata"]
  enabled_protocol     = each.value["enabled_protocol"]
  dynamic "acl" {
    for_each = each.value["acl_enabled"]
    content {
      id = each.value.acl["acl_id"]
      dynamic "access_policy" {
        for_each = each.value.acl["access_policy_enabled"]
        content {
          permissions = each.value.acl.access_policy["permissions"]
          start       = each.value.acl.access_policy["start"]
          expiry      = each.value.acl.access_policy["expiry"]
        }
      }
    }
  }
  depends_on = [azurerm_storage_account.storage_account]
}

resource "azurerm_storage_encryption_scope" "storage_encrypt_scope" { #this property is in preview
  provider                           = azurerm.provisioning
  for_each                           = var.storage_encyptions
  name                               = each.value["name"]
  storage_account_id                 = data.azurerm_storage_account.storage_account_id[each.key].id
  source                             = each.value["source"]
  infrastructure_encryption_required = each.value["infrastructure_encryption_required"]
  key_vault_key_id                   = each.value["key_vault_key_id"]
  depends_on                         = [azurerm_storage_account.storage_account]
}

resource "azurerm_storage_queue" "storage_queue" {
  provider             = azurerm.provisioning
  for_each             = var.storage_queues
  name                 = each.value["name"]
  storage_account_name = each.value["storage_account_name"]
  metadata             = each.value["metadata"]
  depends_on           = [azurerm_storage_account.storage_account]
}

resource "azurerm_storage_table" "storage_table" {
  provider             = azurerm.provisioning
  for_each             = var.storage_tables
  name                 = each.value["name"]
  storage_account_name = each.value["storage_account_name"]
  dynamic "acl" {
    for_each = each.value["acl_enabled"]
    content {
      id = each.value.acl["acl_id"]
      dynamic "access_policy" {
        for_each = each.value.acl["access_policy_enabled"]
        content {
          permissions = each.value.acl.access_policy["permissions"]
          start       = each.value.acl.access_policy["start"]
          expiry      = each.value.acl.access_policy["expiry"]
        }
      }
    }
  }
  depends_on = [azurerm_storage_account.storage_account]
}

resource "azurerm_storage_management_policy" "management_policy" {
  provider              = azurerm.provisioning
  for_each              = var.management_policies
  storage_account_id    = data.azurerm_storage_account.sa_id[each.key].id
  dynamic "rule" {
    for_each  = each.value.rules
    iterator  = rule 
    content {
      name      = rule.value.name
      enabled   = rule.value.enabled
      filters {
        prefix_match    = rule.value.prefix_match 
        blob_types      = ["blockBlob"]
      }
      actions {
        base_blob {
          tier_to_cool_after_days_since_modification_greater_than    = try(rule.value.tier_to_cool_after_days, null)
          tier_to_archive_after_days_since_modification_greater_than = try(rule.value.tier_to_archive_after_days, null)
          delete_after_days_since_modification_greater_than          = try(rule.value.delete_after_modified_days, null)
          delete_after_days_since_last_access_time_greater_than      = try(rule.value.delete_after_accessed_days, null)
        }
      }
    }
  }
  depends_on           = [azurerm_storage_account.storage_account]
}
