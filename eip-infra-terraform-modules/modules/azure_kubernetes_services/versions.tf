provider "azurerm" {
  alias                      = "provisioning"
  subscription_id            = var.subscription
  client_id                  = var.clientid
  client_secret              = var.clientsecret
  tenant_id                  = var.tenantid
  resource_provider_registrations = "none"
  features {}
}