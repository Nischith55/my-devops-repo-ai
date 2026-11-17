federated_credential_ids = {
  "pep-pepgenx-nonprod-eus-global-01-aks-buildagent-arc-fc" = {
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://eastus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/666b581f-7d75-4e42-b320-2d0846e5bb4c/"
    subject             = "system:serviceaccount:pep-pepgenx-global-devsecops-dev:pep-pepgenx-buildagent"
    mi_name             = "pep-aisp-nonprod-buildagent-arc-01-mi"
  }
}
