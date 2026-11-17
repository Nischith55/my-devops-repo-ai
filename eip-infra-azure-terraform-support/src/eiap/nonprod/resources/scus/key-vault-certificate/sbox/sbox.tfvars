key_vault_certs = {
    sbox = {
        resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
        key_vault_name = "pe1001-eiap-infra-01-kv"

        certificate = {
            contents = "_.sbox.gw01.aks03.eus.nonprod.azure.intra.pepsico.com.pfx"
            password = "#{sbox}#"
        }

        tags = {
            department   = "EIAP"
            description  = "AKS cert"
            environment  = "nonprod"
            financialTag = "H-######"
            serviceName  = "EIP"
    }
    }
}