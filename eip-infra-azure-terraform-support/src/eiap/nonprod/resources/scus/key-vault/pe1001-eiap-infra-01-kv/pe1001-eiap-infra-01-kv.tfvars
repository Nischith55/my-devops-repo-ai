key_vaults = {
  pe1001-eiap-infra-01-kv = {
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
      AzRegion           = "southcentralus"
      CreatedByUser      = "09261927"
      CreatedExecuteHost = "PEPWUL146726"
      CreatedTimeStamp   = "2020-07-08T19:38:47"
      Department         = "EIAP"
      ModifiedData       = "{\"ExecuteHost\": \"INPC1F23KR\", \"TimeStamp\": \"2022-06-09T14:30:57\", \"User\": \"chaitanya\"}"
      Module             = "Key Vault"
      Organization       = "CTO"
      Project            = "EIAP"
      SP                 = "pep-eiap-nonprod-paas-sp"
      Sector             = "Global Implementation"
      costCenter         = "EIAP"
      environment        = "nonprod"
      financialTag       = "H-######"
      serviceName        = "EIP"
    }

    network_acls = {
      bypass                     = "AzureServices"
      default_action             = "Allow"
      ip_rules                   = ["157.51.199.111"]
      virtual_network_subnet_ids = []
    }

    access_policies = [ 
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "52df70d1-4fe2-4a3d-9325-4185f96a78cc"
        key_permissions         = ["Get"]
        secret_permissions      = ["Get"]
        certificate_permissions = ["Get"]
        storage_permissions     = ["Get"]
      },

      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "2822624f-6db7-4c3e-bb9e-63dc840ea1d4"
        key_permissions         = ["Get"]
        secret_permissions      = ["Get"]
        certificate_permissions = ["Get"]
        storage_permissions     = ["Get"]
      },

      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "8e10944b-1339-4b7f-ac6f-1d0cafb2d085"
        key_permissions         = ["Backup", "Create", "Decrypt", "Delete", "Encrypt", "Get", "Import", "List", "Purge", "Recover", "Restore", "Sign", "UnwrapKey", "Update", "Verify", "WrapKey", "Release", "Rotate", "GetRotationPolicy", "GetRotationPolicy"]
        secret_permissions      = ["Backup", "Delete", "Get", "List", "Purge", "Recover", "Restore", "Set"]
        certificate_permissions = ["Backup", "Create", "Delete", "DeleteIssuers", "Get", "GetIssuers", "Import", "List", "ListIssuers", "ManageContacts", "ManageIssuers", "Purge", "Recover", "Restore", "SetIssuers", "Update"]
        storage_permissions     = ["Backup", "Delete", "DeleteSAS", "Get", "GetSAS", "List", "ListSAS", "Purge", "Recover", "RegenerateKey", "Restore", "Set", "SetSAS", "Update"] 
      },

      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "0004fd5e-d171-49a1-9a9e-436860d16989"
        key_permissions         = ["Backup", "Create", "Decrypt", "Delete", "Encrypt", "Get", "Import", "List", "Purge", "Recover", "Restore", "Sign", "UnwrapKey", "Update", "Verify", "WrapKey", "Release", "Rotate", "GetRotationPolicy", "GetRotationPolicy"]
        secret_permissions      = ["Backup", "Delete", "Get", "List", "Purge", "Recover", "Restore", "Set"]
        certificate_permissions = ["Backup", "Create", "Delete", "DeleteIssuers", "Get", "GetIssuers", "Import", "List", "ListIssuers", "ManageContacts", "ManageIssuers", "Purge", "Recover", "Restore", "SetIssuers", "Update"]
        storage_permissions     = ["Backup", "Delete", "DeleteSAS", "Get", "GetSAS", "List", "ListSAS", "Purge", "Recover", "RegenerateKey", "Restore", "Set", "SetSAS", "Update"] 
      },

      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "367dfb5d-8aed-4dcf-9366-6024024bfb94"
        key_permissions         = ["Backup", "Create", "Decrypt", "Delete", "Encrypt", "Get", "Import", "List", "Purge", "Recover", "Restore", "Sign", "UnwrapKey", "Update", "Verify", "WrapKey", "Release", "Rotate", "GetRotationPolicy", "GetRotationPolicy"]
        secret_permissions      = ["Backup", "Delete", "Get", "List", "Purge", "Recover", "Restore", "Set"]
        certificate_permissions = ["Backup", "Create", "Delete", "DeleteIssuers", "Get", "GetIssuers", "Import", "List", "ListIssuers", "ManageContacts", "ManageIssuers", "Purge", "Recover", "Restore", "SetIssuers", "Update"]
        storage_permissions     = ["Backup", "Delete", "DeleteSAS", "Get", "GetSAS", "List", "ListSAS", "Purge", "Recover", "RegenerateKey", "Restore", "Set", "SetSAS", "Update"] 
      },

      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "3b4ead34-8ffd-4e23-889f-984ec20c9c61"
        key_permissions         = []
        secret_permissions      = ["Get", "List"]
        certificate_permissions = []
        storage_permissions     = []
      },

      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "d04c3d3c-9503-4ad3-bbc5-6160b8e68d29"
        key_permissions         = []
        secret_permissions      = ["Get", "List"]
        certificate_permissions = ["Backup", "Create", "Delete", "DeleteIssuers", "Get", "GetIssuers", "Import", "List", "ListIssuers", "ManageContacts", "ManageIssuers", "Purge", "Recover", "Restore", "SetIssuers", "Update"]
        storage_permissions     = []
      },

      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "37a2667c-78e4-4c4e-b12a-7ae558871d9b"
        key_permissions         = ["List"]
        secret_permissions      = ["List"]
        certificate_permissions = ["ListIssuers", "List"]
        storage_permissions     = []
      },
      
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "f748990b-37e4-45a3-8fc8-37985b73780d"
        key_permissions         = ["Get", "List", "Update", "Create", "Import", "Delete", "Recover", "Backup", "Restore", "GetRotationPolicy", "SetRotationPolicy", "Rotate"]
        secret_permissions      = ["Get", "List", "Set", "Delete", "Recover", "Backup", "Restore"]
        certificate_permissions = ["Get", "List", "Import", "GetIssuers", "ListIssuers", "Create"]
        storage_permissions     = []
      },

      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "44d4829a-58da-4533-95de-404f6940aafd"
        key_permissions         = []
        secret_permissions      = []
        certificate_permissions = ["Get", "List"]
        storage_permissions     = []
      },
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "772bea8b-f084-4d22-abb6-e57e26d5de30"
        key_permissions         = ["Get", "List"]
        secret_permissions      = ["Get", "List"]
        certificate_permissions = ["Get", "List"]
        storage_permissions     = []
      }

    ]
  }
}