storage_accounts = {
  pe2003auto01tf01sa = {
    name                     = "pe2003auto01tf01sa"
    account_kind             = "StorageV2"
    location                 = "eastus"
    resource_group_name      = "pep-eiap-preprod-eus-infra-01-rg"
    account_replication_type = "ZRS"
    account_tier             = "Standard"
    tags = {
      department   = "EIAP"
      description  = "preprod tf state file storage"
      environment  = "preprod"
      financialTag = "H-######"
      serviceName  = "eip"
    }
    allow_nested_items_to_be_public = false
    is_hns_enabled                  = false
    large_file_share_enabled        = true
    network_rules = {
      bypass                     = ["AzureServices", "Logging", "Metrics"]
      default_action             = "Deny"
      ip_rules                   = ["202.45.7.232","116.75.94.93"]
      virtual_network_subnet_ids = ["/subscriptions/8a22bd18-1080-472c-a8af-da15be88b076/resourceGroups/pep-eiap-preprod-eus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-preprod-eus-network-01-vnet/subnets/pep-eiap-preprod-eus-network-01-vnet-infra-02-aks-01-snet",
                                    "/subscriptions/8a22bd18-1080-472c-a8af-da15be88b076/resourceGroups/pep-eiap-preprod-scus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-preprod-scus-network-01-vnet/subnets/pep-eiap-preprod-scus-network-01-vnet-infra-02-aks-01-snet"
                                    ]
    }
    enable_https_traffic_only = true
    identity_enabled          = []  # specify as ["true"] to enable it
    identity = {
      type         = null
      identity_ids = [] #should be specified in brackets as it is a list
    }
    access_tier                        = "Hot" #default value is Hot; cant be made optional so have to pass it with value as Hot
    azure_files_authentication_enabled = []     # specify as ["true"] to enable it
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
    routing_enabled = []  # specify as ["true"] to enable it
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
  eiap-storage-container = {
    name                  = "eiap-storage-container"
    storage_account_name  = "pe2003auto01tf01sa"
    metadata = {
      description = "storage container for tf state file for EIAP functional area"
    }
  }
  edap-storage-container = {
    name                  = "edap-storage-container"
    storage_account_name  = "pe2003auto01tf01sa"
    metadata = {
      description = "storage container for tf state file for EDAP functional area"
    }
  }
  pfna-storage-container = {
    name                  = "pfna-storage-container"
    storage_account_name  = "pe2003auto01tf01sa"
    metadata = {
      description = "storage container for tf state file for PFNA functional area"
    }
  }
  snt-storage-container = {
    name                  = "snt-storage-container"
    storage_account_name  = "pe2003auto01tf01sa"
    metadata = {
      description = "storage container for tf state file for SNT functional area"
    }
  }
  infratools-storage-container = {
    name                  = "infratools-storage-container"
    storage_account_name  = "pe2003auto01tf01sa"
    metadata = {
      description = "storage container for tf state file for INFRATOOLS functional area"
    }
  }
  cmp-storage-container = {
    name                  = "cmp-storage-container"
    storage_account_name  = "pe2003auto01tf01sa"
    metadata = {
      description = "storage container for tf state file for CMP functional area"
    }
  }
  infosectools-storage-container = {
    name                  = "infosectools-storage-container"
    storage_account_name  = "pe2003auto01tf01sa"
    metadata = {
      description = "storage container for tf state file for INFOSECTOOLS functional area"
    }
  }
  pbna-storage-container = {
    name                  = "pbna-storage-container"
    storage_account_name  = "pe2003auto01tf01sa"
    metadata = {
      description = "storage container for tf state file for PBNA functional area"
    }
  }
  dps-storage-container = {
    name                  = "dps-storage-container"
    storage_account_name  = "pe2003auto01tf01sa"
    metadata = {
      description = "storage container for tf state file for DPS functional area"
    }
  }
  automation-storage-container = {
    name                  = "automation-storage-container"
    storage_account_name  = "pe2003auto01tf01sa"
    metadata = {
      description = "storage container for tf state file for automation functional area"
    }
  }
  aisp-storage-container = {
    name                  = "aisp-storage-container"
    storage_account_name  = "pe2003auto01tf01sa"
    metadata = {
      description = "storage container for tf state file for aisp functional area"
    }
  }  
  pepgenx-storage-container = {
    name                  = "pepgenx-storage-container"
    storage_account_name  = "pe2003auto01tf01sa"
    metadata = {
      description = "storage container for tf state file for ppegenx functional area"
    }
  }
}

storage_shares = {
  #set of properties to be used is given below
  # storage_share1 = {
  #   share_name           = "pvc"
  #   storage_account_name = "petestsawithvnetsnet"
  #   share_quota          = 1
  #   access_tier          = "TransactionOptimized"
  #   enabled_protocol     = "SMB"
  #   metadata             = {}
  #   acl_enabled          = []
  #   acl = {
  #     acl_id                = ""
  #     access_policy_enabled = []
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
  #   name                                = "testencrypt"
  #   storage_account_name                = "petestsawithvnetsnet"
  #   source                              = "Microsoft.Storage"
  #   infrastructure_encryption_required  = true
  #   key_vault_key_id                    = null
  #   storage_account_resource_group_name = "pep-eiap-nonprod-eus-k8s-01-rg"
  # }
}

storage_queues = {
  #set of properties to be used is given below
  # storage_queue1 = {
  #   name                 = "test-queue"
  #   storage_account_name = "petestsawithvnetsnet"
  #   metadata             = {}
  # }
}

storage_tables = {
  #set of properties to be used is given below
  # storage_table1 = {
  #   name                 = "testtable"
  #   storage_account_name = "petestsawithvnetsnet"
  #   acl_enabled          = []
  #   acl = {
  #     acl_id                = ""
  #     access_policy_enabled = []
  #     access_policy = {
  #       permissions = ""
  #       start       = ""
  #       expiry      = ""
  #     }
  #   }
  # }
}
