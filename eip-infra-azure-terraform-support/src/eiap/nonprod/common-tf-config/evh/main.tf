module "evh_nonprod" {
  source                   = "git::https://PepsiCoIT@dev.azure.com/PepsiCoIT/EIP-Infrastructure/_git/eip-infra-terraform-modules//modules/evh"
  evh_ids                  = var.evh_ids
  evh_authorization_rule   = var.evh_authorization_rule
  resource_name_to_create  = var.resource_name_to_create
  subscription             = var.subscription
  clientid                 = var.clientid
  clientsecret             = var.clientsecret
  tenantid                 = var.tenantid
}