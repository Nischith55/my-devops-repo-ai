module "logicapp_nonprod" {
  source = "git::https://PepsiCoIT@dev.azure.com/PepsiCoIT/EIP-Infrastructure/_git/eip-infra-terraform-modules//modules/logicapp"
  logicapp_ids                 = var.logicapp_ids
  resource_name_to_create     = var.resource_name_to_create
  subscription = var.subscription
  clientid = var.clientid
  clientsecret = var.clientsecret
  tenantid = var.tenantid
}