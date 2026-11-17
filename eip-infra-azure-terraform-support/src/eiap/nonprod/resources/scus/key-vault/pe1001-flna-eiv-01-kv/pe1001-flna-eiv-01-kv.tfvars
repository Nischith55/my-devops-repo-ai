key_vaults = {
  pe1001-flna-eiv-01-kv = {
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
      AzRegion      = "southcentralus"
      Department    = "EIAP"
      Environment   = "nonprod"
      Module        = "Key Vault"
      Organization  = "CTO"
      Project       = "EIV"
      SP            = "pep-eiap-nonprod-paas-sp"
      Sector        = "FLNA"
      costCenter    = "EIAP"
      financialTag  = "H-######"
      serviceName   = "EIP"
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
        object_id               = "d01606a1-772f-41f7-8c2a-a4d3fe9ed75a"
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
        object_id               = "85f5820c-a7d3-41b2-b1de-9bce20ac6690"
        key_permissions         = ["Get"]
        secret_permissions      = ["Get"]
        certificate_permissions = ["Get"]
        storage_permissions     = []
      },
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "8377df68-ae32-43be-9181-753c15999d99"
        key_permissions         = ["Get"]
        secret_permissions      = ["Get"]
        certificate_permissions = ["Get"]
        storage_permissions     = []
      },
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "6dd2d798-bbe2-4eba-98be-d3dd0f5256c4"
        key_permissions         = ["Get"]
        secret_permissions      = ["Get"]
        certificate_permissions = ["Get"]
        storage_permissions     = []
      }
    ]
  }
}