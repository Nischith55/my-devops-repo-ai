evh_consumer_group = {
  azure-activity-logs-elastic-01-cgrp = {
    name                = "azure-activity-logs-elastic-01-cgrp"
    namespace_name      = "pep-eiap-nonprod-scus-monitoring-01-evhns"
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    eventhub_name       = "pep-eiap-nonprod-scus-azure-activity-logs-01-evh"
    user_metadata       = "Filebeat for Azure Activity Logs 01"
  }
}  