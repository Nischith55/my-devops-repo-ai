storage_accounts = {
  pp3003hhnxt01aks01sa = {
    name                     = "pp3003hhnxt01aks01sa"
    account_kind             = "StorageV2"
    location                 = "eastus"
    resource_group_name      = "pep-pfna-cit-prod-eus-k8s-hhnxt-01-rg"
    account_replication_type = "ZRS"
    account_tier             = "Standard"
    tags = {
      CreateData   = "{\"ExecuteHost\": \"LTIN246004\", \"TimeStamp\": \"2022-10-12T15:56:41\", \"User\": \"sivakalyan\"}"
      department   = "pfna"
      description  = "hhnxt-01-aks"
      environment  = "prod"
      financialTag = "H-######"
      serviceName  = "och-hhnext"
    }
    allow_nested_items_to_be_public = false
    is_hns_enabled                  = false
    large_file_share_enabled        = true
    network_rules = {
      bypass                     = ["AzureServices", "Logging", "Metrics"]
      default_action             = "Deny"
      ip_rules                   = ["165.197.0.0/16","165.198.0.0/16","28.0.0.0/8"]
      virtual_network_subnet_ids = ["/subscriptions/55bde1f0-8591-432c-a37f-5c1bdff8c2f8/resourceGroups/pep-network-prod-pfna-eus-01-rg/providers/Microsoft.Network/virtualNetworks/pep-paas-prod-pfna-eus-01-vnet/subnets/pep-aks-global-01-subnet"]
    }
    enable_https_traffic_only = true
    identity_enabled          = [] # specify as ["true"] to enable it
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
    custom_domain_enabled = [] # specify as ["true"] to enable it
    custom_domain = {
      name = ""
    }
    nfsv3_enabled   = false
    routing_enabled = []
    routing = {
      publish_internet_endpoints  = false              #default values
      publish_microsoft_endpoints = false              #default values
      choice                      = "MicrosoftRouting" #default values
    }
    blob_properties_enabled = [] # specify as ["true"] to enable it
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
      container_delete_retention_policy_enabled = [] #specify as ["true"] to enable it
      container_delete_retention_policy_in_days = 0
      delete_retention_policy_enabled = []
      delete_retention_policy_in_days = 0 #this property depends on delete_retention_policy_enabled
      last_access_time_enabled        = false
      restore_policy_enabled          = []
      restore_policy_in_days          = 0 #this value should be less than delete_retention_policy property
      versioning_enabled              = false
    }
  }
}

storage_containers = {
  
}

storage_shares = {
  #set of properties to be used is given below
  # storage_share = {
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
  # storage_encrypt_scope = {
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
  # storage_queue = {
  #   name                 = "test-queue"
  #   storage_account_name = "petestsawithvnetsnet"
  #   metadata             = {}
  # }
}

storage_tables = {
  #set of properties to be used is given below
  # storage_table = {
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
