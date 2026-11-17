key_vaults = {
  pe3001-apigee-01-kv = {
    location            = "southcentralus"
    resource_group_name = "pep-apigee-prod-scus-paas-01-rg"
    sku_name            = "standard"

    enable_rbac_authorization       = false
    enabled_for_deployment          = false
    enabled_for_disk_encryption     = false
    enabled_for_template_deployment = true
    purge_protection_enabled        = true
    public_network_access_enabled   = true
    soft_delete_retention_days      = 30

    tags = {
      pep-cmdb-bus-app-id       = "327967b31be36010b050c992604bcbc8"
      pep-cmdb-bus-app-name     = "EIP AZURE KUBERNETES SERVICE"
      pep-cmdb-app-service-id   = "ea7967b31be36010b050c992604bcbc1"
      pep-cmdb-app-service-name = "EIP AZURE KUBERNETES SERVICE PROD"
      department   = "apigee"
      description  = "Apigee scus prod 01 AKS Cluster"
      environment  = "prod"
      financialTag = "H-######"
      serviceName  = "aisp-apigee"
    }

    network_acls = {
      bypass                     = "AzureServices"
      default_action             = "Allow"
      ip_rules                   = []
      virtual_network_subnet_ids = ["/subscriptions/92ddb5ec-2ad5-45f6-b81f-e358d4904d04/resourceGroups/pep-network-prod-infratools-scus-01-rg/providers/Microsoft.Network/virtualNetworks/pep-paas-infratools-prod-scus-01-vnet/subnets/pep-apigee-prod-aks-01-subnet",
      "/subscriptions/72d4c1b3-fd6e-432a-b18a-89eec2c10a6b/resourceGroups/pep-eiap-prod-scus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-prod-scus-network-01-vnet/subnets/pep-eiap-prod-scus-network-01-vnet-global-01-aks-01-snet"]
    }

    access_policies = [
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "6b2d415a-5320-49d3-8f55-3fb09034aaea" #Team.Support.Apigee.admin
        key_permissions         = ["Get", "List", "Update", "Create", "Import", "Delete", "Recover", "Backup", "Restore", "GetRotationPolicy", "SetRotationPolicy", "Rotate"]
        secret_permissions      = ["Get", "List", "Set", "Delete", "Recover", "Backup", "Restore"]
        certificate_permissions = ["Get", "List", "Import", "GetIssuers", "ListIssuers", "Create", "Update", "Delete", "Recover", "Backup", "Restore"]
        storage_permissions     = ["Get", "List", "Set", "Delete", "Recover", "Backup", "Restore"]
      },
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "c1940fc4-7a0d-4709-8058-97c569be47bd" #pep-apigee-prod-acr-spn
        key_permissions         = ["Get", "List", "Update", "Create", "Import", "Delete", "Recover", "Backup", "Restore", "GetRotationPolicy", "SetRotationPolicy", "Rotate"]
        secret_permissions      = ["Get", "List", "Set", "Delete", "Recover", "Backup", "Restore"]
        certificate_permissions = ["Get", "List"]
        storage_permissions     = ["Get", "List"]
      }      
        
      
      
      
    ]
  }
}