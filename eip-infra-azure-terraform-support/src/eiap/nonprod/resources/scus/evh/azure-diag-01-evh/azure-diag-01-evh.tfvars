evh_ids = {
  azure-diag-01-evh = {
    name                = "azure-diag-01-evh"
    namespace_name      = "pep-eiap-nonprod-scus-monitoring-01-evhns"
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    partition_count     = 32
    message_retention   = 7
  }
}
evh_authorization_rule = {
  ElasticBeatListenerAccessKey = {
    name                = "ElasticBeatListenerAccessKey"
    namespace_name      = "pep-eiap-nonprod-scus-monitoring-01-evhns"
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    eventhub_name       = "azure-diag-01-evh"
    manage              = false
    listen              = true
    send                = false
  }
}
 
 