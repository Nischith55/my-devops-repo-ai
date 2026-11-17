storage_accounts = {
  pe1001ctoinfra01sa = {
    name                     = "pe1001ctoinfra01sa"
    account_kind             = "StorageV2"
    location                 = "southcentralus"
    resource_group_name      = "pep-eiap-nonprod-scus-paas-01-rg"
    account_replication_type = "LRS"
    account_tier             = "Premium"
    tags = {
              AzRegion = "southcentralus"
              CreatedByUser = "09261927"
              CreatedExecuteHost = "PEPWUL146726"
              CreatedTimeStamp = "2020-07-27T23:02:20"
              Department = "EIAP"
              Environment = "nonprod"
              ModifiedByUser = "09261927"
              ModifiedExecuteHost = "PEPWUL146726"
              ModifiedTimeStamp = "2020-07-27T23:04:05"
              Module = "SA"
              Organization = "CTO"
              Sector = "Global Implementation"
              ServicePrincipal = "pep-eiap-nonprod-paas-sp"
              costCenter = "EIAP"
              financialTag = "H-######"
              serviceName = "EIP"
            }
    allow_nested_items_to_be_public = false
    is_hns_enabled                  = false
    large_file_share_enabled        = null
    network_rules = {
      bypass                     = ["AzureServices"]
      default_action             = "Deny"
      ip_rules                   = ["122.172.84.112"]
      virtual_network_subnet_ids =  [
                  "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-scus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-scus-network-01-vnet/subnets/pep-eiap-nonprod-scus-network-01-vnet-global-aks-01-snet",
                  "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-scus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-scus-network-01-vnet/subnets/pep-eiap-nonprod-scus-network-01-vnet-infra-02-aks-01-snet",
                  "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-scus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-scus-network-01-vnet/subnets/pep-eiap-nonprod-scus-network-01-vnet-infra-core-01-snet",
                  "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-scus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-scus-network-01-vnet/subnets/pep-eiap-nonprod-scus-network-01-vnet-infra-services-02-snet",
                  "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-scus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-scus-network-01-vnet/subnets/pep-eiap-nonprod-scus-network-01-vnet-paas-pvtlink-01-snet",
                  "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-scus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-scus-network-01-vnet/subnets/pep-eiap-nonprod-scus-network-01-vnet-rsbox-05-aks-01-snet",
                  "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-scus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-scus-network-01-vnet/subnets/pep-eiap-nonprod-scus-network-01-vnet-sbox-03-aks-01-snet",
                  "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eip-nonprod-scus-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eip-nonprod-scus-01-vnet/subnets/pep-eip-infra-mdp-nonprod-scus-01-snet",
                  "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eip-nonprod-scus-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eip-nonprod-scus-01-vnet/subnets/pep_eip_pkspodpcfsandbox_nonprod_01_sub",
                  "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eip-nonprod-scus-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eip-nonprod-scus-01-vnet/subnets/pep_eipaks_nonprod_01_sub",
                  "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eip-nonprod-scus-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eip-nonprod-scus-01-vnet/subnets/pep_eipbackend_nonprod_01_sub",
                  "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eip-nonprod-scus-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eip-nonprod-scus-01-vnet/subnets/pep_eipinfra_nonprod_01_sub",
                  "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eip-nonprod-scus-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eip-nonprod-scus-01-vnet/subnets/pep_eippcfboshinfrasandbox_nonprod_01_sub",
                  "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eip-nonprod-scus-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eip-nonprod-scus-01-vnet/subnets/pep_eippcfmanagementdev_nonprod_01_sub",
                  "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eip-nonprod-scus-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eip-nonprod-scus-01-vnet/subnets/pep_eippcfmanagementsandbox_nonprod_01_sub",
                  "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eip-nonprod-scus-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eip-nonprod-scus-01-vnet/subnets/pep_eippcfpaassandbox_nonprod_01_sub",
                  "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eip-nonprod-scus-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eip-nonprod-scus-01-vnet/subnets/pep_eippcfpasdev_nonprod_01_sub",
                  "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eip-nonprod-scus-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eip-nonprod-scus-01-vnet/subnets/pep_eippcfservicesdev_nonprod_01_sub",
                  "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eip-nonprod-scus-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eip-nonprod-scus-01-vnet/subnets/pep_eippcfservicessandbox_nonprod_01_sub"
                ]
    }
    enable_https_traffic_only = true
    identity_enabled          = []  # specify as ["true"] to enable it
    identity = {
      type         = null
      identity_ids = [] #should be specified in brackets as it is a list
    }
    access_tier                        = "Hot" #default value is Hot; cant be made optional so have to pass it with value as Hot
    azure_files_authentication_enabled = []    # specify as ["true"] to enable it
    azure_files_authentication = {
      directory_type      = ""
      storage_sid         = ""
      domain_name         = ""
      domain_sid          = ""
      domain_guid         = ""
      forest_name         = ""
      netbios_domain_name = ""
    }
    custom_domain_enabled = []  # specify as ["true"] to enable it
    custom_domain = {
      name = ""
    }
    nfsv3_enabled   = false
    routing_enabled = []   # specify as ["true"] to enable it
    routing = {
      publish_internet_endpoints  = false              #default values
      publish_microsoft_endpoints = false              #default values
      choice                      = "MicrosoftRouting" #default values
    }
    blob_properties_enabled = [] # specify as [] to disable it
    blob_properties = {
      change_feed_enabled           = false #this must be set to true when versioning_enabled property is true
      change_feed_retention_in_days = 0
      cors_rule_enabled = []
      cors_rule = {
        allowed_headers    = []
        allowed_methods    = []
        allowed_origins    = []
        exposed_headers    = []
        max_age_in_seconds = ""
      }

      container_delete_retention_policy_enabled = [] # added
      container_delete_retention_policy_in_days = 0  # added
      delete_retention_policy_enabled = []
      delete_retention_policy_in_days = 0 #this property depends on delete_retention_policy_enabled
      last_access_time_enabled        = false
      restore_policy_enabled          = []
      restore_policy_in_days          = null #this value should be less than delete_retention_policy property
      versioning_enabled              = false
    }
  }
}

storage_containers = {
  evh-filebeat-offset-01-blob = {
    name                  = "evh-filebeat-offset-01-blob"
    storage_account_name  = "pe1001ctoinfra01sa"
    metadata = {
      "usage": "EVH_Offset_Storage"
    }
  } 
}

storage_shares = {
  #set of properties to be used is given below
  # storage_share1 = {
  #   share_name           = ""
  #   storage_account_name = ""
  #   share_quota          = 1
  #   access_tier          = "TransactionOptimized"
  #   enabled_protocol     = "SMB"
  #   metadata             = {}
  #   acl_enabled          = [] # specify as ["true"] to enable it
  #   acl = {
  #     acl_id                = ""
  #     access_policy_enabled = [] # specify as ["true"] to enable it
  #     access_policy = {
  #       permissions = ""
  #       start       = ""
  #       expiry      = ""
  #     }
  #   }
  # }
}

storage_encyptions = {
  #set of properties to be used is given below
  # storage_encrypt_scope1 = {
  #   name                                = ""
  #   storage_account_name                = ""
  #   source                              = "Microsoft.Storage"
  #   infrastructure_encryption_required  = true
  #   key_vault_key_id                    = null
  #   storage_account_resource_group_name = ""
  # }
}

storage_queues = {
  #set of properties to be used is given below
  # storage_queue1 = {
  #   name                 = ""
  #   storage_account_name = ""
  #   metadata             = {}
  # }
}

storage_tables = {
  #set of properties to be used is given below
  # storage_table1 = {
  #   name                 = "testtable"
  #   storage_account_name = ""
  #   acl_enabled          = [] # specify as ["true"] to enable it
  #   acl = {
  #     acl_id                = ""
  #     access_policy_enabled = [] # specify as ["true"] to enable it
  #     access_policy = {
  #       permissions = ""
  #       start       = ""
  #       expiry      = ""
  #     }
  #   }
  # }
}
