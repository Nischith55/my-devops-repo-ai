evh_ids = {
  pep-eiap-nonprod-eus-azure-activity-logs-01-evh = {
    name                = "pep-eiap-nonprod-eus-azure-activity-logs-01-evh"
    namespace_name      = "pep-eiap-nonprod-eus-monitoring-01-evhns"
    resource_group_name = "pep-eiap-nonprod-eus-paas-01-rg"
    partition_count     = 5
    message_retention   = 7
  }
}
evh_authorization_rule = {
  AzureDiagnosticManagerAccessKey = {
    name                = "AzureDiagnosticManagerAccessKey"
    namespace_name      = "pep-eiap-nonprod-eus-monitoring-01-evhns"
    resource_group_name = "pep-eiap-nonprod-eus-paas-01-rg"
    eventhub_name       = "pep-eiap-nonprod-eus-azure-activity-logs-01-evh"
    manage              = true
    listen              = true
    send                = true
  }
  ElasticBeatListenerAccessKey = {
    name                = "ElasticBeatListenerAccessKey"
    namespace_name      = "pep-eiap-nonprod-eus-monitoring-01-evhns"
    resource_group_name = "pep-eiap-nonprod-eus-paas-01-rg"
    eventhub_name       = "pep-eiap-nonprod-eus-azure-activity-logs-01-evh"
    manage              = false
    listen              = true
    send                = false
  }
}
 