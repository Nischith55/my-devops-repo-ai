key_vault_certs = {
    scmintrapepsicocomcert = {
        resource_group_name = "pep-hhnext-dev-eus-01-rg"
        key_vault_name = "pe1001-pfna-asenp-01-kv"

        certificate = {
            contents = "_.scm.intra.pepsico.com.pfx"
            password = "#{scm.intra.pepsico.com}#"
        }

        tags = {
            department   = "EIAP"
            description  = "ASE cert"
            environment  = "nonprod"
            financialTag = "H-######"
            serviceName  = "HHNEXT"
    }
    }
}