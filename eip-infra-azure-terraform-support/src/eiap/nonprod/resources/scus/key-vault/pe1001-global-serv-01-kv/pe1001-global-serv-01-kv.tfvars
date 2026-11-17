key_vaults = {
  pe1001-global-serv-01-kv = {
    location            = "southcentralus"
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    sku_name            = "standard"

    enable_rbac_authorization       = false
    enabled_for_deployment          = true
    enabled_for_disk_encryption     = true
    enabled_for_template_deployment = true
    purge_protection_enabled        = true
    public_network_access_enabled   = true
    soft_delete_retention_days      = 7

    tags = {
      AzRegion            = "southcentralus",
      CreatedByUser       = "80213871",
      CreatedExecuteHost  = "INPC18PADJ",
      CreatedTimeStamp    = "2020-12-24T14:17:38",
      Environment         = "nonprod",
      Module              = "Key Vault",
      Project             = "eiap-services",
      SP                  = "pep-eiap-nonprod-paas-sp",
      Sector              = "global",
      financialTag        = "H-######",
      serviceName         = "EIAP"
    }

    network_acls = {
      bypass                     = "AzureServices"
      default_action             = "Allow"
      ip_rules                   = []
      virtual_network_subnet_ids = []
    }

    access_policies = [
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "9b6ffed0-c645-45ba-b34f-f0d3790b9eed"
        key_permissions         = ["Get",
                                   "List",
                                   "Update",
                                   "Create",
                                   "Import",
                                   "Delete",
                                   "Recover",
                                   "Backup",
                                   "Restore",
                                   "Decrypt",
                                   "Encrypt",
                                   "UnwrapKey",
                                   "WrapKey",
                                   "Verify",
                                   "Sign",
                                   "Release",
                                   "Rotate",
                                   "GetRotationPolicy",
                                   "SetRotationPolicy"]
        secret_permissions      = ["Get",
                                   "List",
                                   "Set",
                                   "Delete",
                                   "Recover",
                                   "Backup",
                                   "Restore"]
        certificate_permissions = ["Get",
                                   "List",
                                   "Update",
                                   "Create",
                                   "Import",
                                   "Delete",
                                   "Recover",
                                   "Backup",
                                   "Restore",
                                   "ManageContacts",
                                   "ManageIssuers",
                                   "GetIssuers",
                                   "ListIssuers",
                                   "SetIssuers",
                                   "DeleteIssuers"]
        storage_permissions     = [] 
      },
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "2207322a-6b0b-4c77-9a19-a8ba1f0230fa"
        key_permissions         = ["Get",
                                   "List",
                                   "Update",
                                   "Create",
                                   "Import",
                                   "Delete",
                                   "Recover",
                                   "Backup",
                                   "Restore",
                                   "Decrypt",
                                   "Encrypt",
                                   "UnwrapKey",
                                   "WrapKey",
                                   "Verify",
                                   "Sign",
                                   "Release",
                                   "Rotate",
                                   "GetRotationPolicy",
                                   "SetRotationPolicy"]
        secret_permissions      = ["Get",
                                   "List",
                                   "Set",
                                   "Delete",
                                   "Recover",
                                   "Backup",
                                   "Restore"]
        certificate_permissions = ["Get",
                                   "List",
                                   "Update",
                                   "Create",
                                   "Import",
                                   "Delete",
                                   "Recover",
                                   "Backup",
                                   "Restore",
                                   "ManageContacts",
                                   "ManageIssuers",
                                   "GetIssuers",
                                   "ListIssuers",
                                   "SetIssuers",
                                   "DeleteIssuers"]
        storage_permissions     = []
      },
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "2ab2aca6-98db-4256-bae5-c0aa5d0b7f47"
        key_permissions         = ["Get",
                                   "List",
                                   "Update",
                                   "Create",
                                   "Import",
                                   "Delete",
                                   "Recover",
                                   "Backup",
                                   "Restore",
                                   "Decrypt",
                                   "Encrypt",
                                   "UnwrapKey",
                                   "WrapKey",
                                   "Verify",
                                   "Sign",
                                   "Release",
                                   "Rotate",
                                   "GetRotationPolicy",
                                   "SetRotationPolicy"]
        secret_permissions      = ["Get",
                                   "List",
                                   "Set",
                                   "Delete",
                                   "Recover",
                                   "Backup",
                                   "Restore"]
        certificate_permissions = ["Get",
                                   "List",
                                   "Update",
                                   "Create",
                                   "Import",
                                   "Delete",
                                   "Recover",
                                   "Backup",
                                   "Restore",
                                   "ManageContacts",
                                   "ManageIssuers",
                                   "GetIssuers",
                                   "ListIssuers",
                                   "SetIssuers",
                                   "DeleteIssuers"]
        storage_permissions     = []
      },
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "882548d6-2ed6-40ee-bd36-db76d5b6e80f"
        key_permissions         = ["Get"]
        secret_permissions      = ["Get"]
        certificate_permissions = ["Get"]
        storage_permissions     = []
      }
    ]
  }
}