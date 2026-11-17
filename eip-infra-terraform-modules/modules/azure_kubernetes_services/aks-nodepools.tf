resource "azurerm_kubernetes_cluster" "aks_cluster" {
  provider = azurerm.provisioning
  for_each = var.aks_clusters
  name     = var.resource_name_to_create
  location = var.cluster_location
  identity {
    type         = each.value["identity_type"]
    identity_ids = [data.azurerm_user_assigned_identity.mi.id]
  }
  sku_tier = each.value["sku_tier"]
  tags     = var.cluster_tags
  azure_active_directory_role_based_access_control {
    // managed                = each.value["ad_rbac_managed"]
    azure_rbac_enabled     = each.value["ad_azure_rbac_enabled"]
    tenant_id              = data.azurerm_client_config.current.tenant_id
    admin_group_object_ids = var.active_directory_admin_group_object_ids
  }
  local_account_disabled   = try(each.value["local_account_disabled"], null)
 

  private_cluster_enabled             = each.value["ad_private_cluster_enabled"]
  private_cluster_public_fqdn_enabled = each.value["ad_private_cluster_public_fqdn_enabled"]
  private_dns_zone_id                 = var.private_dns_zone_id
  auto_scaler_profile {
    balance_similar_node_groups      = each.value["as_balance_similar_node_groups"]
    expander                         = each.value["as_expander"]
    empty_bulk_delete_max            = each.value["as_empty_bulk_delete_max"]
    max_graceful_termination_sec     = each.value["as_max_graceful_termination_sec"]
    max_unready_percentage           = each.value["as_max_unready_percentage"]
    new_pod_scale_up_delay           = each.value["as_new_pod_scale_up_delay"]
    max_unready_nodes                = each.value["as_max_unready_nodes"]
    scale_down_delay_after_add       = each.value["as_scale_down_delay_after_add"]
    scale_down_delay_after_delete    = each.value["as_scale_down_delay_after_delete"]
    scale_down_delay_after_failure   = each.value["as_scale_down_delay_after_failure"]
    scale_down_unneeded              = each.value["as_scale_down_unneeded"]
    scale_down_unready               = each.value["as_scale_down_unready"]
    scale_down_utilization_threshold = each.value["as_scale_down_utilization_threshold"]
    scan_interval                    = each.value["as_scan_interval"]
    skip_nodes_with_local_storage    = each.value["as_skip_nodes_with_local_storage"]
    skip_nodes_with_system_pods      = each.value["as_skip_nodes_with_system_pods"]
    // ignore_daemonsets_utilization_enabled = try(each.value["as_ignore_daemonsets_utilization"], false)
    // daemonset_eviction_for_empty_nodes_enabled = try(each.value["as_daemonset_eviction_for_empty_nodes"], false)
  }
  // automatic_channel_upgrade         = try(each.value["automatic_channel_upgrade"], null)
  automatic_upgrade_channel         = try(each.value["automatic_channel_upgrade"], null)
  node_os_upgrade_channel           = try(each.value["node_os_upgrade_channel"], "None")
  image_cleaner_enabled             = try(each.value["image_cleaner_enabled"], false)
  image_cleaner_interval_hours      = try(each.value["image_cleaner_interval_hours"], 48)
  dynamic "maintenance_window_auto_upgrade" {
    for_each  = try(each.value["maintenance_window_auto_upgrade_enabled"], [])
    content {
      duration        = each.value["mwau_duration"]
      frequency       = each.value["mwau_frequency"]
      interval        = each.value["mwau_interval"]
      day_of_month    = each.value["mwau_day_of_month"]
      day_of_week     = each.value["mwau_day_of_week"]
      start_date      = each.value["mwau_start_date"]
      start_time      = each.value["mwau_start_time"]
      utc_offset      = each.value["mwau_utc_offset"]
      week_index       = each.value["mwau_week_index"]

      dynamic "not_allowed" {
        for_each  = each.value["mwau_not_allowed"]
        content {
          end     = each.value["mwau_not_allowed_end"]
          start   = each.value["mwau_not_allowed_start"]
        }
      }
    }
  }

  dynamic "maintenance_window_node_os" {
    for_each  = try(each.value["maintenance_window_node_os_enabled"], [])
    content {
      duration        = each.value["mwno_duration"]
      frequency       = each.value["mwno_frequency"]
      interval        = each.value["mwno_interval"]
      day_of_month    = each.value["mwno_day_of_month"]
      day_of_week     = each.value["mwno_day_of_week"]
      start_date      = each.value["mwno_start_date"]
      start_time      = each.value["mwno_start_time"]
      utc_offset      = each.value["mwno_utc_offset"]
      week_index      = each.value["mwno_week_index"]

      dynamic "not_allowed" {
        for_each  = each.value["mwno_not_allowed"]
        content {
          end     = each.value["mwno_not_allowed_end"]
          start   = each.value["mwno_not_allowed_start"]
        }
      }
    }
  }

  dns_prefix         = var.resource_name_to_create
  kubernetes_version = var.kubernetes_version
  dynamic "linux_profile" {
    for_each = each.value["linux_profile_enabled"]
    content {
      admin_username = var.lp_admin_username
      ssh_key {
        key_data = var.lp_ssh_key
      }
    }
  }

  dynamic "windows_profile" { #have to include this in repo
    for_each = each.value["windows_profile_enabled"]
    content {
      admin_username = var.wp_admin_username
      admin_password = var.wp_admin_password
      license        = each.value["wp_license"]
    }
  }

  network_profile {
    dns_service_ip = each.value["np_dns_service_ip"]
    #docker_bridge_cidr = each.value["np_docker_bridge_cidr"] deprecated
    network_plugin      = each.value["np_network_plugin"]
    load_balancer_sku   = each.value["np_load_balancer_sku"]
    network_policy      = try(each.value["np_network_policy"], null)
    outbound_type       = each.value["np_outbound_type"]
    pod_cidr            = each.value["np_pod_cidr"]
    service_cidr        = each.value["np_service_cidr"]
    network_plugin_mode = try(each.value["np_network_plugin_mode"], null)
    network_data_plane  = try(each.value["np_network_data_plane"], null)
  }

  node_resource_group = var.default_node_pool_resource_group
  default_node_pool {
    node_count            = each.value["node_count"]
    // enable_auto_scaling   = each.value["enable_auto_scaling"]
    auto_scaling_enabled   = each.value["enable_auto_scaling"]
    // enable_node_public_ip = each.value["enable_node_public_ip"]
    node_public_ip_enabled = each.value["enable_node_public_ip"]
    dynamic "kubelet_config" {
      for_each = each.value["pod_max_pid"]
      content {
        pod_max_pid = kubelet_config.value
        cpu_cfs_quota_enabled  = try(each.value["cpu_cfs_quota_enabled"], true)
      }
    }
    kubelet_disk_type            = each.value["kubelet_disk_type"]
    max_count                    = each.value["max_count"]
    min_count                    = each.value["min_count"]
    name                         = each.value["name"]
    only_critical_addons_enabled = each.value["only_critical_addons_enabled"]
    #node_taints                  = each.value["node_taints"]
    node_labels                  = each.value["node_labels"]
    orchestrator_version         = var.kubernetes_version
    os_disk_size_gb              = each.value["os_disk_size_gb"]
    os_disk_type                 = each.value["os_disk_type"]
    os_sku                       = each.value["os_sku"] 
    tags                         = var.default_node_pool_tags
    type                         = each.value["node_pool_type"]
    dynamic "upgrade_settings" {
      for_each = each.value["max_surge"]
      content {
        max_surge = upgrade_settings.value
      }
    }
    vm_size                      = each.value["node_vm_size"]
    vnet_subnet_id               = data.azurerm_subnet.aks_vnet_snet_assoc.id
    zones                        = each.value["node_zones"]
    temporary_name_for_rotation  = try(each.value["temporary_name_for_rotation"], null)
    proximity_placement_group_id = each.value["proximity_placement_group_id"]
  }
  resource_group_name = var.cluster_resource_group_name
  oidc_issuer_enabled = each.value["oidc_issuer_enabled"] 
  dynamic "storage_profile" {                             
    for_each = each.value["storage_profile_enabled"]
    content {
      blob_driver_enabled         = each.value["blobCsiDriver"]
      file_driver_enabled         = each.value["fileCsiDriver"]
      disk_driver_enabled         = each.value["diskCsiDriver"]
      snapshot_controller_enabled = each.value["snapshotController"]
    }
  }
  dynamic "workload_autoscaler_profile" { 
    for_each = each.value["workload_autoscaler_profile"]
    content {
      keda_enabled = workload_autoscaler_profile.value
    }
  }
  dynamic "key_vault_secrets_provider" { 
    for_each = each.value["key_vault_secrets_provider_enabled"]
    content {
      secret_rotation_enabled  = each.value["secret_rotation_enabled"]
      secret_rotation_interval = each.value["secret_rotation_interval"]
    }
  }
  dynamic "oms_agent" { 
    for_each = each.value["oms_agent_enabled"]
    content {
      log_analytics_workspace_id = each.value["log_analytics_workspace_id"]
    }
  }
  disk_encryption_set_id    = each.value["disk_encryption_set_id"] 
  workload_identity_enabled = each.value["workload_identity_enabled"]

  lifecycle {
    #prevent_destroy = true
    ignore_changes = [
      default_node_pool[0].kubelet_config,
      default_node_pool.0.node_count,
      automatic_upgrade_channel,
      default_node_pool[0].kubelet_config,
      default_node_pool[0].linux_os_config,
      default_node_pool[0].kubelet_config[0].cpu_cfs_quota_enabled

    ]
  }
}


resource "azurerm_kubernetes_cluster_node_pool" "aks_node_pools" {
  provider              = azurerm.provisioning
  for_each              = var.node_pools
  name                  = each.value["name"]
  kubernetes_cluster_id = azurerm_kubernetes_cluster.aks_cluster[var.resource_name_to_create].id
  vm_size               = each.value["vm_size"]
  node_count            = each.value["node_count"]
  // enable_auto_scaling   = each.value["enable_auto_scaling"]
  auto_scaling_enabled   = each.value["enable_auto_scaling"]
  // enable_node_public_ip = each.value["enable_node_public_ip"]
  node_public_ip_enabled = each.value["enable_node_public_ip"]
  dynamic "kubelet_config" {
    for_each = each.value["pod_max_pid"]
    content {
      pod_max_pid = kubelet_config.value
      cpu_cfs_quota_enabled  = try(each.value["cpu_cfs_quota_enabled"], false)
    }
  }
  kubelet_disk_type    = each.value["kubelet_disk_type"]
  max_count            = each.value["max_count"]
  min_count            = each.value["min_count"]
  node_labels          = each.value["node_labels"]
  node_taints          = each.value["node_taints"]
  orchestrator_version = each.value["orchestrator_version"]
  os_disk_size_gb      = each.value["os_disk_size_gb"]
  os_disk_type         = each.value["os_disk_type"]
  os_type              = each.value["os_type"]
  os_sku               = each.value["os_sku"]
  gpu_driver           = try(each.value["gpu_driver"], null) 
  gpu_instance         = try(each.value["gpu_instance"], null)

  tags = each.value["tags"]
  dynamic "upgrade_settings" {
    for_each = each.value["max_surge"]
    content {
      max_surge = upgrade_settings.value
    }
  }
  vnet_subnet_id               = data.azurerm_subnet.vnet_snet_assoc[each.key].id
  zones                        = each.value["zones"]
  mode                         = each.value["mode"]
  temporary_name_for_rotation  = try(each.value["temporary_name_for_rotation"], null)
  proximity_placement_group_id = each.value["proximity_placement_group_id"]
  max_pods                     = try(each.value["max_pods"], null)
  lifecycle {
    ignore_changes = [
      node_count,
      kubelet_config

    ]
  }
  depends_on = [azurerm_kubernetes_cluster.aks_cluster]
}

