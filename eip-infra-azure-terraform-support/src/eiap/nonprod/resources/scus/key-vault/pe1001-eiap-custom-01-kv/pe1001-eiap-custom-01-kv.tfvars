key_vaults = {
  pe1001-eiap-custom-01-kv = {
    location            = "southcentralus"
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    sku_name            = "standard"

    enable_rbac_authorization       = false
    enabled_for_deployment          = false
    enabled_for_disk_encryption     = false
    enabled_for_template_deployment = true
    purge_protection_enabled        = true
    public_network_access_enabled   = true
    soft_delete_retention_days      = 30

    tags = {
      department   = "EIAP"
      description  = "Key Vault for EIAP Nonprod Custom domains"
      environment  = "nonprod"
      financialTag = "H-######"
      serviceName  = "eiap"
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
        object_id               = "b9f350b9-608d-4bdf-a671-48d718e69c30" #pep-eiap-nonprod-eus-global-02-aks-01-mi
        key_permissions         = ["Get", "List"]
        secret_permissions      = ["Get", "List"]
        certificate_permissions = ["Get", "List"]
        storage_permissions     = ["Get", "List"]
      },
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "aef4f676-a045-463e-bba2-dbfbc9b27ea6" #pep-arize-nonprod-infra-kv-01-mi
        key_permissions         = ["Get", "List"]
        secret_permissions      = ["Get", "List"]
        certificate_permissions = ["Get", "List"]
        storage_permissions     = ["Get", "List"]
      },
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "5bbcc0b6-e4f6-44f3-9e84-6fbae2239cd0" #pep-infratools-nonprod-infra-kv-01-mi
        key_permissions         = ["Get", "List"]
        secret_permissions      = ["Get", "List"]
        certificate_permissions = ["Get", "List"]
        storage_permissions     = ["Get", "List"]
      },
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "a9d08506-09e3-486b-9d19-f1a4218b8626" #Team.App.EIAP.azurekeyvault.nonprod.admin
        key_permissions         = ["Get", "List"]
        secret_permissions      = ["Get", "List"]
        certificate_permissions = ["Get", "List"]
        storage_permissions     = ["Get", "List"]
      }, 
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "d04c3d3c-9503-4ad3-bbc5-6160b8e68d29" #pep-eiap-nonprod-paas-sp
        key_permissions         = []
        secret_permissions      = ["Get", "List"]
        certificate_permissions = ["Backup", "Create", "Delete", "DeleteIssuers", "Get", "GetIssuers", "Import", "List", "ListIssuers", "ManageContacts", "ManageIssuers", "Purge", "Recover", "Restore", "SetIssuers", "Update"]
        storage_permissions     = []
      },
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "bbb2f5e3-8297-495c-a66d-ec21d27823ff" #pep-eiap-nonprod-k8s-sp
        key_permissions         = []
        secret_permissions      = ["Get", "List"]
        certificate_permissions = ["Backup", "Create", "Delete", "DeleteIssuers", "Get", "GetIssuers", "Import", "List", "ListIssuers", "ManageContacts", "ManageIssuers", "Purge", "Recover", "Restore", "SetIssuers", "Update"]
        storage_permissions     = []
      },
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "37a2667c-78e4-4c4e-b12a-7ae558871d9b" #wiz-5995df22-66bb-42d9-97ba-571bd8bb09f3
        key_permissions         = ["List"]
        secret_permissions      = ["List"]
        certificate_permissions = ["ListIssuers", "List"]
        storage_permissions     = []
      },
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "6b922ae7-a185-48e9-9e7e-ec5bb6f67b95" #myCert Azure Key Vault provisioning
        key_permissions         = ["Get", "List", "Update", "Create", "Import", "Recover", "Backup", "Restore", "GetRotationPolicy", "SetRotationPolicy", "Rotate"]
        secret_permissions      = ["Get", "List", "Set", "Recover", "Backup", "Restore"]
        certificate_permissions = ["Get", "List", "Import", "GetIssuers", "ListIssuers", "Create", "Update"]
        storage_permissions     = []
      },
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "44d4829a-58da-4533-95de-404f6940aafd" #Team.Support.Azure.PKI.Access
        key_permissions         = []
        secret_permissions      = []
        certificate_permissions = ["Get", "List"]
        storage_permissions     = []
      },
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "1caa76bd-f3dd-43e7-b5f4-ed22aa9b41f3" #pep-eiap-nonprod-eus-global-02-aks-agentpool 
        key_permissions         = ["Backup", "Create", "Decrypt", "Delete", "Encrypt", "Get", "Import", "List", "Purge", "Recover", "Restore", "Sign", "UnwrapKey", "Update", "Verify", "WrapKey", "Release", "Rotate", "GetRotationPolicy", "GetRotationPolicy"]
        secret_permissions      = ["Backup", "Delete", "Get", "List", "Purge", "Recover", "Restore", "Set"]
        certificate_permissions = ["Backup", "Create", "Delete", "DeleteIssuers", "Get", "GetIssuers", "Import", "List", "ListIssuers", "ManageContacts", "ManageIssuers", "Purge", "Recover", "Restore", "SetIssuers", "Update"]
        storage_permissions     = ["Backup", "Delete", "DeleteSAS", "Get", "GetSAS", "List", "ListSAS", "Purge", "Recover", "RegenerateKey", "Restore", "Set", "SetSAS", "Update"] 
      },
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "367dfb5d-8aed-4dcf-9366-6024024bfb94" #Team.Support.EIAP.K8S.Admin
        key_permissions         = ["Backup", "Create", "Decrypt", "Delete", "Encrypt", "Get", "Import", "List", "Purge", "Recover", "Restore", "Sign", "UnwrapKey", "Update", "Verify", "WrapKey", "Release", "Rotate", "GetRotationPolicy", "GetRotationPolicy"]
        secret_permissions      = ["Backup", "Delete", "Get", "List", "Purge", "Recover", "Restore", "Set"]
        certificate_permissions = ["Backup", "Create", "Delete", "DeleteIssuers", "Get", "GetIssuers", "Import", "List", "ListIssuers", "ManageContacts", "ManageIssuers", "Purge", "Recover", "Restore", "SetIssuers", "Update"]
        storage_permissions     = ["Backup", "Delete", "DeleteSAS", "Get", "GetSAS", "List", "ListSAS", "Purge", "Recover", "RegenerateKey", "Restore", "Set", "SetSAS", "Update"] 
      }
    ]
  }
}