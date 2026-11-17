module "kvc_nonprod" {
  source                   = "git::https://PepsiCoIT@dev.azure.com/PepsiCoIT/EIP-Infrastructure/_git/eip-infra-terraform-modules//modules/key_vault_certificate"
  key_vault_certs          = var.key_vault_certs
  resource_name_to_create  = var.resource_name_to_create
  subscription             = var.subscription
  clientid                 = var.clientid
  clientsecret             = var.clientsecret
  tenantid                 = var.tenantid
}