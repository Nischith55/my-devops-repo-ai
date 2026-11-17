storage_accounts = {
  pc1003infra01aks01sa = {
    name                     = "pf2001fortify01aks01sa"
    account_kind             = "StorageV2"
    location                 = "southcentralus"
    resource_group_name      = "pep-fortify-preprod-scus-k8s-01-rg"
    account_replication_type = "ZRS"
    account_tier             = "Standard"
    tags = {
      department         = "FORTIFY"
      description        = "preprod fortify storage"
      environment        = "preprod"
      financialTag       = "H-######"
      serviceName        = "fortify"
    }
    allow_nested_items_to_be_public = false
    is_hns_enabled                  = false
    large_file_share_enabled        = true
    network_rules = {
      bypass                     = ["AzureServices", "Logging", "Metrics"]
      default_action             = "Deny"
      ip_rules                   = []
      virtual_network_subnet_ids = ["/subscriptions/bbfb8d7c-7f66-4690-9a6a-0aec959d9035/resourceGroups/pep-network-infosectools-nonprod-scus-01-rg/providers/Microsoft.Network/virtualNetworks/pep-paas-infosectools-nonprod-01-scus-vnet/subnets/pep-aks-global-01-subnet"]
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
    blob_properties_enabled = ["true"] # specify as [] to disable it
    blob_properties = {
      change_feed_enabled           = true #this must be set to true when versioning_enabled property is true
      change_feed_retention_in_days = 7
      cors_rule_enabled = []
      cors_rule = {
        allowed_headers    = []
        allowed_methods    = []
        allowed_origins    = []
        exposed_headers    = []
        max_age_in_seconds = ""
      }
      container_delete_retention_policy_enabled = [] #specify as ["true"] to enable it
      container_delete_retention_policy_in_days = 0
      delete_retention_policy_enabled = ["true"]
      delete_retention_policy_in_days = 7 #this property depends on delete_retention_policy_enabled
      last_access_time_enabled        = false
      restore_policy_enabled          = ["true"]
      restore_policy_in_days          = 6 #this value should be less than delete_retention_policy property
      versioning_enabled              = true
    }
  }
}

storage_containers = {
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
  #set of properties to be used is given below..
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
  #set of properties to be used is given below..
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
