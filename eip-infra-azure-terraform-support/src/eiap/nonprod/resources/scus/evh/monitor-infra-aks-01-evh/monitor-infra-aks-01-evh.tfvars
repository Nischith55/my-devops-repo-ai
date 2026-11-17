evh_ids = {
  monitor-infra-aks-01-evh = {
    name                = "monitor-infra-aks-01-evh"
    namespace_name      = "pep-eiap-nonprod-scus-mon-infra-01-evhns"
    resource_group_name = "pep-eiap-nonprod-scus-k8s-01-rg"
    partition_count     = 20
    message_retention   = 1
  }
}
evh_authorization_rule = {
  aks-monitor-send-01-evh-authz = {
    name                = "aks-monitor-send-01-evh-authz"
    namespace_name      = "pep-eiap-nonprod-scus-mon-infra-01-evhns"
    resource_group_name = "pep-eiap-nonprod-scus-k8s-01-rg"
    eventhub_name       = "monitor-infra-aks-01-evh"
    manage              = false
    listen              = false
    send                = true
  }
}

