key_vaults = {
  pe3001-eiap-infra-01-kv = {
    location            = "southcentralus"
    resource_group_name = "pep-eiap-prod-scus-paas-01-rg"
    sku_name            = "standard"

    enable_rbac_authorization       = false
    enabled_for_deployment          = true
    enabled_for_disk_encryption     = true
    enabled_for_template_deployment = true
    purge_protection_enabled        = true
    public_network_access_enabled   = true
    soft_delete_retention_days      = 7

    tags = {
      AzRegion = "southcentralus"
      CreatedByUser = "80213871"
      CreatedExecuteHost = "INPC18PADJ"
      CreatedTimeStamp = "2020-10-06T20:19:24"
      ModifiedData = "{\"ExecuteHost\": \"INPC1F23KR\", \"TimeStamp\": \"2022-06-16T15:00:48\", \"User\": \"chaitanya\"}"
      Module = "Key Vault"
      Project = "EIAP"
      SP = "pep-eiap-prod-paas-sp"
      Sector = "Global Implementation"
      department = "EIAP"
      environment = "prod"
      financialTag = "H-######"
      serviceName = "EIAP"
    }

    network_acls = {
      bypass                     = "AzureServices"
      default_action             = "Allow"
      ip_rules                   = []
      virtual_network_subnet_ids = []
    }

    access_policies = [
      {
        object_id = "8e10944b-1339-4b7f-ac6f-1d0cafb2d085"
        tenant_id = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        certificate_permissions = ["Backup","Create","Delete","DeleteIssuers","Get","GetIssuers","Import","List","ListIssuers","ManageContacts","ManageIssuers","Purge","Recover","Restore","SetIssuers","Update"]
        key_permissions = ["Backup","Create","Decrypt","Delete","Encrypt","Get","Import","List","Purge","Recover","Restore","Sign","UnwrapKey","Update","Verify","WrapKey","Release","Rotate","GetRotationPolicy","SetRotationPolicy"]
        secret_permissions = ["Backup","Delete","Get","List","Purge","Recover","Restore","Set"]
        storage_permissions = ["Backup","Delete","DeleteSAS","Get","GetSAS","List","ListSAS","Purge","Recover","RegenerateKey","Restore","Set","SetSAS","Update"]
      },
      {
        object_id = "0004fd5e-d171-49a1-9a9e-436860d16989"
        tenant_id = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        certificate_permissions = ["Backup","Create","Delete","DeleteIssuers","Get","GetIssuers","Import","List","ListIssuers","ManageContacts","ManageIssuers","Purge","Recover","Restore","SetIssuers","Update"]
        key_permissions = ["Backup","Create","Decrypt","Delete","Encrypt","Get","Import","List","Purge","Recover","Restore","Sign","UnwrapKey","Update","Verify","WrapKey","Release","Rotate","GetRotationPolicy","SetRotationPolicy"]
        secret_permissions = ["Backup","Delete","Get","List","Purge","Recover","Restore","Set"]
        storage_permissions = ["Backup","Delete","DeleteSAS","Get","GetSAS","List","ListSAS","Purge","Recover","RegenerateKey","Restore","Set","SetSAS","Update"]
        
      },
      {
        object_id = "03437209-f702-4593-8230-7d8dffcdeb0f"
        tenant_id = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        certificate_permissions= []
        key_permissions = []
        secret_permissions = ["Get","List"]
        storage_permissions = []
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
        object_id = "f748990b-37e4-45a3-8fc8-37985b73780d"
        tenant_id = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        certificate_permissions= ["Get", "List", "Import", "GetIssuers", "ListIssuers", "Create"]
        key_permissions = ["Get", "List", "Update", "Create", "Import", "Delete", "Recover", "Backup", "Restore", "GetRotationPolicy", "SetRotationPolicy", "Rotate"]
        secret_permissions = ["Get", "List", "Set", "Delete", "Recover", "Backup", "Restore"]
        storage_permissions = []
      },

      {
        object_id = "44d4829a-58da-4533-95de-404f6940aafd"
        tenant_id = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        certificate_permissions= ["Get","List"]
        key_permissions = []
        secret_permissions = []
        storage_permissions = []
      },
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "04b0ce5e-3566-44bb-b447-3f1d870f828a" #pep-cgf-prod-infra-kv-01-mi
        key_permissions         = ["Get", "List"]
        secret_permissions      = ["Get", "List"]
        certificate_permissions = ["Get", "List"]
        storage_permissions     = ["Get", "List"]
      },
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "b9e010b7-b46a-433e-aef4-e84cff17f7a6" #pep-aisp-nonprod-infra-kv-01-mi
        key_permissions         = ["Get", "List"]
        secret_permissions      = ["Get", "List"]
        certificate_permissions = ["Get", "List"]
        storage_permissions     = ["Get", "List"]
      }


    ]
  }
}
