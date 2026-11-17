module "pvtep_preprod" {
  source                    = "git::https://PepsiCoIT@dev.azure.com/PepsiCoIT/EIP-Infrastructure/_git/eip-infra-terraform-modules//modules/private_endpoint"
  private_endpoint          = var.private_endpoint
  resource_name_to_create   = var.resource_name_to_create
  subscription              = var.subscription
  clientid                  = var.clientid
  clientsecret              = var.clientsecret
  tenantid                  = var.tenantid
}