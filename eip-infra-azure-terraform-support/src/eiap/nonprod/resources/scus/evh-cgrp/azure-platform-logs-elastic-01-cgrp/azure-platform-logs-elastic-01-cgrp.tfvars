evh_consumer_group = {
  azure-platform-logs-elastic-01-cgrp = {
    name                = "azure-platform-logs-elastic-01-cgrp"
    namespace_name      = "pep-eiap-nonprod-scus-monitoring-01-evhns"
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    eventhub_name       = "pep-eiap-nonprod-scus-azure-platform-logs-01-evh"
    user_metadata       = "Filebeat for Azure Platform Logs 01"
  }
}  