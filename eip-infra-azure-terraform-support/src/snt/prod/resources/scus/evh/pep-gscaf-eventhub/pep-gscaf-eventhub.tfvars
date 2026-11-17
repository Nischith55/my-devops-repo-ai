evh_ids = {
  pep-gscaf-eventhub = {
    name                = "pep-gscaf-eventhub"
    namespace_name      = "pep-dps-prod-scus-eventhub-01-evhns"
    resource_group_name = "pep-snt-b2bso-prod-scus-01-rg"
    partition_count     = 2
    message_retention   = 1
  }
}
evh_authorization_rule = {
  gscaf = {
    name                = "gscaf"
    namespace_name      = "pep-dps-prod-scus-eventhub-01-evhns"
    resource_group_name = "pep-snt-b2bso-prod-scus-01-rg"
    eventhub_name       = "pep-gscaf-eventhub"
    manage              = true
    listen              = true
    send                = true
  }
}