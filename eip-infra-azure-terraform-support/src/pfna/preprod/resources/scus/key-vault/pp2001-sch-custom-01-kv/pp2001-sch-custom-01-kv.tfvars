key_vaults = {
  pp2001-sch-custom-01-kv = {
    location            = "southcentralus"
    resource_group_name = "pep-pfna-sch-preprod-scus-k8s-01-rg"
    sku_name            = "standard"

    enable_rbac_authorization       = false
    enabled_for_deployment          = false
    enabled_for_disk_encryption     = false
    enabled_for_template_deployment = true
    purge_protection_enabled        = true
    public_network_access_enabled   = true
    soft_delete_retention_days      = 30

    tags = {
      department   = "pfna"
      description  = "Key Vault for SCH Preprod custom domains"
      environment  = "Preprod"
      financialTag = "H-######"
      serviceName  = "PFNA-SCH"
    }

    network_acls = {
      bypass                     = "AzureServices"
      default_action             = "Allow"
      ip_rules                   = []
      virtual_network_subnet_ids = ["/subscriptions/93c33431-a080-4b4a-a362-3b7c5a36b6dc/resourceGroups/pep-network-nonprod-snt-dps-eus-01-rg/providers/Microsoft.Network/virtualNetworks/pep-paas-nonprod-snt-dps-01-eus-vnet/subnets/pep-aks-global-01-subnet",
                                    "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-eus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-eus-network-01-vnet/subnets/pep-eiap-nonprod-eus-network-01-vnet-infra-services-01-snet",
                                    "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-eus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-eus-network-01-vnet/subnets/pep-eiap-nonprod-eus-network-01-vnet-infra-services-02-snet"]
    }

    access_policies = [
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "f6605f0a-8b58-4acc-ac4c-ded01b11c376" #pep-pfna-nonprod-infra-kv-01-mi
        key_permissions         = ["Get", "List"]
        secret_permissions      = ["Get", "List"]
        certificate_permissions = ["Get", "List"]
        storage_permissions     = ["Get", "List"]
      },
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "fb58adea-7dd4-42e8-8b12-877554427819" #pep-eiap-preprod-paas-sp
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
        object_id               = "f748990b-37e4-45a3-8fc8-37985b73780d" #myCert Azure Key Vault provisioning
        key_permissions         = ["Get", "List", "Update", "Create", "Import", "Delete", "Recover", "Backup", "Restore", "GetRotationPolicy", "SetRotationPolicy", "Rotate"]
        secret_permissions      = ["Get", "List", "Set", "Delete", "Recover", "Backup", "Restore"]
        certificate_permissions = ["Get", "List", "Import", "GetIssuers", "ListIssuers", "Create"]
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
        object_id               = "01a95099-8f48-4a82-a6a6-9f308e1deba9" #pep-pfna-sch-preprod-scus-01-aks-agentpool
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
        object_id               = "6b922ae7-a185-48e9-9e7e-ec5bb6f67b95" #myCert Azure Key Vault provisioning
        key_permissions         = ["Get", "List", "Update", "Create", "Import", "Recover", "Backup", "Restore", "GetRotationPolicy", "SetRotationPolicy", "Rotate"]
        secret_permissions      = ["Get", "List", "Set", "Recover", "Backup", "Restore"]
        certificate_permissions = ["Get", "List", "Import", "GetIssuers", "ListIssuers", "Create", "Update"]
        storage_permissions     = []
      }
    ]
  }
}