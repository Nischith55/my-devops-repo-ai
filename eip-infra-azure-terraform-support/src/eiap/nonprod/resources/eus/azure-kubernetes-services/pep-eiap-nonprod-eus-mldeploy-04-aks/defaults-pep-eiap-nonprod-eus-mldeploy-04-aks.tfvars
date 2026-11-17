aks_clusters = {
  pep-eiap-nonprod-eus-mldeploy-04-aks = {
    identity_type = "UserAssigned"
    sku_tier      = "Standard"

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

    #linux_profile 
    linux_profile_enabled = ["true"] #set this as ["true"] to enable ssh connections to node pools; user name and
    #password will be picked up from pipeline variables

    #windows_profile
    windows_profile_enabled = [] #if using windows profile or windows aks cluster, set this variable as ["true"];
    # user name and #password will be picked up from pipeline variables 
    wp_license = "" #only possible value is "Windows_Server"

    #network_profile
    np_dns_service_ip      = "10.17.128.10"
    np_docker_bridge_cidr  = "172.17.0.1/16"
    np_network_plugin      = "azure"
    np_load_balancer_sku   = "standard"
    np_network_policy      = "cilium"
    np_outbound_type       = "userDefinedRouting"
    np_network_data_plane  = "cilium"
    np_network_plugin_mode = "overlay"
    np_pod_cidr            = "10.217.128.0/18"
    np_service_cidr        = "10.17.128.0/18"

    #default_node_pool
    node_count            = 1
    enable_auto_scaling   = true
    enable_node_public_ip = false
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
    orchestrator_version         = "1.34.7"
    os_disk_size_gb              = 100
    os_disk_type                 = "Ephemeral"
    os_sku                       = "Ubuntu" #set to "Windows2019" or "Windows2022" to use windows
    proximity_placement_group_id = null
    node_pool_type               = "VirtualMachineScaleSets"
    max_surge                    = ["1"] #set this to [] if not using this property while AKS creation
    node_vm_size                 = "Standard_D4ds_v4"
    node_zones                   = [3]
    storage_profile_enabled      = []   #set this as ["true"] to use this property
    blobCsiDriver                = true #default value
    diskCsiDriver                = true #default value
    fileCsiDriver                = true #default value
    snapshotController           = true #default value

    workload_autoscaler_profile = [] #set this as ["true"] to use this property 
    #key vault secret
    secret_rotation_enabled            = true
    secret_rotation_interval           = "10m"
    key_vault_secrets_provider_enabled = ["true"] #set this as ["true"] to use this property
    #oidc issuer
    oidc_issuer_enabled = true
    #oms agent
    oms_agent_enabled          = [] #set this as ["true"] to use this property
    log_analytics_workspace_id = ""
    disk_encryption_set_id     = null
    workload_identity_enabled  = false
  }
}
