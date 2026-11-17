aks_clusters = {
  pep-eiap-nonprod-eus-sbox-03-aks = {
    identity_type = "UserAssigned"
    sku_tier      = "Free"

    #azure_active_directory_role_based_access_control
    ad_rbac_managed                        = true
    ad_azure_rbac_enabled                  = false
    ad_private_cluster_enabled             = true
    ad_private_cluster_public_fqdn_enabled = true

    #auto_scaler_profile  
    as_balance_similar_node_groups      = true
    as_expander                         = "most-pods"
    as_empty_bulk_delete_max            = "10"
    as_max_graceful_termination_sec     = "60"
    as_max_unready_percentage           = "55"
    as_new_pod_scale_up_delay           = "10s"
    as_max_unready_nodes                = "3"
    as_scale_down_delay_after_add       = "5m"
    as_scale_down_delay_after_delete    = "10s"
    as_scale_down_delay_after_failure   = "3m"
    as_scale_down_unneeded              = "30m"
    as_scale_down_unready               = "20m"
    as_scale_down_utilization_threshold = "0.3"
    as_scan_interval                    = "10s"
    as_skip_nodes_with_local_storage    = false
    as_skip_nodes_with_system_pods      = true
    as_ignore_daemonsets_utilization 	= true
    as_daemonset_eviction_for_empty_nodes	= false
    as_daemonset_eviction_for_occupied_nodes_enabled = true
    as_ignore_daemonsets_utilization_enabled = false
    as_max_node_provisioning_time = "15m"
    #linux_profile 
    linux_profile_enabled = ["true"] #set this as ["true"] to enable ssh connections to node pools; user name and
    #password will be picked up from pipeline variables

    #windows_profile
    windows_profile_enabled = [] #if using windows profile or windows aks cluster, set this variable as ["true"];
    # user name and #password will be picked up from pipeline variables 
    wp_license = "" #only possible value is "Windows_Server"

    #network_profile
    np_dns_service_ip     = "10.11.0.10"
    np_docker_bridge_cidr = "172.17.0.1/16"
    np_network_plugin     = "kubenet"
    np_load_balancer_sku  = "standard"
    np_network_policy     = "calico"
    np_outbound_type      = "userDefinedRouting"
    np_pod_cidr           = "10.201.0.0/16"
    np_service_cidr       = "10.11.0.0/16"

    #default_node_pool
    node_count            = 1
    enable_auto_scaling   = true
    enable_node_public_ip = false
    #cpu_cfs_quota         = false
    #fail_swap_on          = false
    pod_max_pid           = ["4194304"]

    kubelet_disk_type     = "OS"
    max_count             = 3
    min_count             = 1
    name                  = "nps01z3"
    node_labels = {
      balance-group = "System01ZonedPools"
    }
    only_critical_addons_enabled = false #changing this property to true will taint the default node pool 
    #with "CriticalAddonsOnly=true:NoSchedule" taint
    #node_taints                  = [] #this is always blank for default node pool
    orchestrator_version         = "1.33.6"
    os_disk_size_gb              = 100
    os_disk_type                 = "Ephemeral"
    os_sku                       = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    proximity_placement_group_id = null
    node_pool_type               = "VirtualMachineScaleSets"
    max_surge                    = [] #set this to [] if not using this property while AKS creation
    node_vm_size                 = "Standard_E4ds_v4"
    node_zones                   = [3]
    temporary_name_for_rotation  = "dfn" #DO NOT CHANGE THIS PROPERTY

    #storage_profile_enabled
    storage_profile_enabled = []   #set this as ["true"] to use this property
    blobCsiDriver           = true #default value
    diskCsiDriver           = true #default value
    fileCsiDriver           = true #default value
    snapshotController      = true #default value

    workload_autoscaler_profile = ["true"] #set this as ["true"] to use this property
    #key vault secret
    secret_rotation_enabled            = true
    secret_rotation_interval           = "5m"
    key_vault_secrets_provider_enabled = ["true"] #set this as ["true"] to use this property
    #oidc issuer
    oidc_issuer_enabled = true
    #oms agent
    oms_agent_enabled          = [] #set this as ["true"] to use this property
    log_analytics_workspace_id = ""
    disk_encryption_set_id     = null
    workload_identity_enabled  = true
    
    #Auto upgrade settings
    automatic_upgrade_channel   = "stable"
    #maintenance_window_auto_upgrade settings
    #maintenance_window_auto_upgrade_enabled = ["true"] #set this as ["true"] to use this property
    #mwau_duration               = 8                                         #default value
    #mwau_frequency              = "RelativeMonthly"                         #default value
    #mwau_interval               = 1                                         #default value
    #mwau_day_of_month           = 0                                         #default value
    #mwau_day_of_week            ="Thursday"                                 #default value
    #mwau_start_date             = "2024-09-19T00:00:00Z"                    #default value
    #mwau_start_time             = "18:00"                                   #default value
    #mwau_utc_offset             = "+05:30"                                  #default value
    #mwau_week_index             = "Third"                                   #default value
    #mwau_not_allowed = [] #set this as ["true"] to use this property        #default value
    #mwau_not_allowed_end        = null                                      #default value
    #mwau_not_allowed_start      = null                                      #default value

    #maintenance_window_node_os settings
    maintenance_window_node_os_enabled = ["true"] #set this as ["true"] to use this property
    mwno_duration               = 8                                         #default value
    mwno_frequency              = "RelativeMonthly"                         #default value
    mwno_interval               = 1                                         #default value
    mwno_day_of_month           = 0                                         #default value
    mwno_day_of_week            ="Friday"                                   #default value
    mwno_start_date             = "2024-09-13T00:00:00Z"                    #default value
    mwno_start_time             = "15:00"                                   #default value
    mwno_utc_offset             = "+05:30"                                  #default value
    mwno_week_index             = "Second"                                  #default value
    mwno_not_allowed = [] #set this as ["true"] to use this property        #default value
    mwno_not_allowed_end        = null                                      #default value
    mwno_not_allowed_start      = null                                      #default value

  }
}
