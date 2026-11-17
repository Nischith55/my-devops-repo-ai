resource "azurerm_monitor_diagnostic_setting" "arm_diagnostic_setting" {
  provider = azurerm.provisioning
  for_each = {
    for key, value in var.logicapp_ids :
    key => value
    if value.enable_diagnostic_settings != false
  }
  name                       = format("%s-%s", var.resource_name_to_create, lower("monitor_diagnostic_setting"))
  target_resource_id         = azurerm_logic_app_standard.logic_app[each.key].id
  log_analytics_workspace_id = lookup(each.value, "log_analytics_workspace_id", "")
  metric { category = "AllMetrics" }
  enabled_log { category = "WorkflowRuntime" }
}