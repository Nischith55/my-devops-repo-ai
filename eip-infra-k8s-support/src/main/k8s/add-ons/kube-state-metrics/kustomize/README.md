### Generating Kubernetes Manifests for kube-state-metrics

#### kube-state-metrics references
- [cli arguments](https://github.com/kubernetes/kube-state-metrics/blob/master/docs/cli-arguments.md#available-options)

#### Options for generating the manifest
Currently there are 2 options for generating the manifests (base)
- Straight from kube-state-metrics (preferred)
- From prometheus-community helm repository. Please use this to see what the
  generated manifests look like.

##### Option 1) download-files.sh (preferred)
Please update the download-files.sh for the version desired. And run it to get
the approriated manifests from github repository for kube-state-metrics

```bash
  $ chmod 755 src/main/k8s/add-ons/kube-state-metrics/kustomize/download-files.sh
  $ src/main/k8s/add-ons/kube-state-metrics/kustomize/download-files.sh
  # At this point the manifests should be available in <version>/base
```

##### Option 2) prometheus-community (helm chart) (do not use except for checking)

###### Pre-requisites

We will use the helm3 charts by prometheus community.

- Github Url [prometheus-community](https://github.com/prometheus-community/helm-charts)
- Use helm3 (commands below assume helm3 installation)

###### Setup helm3 repository

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

##### Generating the kubernetes that can be Kustomize.

- Create a values.yml (enclosed here)
- Then execute template --dry-run **important**
- Select a RELEASE otherwise it defaults to RELEASE-NAME, for eiap choose prefix

```bash
  # IMPORTANT we are using 'monitoring' namespace and release name as date 
  $ helm3 template -n monitoring -f values.yml --dry-run --include-crds <instance-name> prometheus-community/kube-state-metrics > kustomize/base/prometheus.yml
```

