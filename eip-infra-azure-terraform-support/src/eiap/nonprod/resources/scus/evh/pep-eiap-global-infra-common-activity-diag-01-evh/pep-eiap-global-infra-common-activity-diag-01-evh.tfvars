evh_ids = {
  pep-eiap-global-infra-common-activity-diag-01-evh = {
    name                = "pep-eiap-global-infra-common-activity-diag-01-evh"
    namespace_name      = "pep-eiap-nonprod-scus-mon-infra-01-evhns"
    resource_group_name = "pep-eiap-nonprod-scus-k8s-01-rg"
    partition_count     = 1
    message_retention   = 2
  }
}
evh_authorization_rule = {
  pep-eiap-global-activity-diag-01-admin-evh-authz = {
    name                = "pep-eiap-global-activity-diag-01-admin-evh-authz"
    namespace_name      = "pep-eiap-nonprod-scus-mon-infra-01-evhns"
    resource_group_name = "pep-eiap-nonprod-scus-k8s-01-rg"
    eventhub_name       = "pep-eiap-global-infra-common-activity-diag-01-evh"
    manage              = true
    listen              = true
    send                = true
  }
  pep-eiap-global-activity-diag-01-listen-evh-authz = {
    name                = "pep-eiap-global-activity-diag-01-listen-evh-authz"
    namespace_name      = "pep-eiap-nonprod-scus-mon-infra-01-evhns"
    resource_group_name = "pep-eiap-nonprod-scus-k8s-01-rg"
    eventhub_name       = "pep-eiap-global-infra-common-activity-diag-01-evh"
    manage              = false
    listen              = true
    send                = false
  }
  pep-eiap-global-activity-diag-01-send-evh-authz = {
    name                = "pep-eiap-global-activity-diag-01-send-evh-authz"
    namespace_name      = "pep-eiap-nonprod-scus-mon-infra-01-evhns"
    resource_group_name = "pep-eiap-nonprod-scus-k8s-01-rg"
    eventhub_name       = "pep-eiap-global-infra-common-activity-diag-01-evh"
    manage              = false
    listen              = false
    send                = true
  }
}
 
 