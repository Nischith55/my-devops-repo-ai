terraform {
  backend "azurerm" {
    use_msi = true
  }
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "4.42.0"
    }
  }
}

provider "azurerm" {
  skip_provider_registration = true
  features {}
}
