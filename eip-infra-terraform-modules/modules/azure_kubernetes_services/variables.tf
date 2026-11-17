variable "node_pools" {
  type = map(object({
    name                         = string
    vm_size                      = string
    node_count                   = number
    enable_auto_scaling          = bool
    enable_node_public_ip        = bool
    pod_max_pid                  = list(string)          # used in dynamic kubelet_config
    cpu_cfs_quota_enabled        = optional(bool)        # optional
    kubelet_disk_type            = string
    max_count                    = number
    min_count                    = number
    node_labels                  = map(string)
    node_taints                  = list(string)
    orchestrator_version         = string
    os_disk_size_gb              = number
    os_disk_type                 = string
    os_type                      = string
    os_sku                       = string
    gpu_driver                   = optional(string)     # optional for GPU pools
    gpu_instance                 = optional(string) 
    tags                         = map(string)
    max_surge                    = list(string)         # used in dynamic upgrade_settings
    zones                        = list(number)
    mode                         = string
    proximity_placement_group_id = optional(string)
    max_pods                     = optional(number)
    snet_name                    = string
    vnet_name                    = string
    vnet_snet_resource_group_name = string
    temporary_name_for_rotation = optional(string)
  }))
}


variable "aks_clusters" {
  type = map(any)
}

variable "resource_name_to_create" {
  type = string
}

variable "cluster_resource_group_name" {
  type = string
}

variable "cluster_vnet_snet_resource_group_name" {
  type = string
}

variable "cluster_vnet_name" {
  type = string
}

variable "cluster_snet_name" {
  type = string
}

variable "managed_identity_name" {
  type = string
}

variable "managed_identity_resource_group_name" {
  type = string
}

variable "cluster_tags"{
  type = map(any)
}

variable "default_node_pool_tags"{
  type = map(any)
}

variable "active_directory_admin_group_object_ids" {
  type = tuple([ string ])
}

variable "private_dns_zone_id" {
  type = string
}

variable "default_node_pool_resource_group" {
  type = string
}

variable "kubernetes_version" {
  type = string
}

variable "lp_admin_username" {
  type = string
}

variable "lp_ssh_key" {
  type = string
}

variable "wp_admin_username" {
  type = string
}

variable "wp_admin_password" {
  type = string
}

variable "cluster_location" {
  type = string
}

variable "subscription" {
   type = string
 }

variable "clientid" {
   type = string
 }

variable "clientsecret" {
   type = string
 }

variable "tenantid" {
   type = string
 }