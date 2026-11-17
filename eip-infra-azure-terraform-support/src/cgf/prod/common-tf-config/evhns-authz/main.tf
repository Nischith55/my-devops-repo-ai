module "evhns_authz_prod" {
  source                    = "git::https://PepsiCoIT@dev.azure.com/PepsiCoIT/EIP-Infrastructure/_git/eip-infra-terraform-modules//modules/evhns_authz"
  evhns_authorization_rule  = var.evhns_authorization_rule
  resource_name_to_create   = var.resource_name_to_create
  subscription              = var.subscription
  clientid                  = var.clientid
  clientsecret              = var.clientsecret
  tenantid                  = var.tenantid
}