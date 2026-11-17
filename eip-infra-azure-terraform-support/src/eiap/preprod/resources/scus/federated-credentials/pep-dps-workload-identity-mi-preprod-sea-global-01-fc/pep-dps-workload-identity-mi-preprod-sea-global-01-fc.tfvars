federated_credential_ids = {
  "pep-dps-workload-identity-mi-preprod-sea-global-01-fc" = {       
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"       
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://southeastasia.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/d75f5338-ea9f-4b1d-bdb6-a94858b46721/"
    subject             = "system:serviceaccount:istio-system:pep-dps-ingress-gw01-service-account" 
    mi_name             = "pep-dps-nonprod-infra-kv-01-mi"         
  }
}