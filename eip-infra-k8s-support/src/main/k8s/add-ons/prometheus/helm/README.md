## Generating Kubernetes Manifests for Prometheus Stack

We will use the helm3 charts by prometheus community.

- Github Url [prometheus-community](https://github.com/prometheus-community/helm-charts)
- Use helm3 (commands below assume helm3 installation)

### Setup helm3 repository

Adding the charts:

```bash
  $ helm3 repo add prometheus-community https://prometheus-community.github.io/helm-charts
  $ helm3 repo add stable https://charts.helm.sh/stable
  $ helm3 repo update
```

Some useful commands to show values:

```bash
  $ helm3 show values prometheus-community/prometheus
  # search shart repo
  $ helm3 search repo prometheus

```

### Prometheus Server Generating manifest before piping to kustomize 

- Create a values-eaip.yml (use values.yml as reference)
- Then execute template --dry-run **important**
- Select a RELEASE otherwise it defaults to RELEASE-NAME, use eiap
- please change <version> to what EIAP team version is

```bash
  # IMPORTANT we are using 'monitoring' namespace and release name as date 
  $ helm3 template -n monitoring -f values-eiap.yml --dry-run --include-crds eiap prometheus-community/prometheus > kustomize/server/<version>/prometheus.yml
```

### Prometheus Blackbox Exporter Generating manifest before piping to kustomize 

- Create a values-eaip.yml (use values.yml as reference)
- Then execute template --dry-run **important**
- Select a RELEASE otherwise it defaults to RELEASE-NAME, for eiap choose prefix

```bash
  # IMPORTANT we are using 'monitoring' namespace and release name as date 
  $ helm3 template -n monitoring -f <dir_where_this_file>/values-eiap.yml --dry-run --include-crds  eiap prometheus-community/prometheus-blackbox-exporter > kustomize/blackbox-exporter/<version>/prometheus-blackbox-exporter.yml
```
