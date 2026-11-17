federated_credential_ids = {
  "pep-pfna-cit-preprod-scus-pcaf-01-aks-fc" = {
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://southcentralus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/66e3dbe5-b1ca-4a84-ac60-dc93634bcbc3/"
    subject             = "system:serviceaccount:istio-system:pep-pfna-ingress-gw01-service-account"
    mi_name             = "pep-pfna-nonprod-infra-kv-01-mi"
  }
}
