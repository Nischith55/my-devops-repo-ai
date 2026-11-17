resource "azurerm_service_plan" "ase_plan" {
   provider                   = azurerm.provisioning
   for_each                   = var.ase_plan_ids
   name                       = var.resource_name_to_create
   resource_group_name        = each.value["resource_group_name"]
   location                   = each.value["location"]
   os_type                    = each.value["os_type"]
   sku_name                   = each.value["sku_name"]
   app_service_environment_id = data.azurerm_app_service_environment_v3.asev3_id[each.key].id
   zone_balancing_enabled     = each.value["zone_balancing_enabled"]
   tags                       = each.value["tags"]
   per_site_scaling_enabled   = each.value["per_site_scaling_enabled"]
   worker_count               = each.value["worker_count"]
   maximum_elastic_worker_count = each.value["maximum_elastic_worker_count"]
 
 }

