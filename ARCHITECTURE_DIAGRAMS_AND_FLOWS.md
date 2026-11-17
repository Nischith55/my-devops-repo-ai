# 📊 Comprehensive Architecture Diagrams & Flow Charts

---

## 1. COMPLETE END-TO-END INFRASTRUCTURE STACK

```
DEVELOPER                AZURE DEVOPS              AZURE CLOUD                  KUBERNETES CLUSTER
───────────             ─────────────             ────────────                  ──────────────────

     │                                                                                       
     │ commit                                                                               
     ├─────────────────►  Azure Pipelines                                                   
     │                    (CI/CD Engine)                                                    
     │                         │                                                            
     │                         │ trigger on:                                                
     │                         │ - Push to dev/qa/main                                      
     │                         ▼                                                            
     │                    ┌──────────────┐                                                  
     │                    │ Stage 1:     │                                                  
     │                    │ CI BUILD     │                                                  
     │                    │              │                                                  
     │                    │ • pytest     │                                                  
     │                    │ • coverage   │                                                  
     │                    │ • SonarQube  │                                                  
     │                    │ • Fortify    │                                                  
     │                    │ • Snyk       │                                                  
     │                    │ • Kaniko     │                                                  
     │                    └──────┬───────┘                                                  
     │                           │ BUILD SUCCESS                                            
     │                           ▼                                                          
     │                    Docker Image                                                      
     │                         │                                                            
     │                         │ Push to                                                    
     │                    ┌────▼──────────────┐                                             
     │                    │ Azure Container  │                                              
     │                    │ Registry (ACR)   │                                              
     │                    │                  │                                              
     │                    │ Tag: BuildNumber │                                              
     │                    │ e.g. 20240315.5  │                                              
     │                    └────┬──────────────┘                                             
     │                         │                                                            
     │                    ┌────▼───────────────────────────────┐                            
     │                    │ Stage 2-4: Deployment              │                            
     │                    │ (Dev/QA/Prod)                      │                            
     │                    │                                    │                            
     │                    │ • Clone manifest repo              │                            
     │                    │ • Update helm-values.yaml          │                            
     │                    │ • Create PR                        │                            
     │                    │ • Merge PR (auto/manual)           │                            
     │                    └────┬────────────────────────────────┘                           
     │                         │ Git Push                                                   
     │                         ▼                                                            
     │                    ┌──────────────────────────────┐                                  
     │                    │ GitOps Repository            │                                  
     │                    │ (potato-sourcing-            │                                  
     │                    │  argocd-configs)             │                                  
     │                    │                              │                                  
     │                    │ dev/                         │                                  
     │                    │  └── cluster/app/values.yaml │                                  
     │                    │ qa/                          │                                  
     │                    │  └── cluster/app/values.yaml │                                  
     │                    │ prod/                        │                                  
     │                    │  └── cluster/app/values.yaml │                                  
     │                    └──────┬───────────────────────┘                                  
     │                           │ Git Change                                               
     │                           ▼                                                          
     │                    ┌──────────────────┐                                              
     │                    │ ArgoCD           │                                              
     │                    │ (GitOps)         │                                              
     │                    │                  │                                              
     │                    │ • Detects change │                                              
     │                    │ • Renders Helm   │                                              
     │                    │ • Syncs to k8s   │                                              
     │                    └──────┬───────────┘                                              
     │                           │                                                          
     │                           │ Sync                                                    
     │                           ▼                                                          
     │        ┌──────────────────────────────────────────────────────────┐                  
     │        │  AZURE KUBERNETES CLUSTER (AKS)                         │                  
     │        │                                                          │                  
     │        │  ┌─────────────────────────────────────────────────┐   │                  
     │        │  │ NAMESPACE: pep-eiap-apps-{dev/qa/prod}         │   │                  
     │        │  │                                                 │   │                  
     │        │  │  ┌──────────────────────────────────────────┐  │   │                  
     │        │  │  │ POD DEPLOYMENT / STATEFULSET / ROLLOUT   │  │   │                  
     │        │  │  │                                          │  │   │                  
     │        │  │  │ ┌──────────────┐  ┌─────────────────┐   │  │   │                  
     │        │  │  │ │ Container:   │  │ Sidecar:        │   │  │   │                  
     │        │  │  │ │ potato-      │  │ Envoy Proxy     │   │  │   │                  
     │        │  │  │ │ sourcing-api │  │ (Istio)         │   │  │   │                  
     │        │  │  │ │              │  │                 │   │  │   │                  
     │        │  │  │ │ Image:       │  │ + APM agent     │   │  │   │                  
     │        │  │  │ │ ACR:tag:     │  │ (AppDynamics)   │   │  │   │                  
     │        │  │  │ │ 20240315.5   │  │                 │   │  │   │                  
     │        │  │  │ └──────────────┘  └─────────────────┘   │  │   │                  
     │        │  │  │                                          │  │   │                  
     │        │  │  │ ┌──────────────────────────────────────┐ │  │   │                  
     │        │  │  │ │ Readiness/Liveness Probes            │ │  │   │                  
     │        │  │  │ │ Health Checks ✓                      │ │  │   │                  
     │        │  │  │ └──────────────────────────────────────┘ │  │   │                  
     │        │  │  └──────────────────────────────────────────┘  │   │                  
     │        │  │                                                 │   │                  
     │        │  │  ┌──────────────────────────────────────────┐  │   │                  
     │        │  │  │ SERVICE: potato-sourcing-api            │  │   │                  
     │        │  │  │ Type: ClusterIP                         │  │   │                  
     │        │  │  │ Port: 8000                              │  │   │                  
     │        │  │  └──────────────────────────────────────────┘  │   │                  
     │        │  │                                                 │   │                  
     │        │  │  ┌──────────────────────────────────────────┐  │   │                  
     │        │  │  │ STORAGE (if enabled)                    │  │   │                  
     │        │  │  │ PVC → PV → Azure Disk / File Share      │  │   │                  
     │        │  │  └──────────────────────────────────────────┘  │   │                  
     │        │  │                                                 │   │                  
     │        │  │  ┌──────────────────────────────────────────┐  │   │                  
     │        │  │  │ SECRETS (Key Vault Integration)         │  │   │                  
     │        │  │  │ CSI Driver → /mnt/secrets-store         │  │   │                  
     │        │  │  │ - DATABASE_PASSWORD                     │  │   │                  
     │        │  │  │ - API_KEY                               │  │   │                  
     │        │  │  │ - SSL_CERTIFICATE                       │  │   │                  
     │        │  │  └──────────────────────────────────────────┘  │   │                  
     │        │  └─────────────────────────────────────────────────┘   │                  
     │        │                                                          │                  
     │        │  ┌─────────────────────────────────────────────────┐   │                  
     │        │  │ ISTIO SERVICE MESH                            │   │                  
     │        │  │                                                │   │                  
     │        │  │ • VirtualService: Routing rules              │   │                  
     │        │  │ • DestinationRule: Load balancing            │   │                  
     │        │  │ • EnvoyFilter: Custom proxy logic            │   │                  
     │        │  │ • Gateway: Ingress controller                │   │                  
     │        │  └─────────────────────────────────────────────────┘   │                  
     │        │                                                          │                  
     │        │  ┌─────────────────────────────────────────────────┐   │                  
     │        │  │ AUTOSCALING                                   │   │                  
     │        │  │                                                │   │                  
     │        │  │ • HPA: Min=2, Max=10, Target CPU=70%         │   │                  
     │        │  │ • KEDA: Kafka/Redis/EventHub triggers        │   │                  
     │        │  │ • PDB: Minimum 1 pod always available        │   │                  
     │        │  └─────────────────────────────────────────────────┘   │                  
     │        │                                                          │                  
     │        │  ┌─────────────────────────────────────────────────┐   │                  
     │        │  │ DEPLOYMENT STRATEGY                           │   │                  
     │        │  │                                                │   │                  
     │        │  │ IF Dev/QA: Standard rolling update            │   │                  
     │        │  │ IF Prod: Canary (Argo Rollouts)               │   │                  
     │        │  │   - 20% → 40% → 60% → 80% → 100%            │   │                  
     │        │  │   - AnalysisTemplate monitors metrics         │   │                  
     │        │  │   - Auto-promote if metrics OK                │   │                  
     │        │  │   - Automatic rollback if failed              │   │                  
     │        │  └─────────────────────────────────────────────────┘   │                  
     │        │                                                          │                  
     │        │  ┌─────────────────────────────────────────────────┐   │                  
     │        │  │ MONITORING & OBSERVABILITY                    │   │                  
     │        │  │                                                │   │                  
     │        │  │ • Prometheus: Metrics collection              │   │                  
     │        │  │ • AppDynamics: APM tracing                    │   │                  
     │        │  │ • Jaeger: Distributed tracing                 │   │                  
     │        │  │ • Kiali: Service mesh visualization           │   │                  
     │        │  │ • Azure Monitor: Logs & alerts                │   │                  
     │        │  │ • Grafana: Dashboard visualization            │   │                  
     │        │  └─────────────────────────────────────────────────┘   │                  
     │        └──────────────────────────────────────────────────────────┘                  
     │                                                                                       
     │ ◄─────────────────────────── MONITORING FEEDBACK ─────────────────────────────────   
     │                                                                                       
     └─► VIEW IN: Azure Portal, Grafana, AppDynamics, Kiali dashboards                      
```

---

## 2. CI/CD PIPELINE STAGE FLOW

```
CODE COMMIT
    │
    │ trigger: branches=[dev, qa, main]
    │
    ▼
┌─────────────────────────────────────────┐
│  AZURE DEVOPS PIPELINES                 │
│  (azure-pipeline.yaml / Spring-CICD.yaml)│
└────────┬────────────────────────────────┘
         │
         ├─────────────────────────────────────────────────────┐
         │                                                     │
         ▼                                                     ▼
    ┌─────────────────────────┐                    ┌──────────────────────┐
    │ STAGE 1: CI_BUILD       │                    │ POOL AGENT           │
    │ (Only if NOT deployOnly)│                    │ Self-Hosted (Shared) │
    │                         │                    │ Location: EUS        │
    └────────┬────────────────┘                    └──────────────────────┘
             │
             ├─► STEP 1: Dependencies
             │   ├─ pip install -r requirements.txt
             │   └─ python3 --version
             │
             ├─► STEP 2: Unit Tests
             │   ├─ python3 -m pytest
             │   └─ python3 -m coverage run
             │
             ├─► STEP 3: SonarQube Analysis
             │   ├─ Task: SonarQubePrepare
             │   ├─ Config: Manual mode
             │   ├─ Project Key: potato-sourcing-matrix-api
             │   ├─ Quality Gate: PASS ✓ (blocks if fail)
             │   └─ Gate Wait: sonar.qualitygate.wait=true
             │
             ├─► STEP 4: Fortify SAST Scan
             │   ├─ Tool: FortifyScanCentral
             │   ├─ Controller: https://csc.pepasm.net/scancentral-ctrl
             │   ├─ SSC Endpoint: https://ssc.pepasm.net/ssc
             │   ├─ Severity: Critical/High blocks
             │   └─ Upload: YES (to SSC)
             │
             ├─► STEP 5: Snyk Vulnerability Scan
             │   ├─ Auth Token: $(SNYK_AUTH_TOKEN)
             │   ├─ Organization: $(orgid)
             │   ├─ Scan Type: Container + dependencies
             │   ├─ Image: ACR image (latest build)
             │   └─ Action: Monitor (report vulnerabilities)
             │
             ├─► STEP 6: Docker Image Build (Kaniko)
             │   ├─ Method: Kaniko (no Docker daemon)
             │   ├─ Location: In-cluster PVC
             │   ├─ Dockerfile Path: ./Dockerfile
             │   ├─ Image Destination:
             │   │   $(npglobalacrurl)/$(acrrepoprefix)/$(acrreponame):$(Build.BuildNumber)
             │   │   = pepeiapnonprodcommonacr.azurecr.io/pep/eiap/potato-sourcing-matrix-api:20240315.5
             │   ├─ Steps:
             │   │   1. Clone git repo
             │   │   2. Create Kaniko Job from template
             │   │   3. kubectl create job_template_kaniko.yaml
             │   │   4. Wait: kubectl wait --for=condition=complete --timeout=20m
             │   │   5. Retrieve logs
             │   │   6. Delete job & cleanup PVC
             │   └─ Timeout: 20 minutes
             │
             ├─► STEP 7: Push to ACR
             │   ├─ Image Pushed: ✓ pepeiapnonprodcommonacr.azurecr.io/.../potato-sourcing-matrix-api:20240315.5
             │   └─ Available for: Dev/QA/Prod deployment
             │
             └─► STEP 8: Publish Build Artifacts
                 ├─ Artifact Name: drop
                 ├─ Contents:
                 │   ├─ Build logs
                 │   ├─ Test reports
                 │   ├─ Coverage XML
                 │   └─ Deployment config
                 └─ Location: $(build.artifactstagingdirectory)
                     └─ Available for: Deploy stages

             ◄──── CI_BUILD SUCCESS ────►
             │
             ├─ Set Output: BUILD_STATUS = SUCCESS
             └─ Set Variable: IMAGE_TAG = 20240315.5


┌────────────────────────────────────────────────────────────┐
│  DECISION: Which environments to deploy?                  │
│                                                            │
│  IF branch = dev/feature                                  │
│     └─► AUTO Deploy to DEV                                │
│                                                            │
│  ELSE IF branch = qa                                      │
│     └─► AUTO Deploy to DEV + QA                           │
│                                                            │
│  ELSE IF branch = main (release)                          │
│     └─► AUTO Deploy to DEV + QA                           │
│     └─► WAIT Deploy to PROD (manual approval)             │
└────────────────────────────────────────────────────────────┘

                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
    ┌─────────────┐ ┌──────────────┐ ┌──────────────────┐
    │ STAGE 2:    │ │ STAGE 3:     │ │ STAGE 4:         │
    │ DEV Deploy  │ │ QA Deploy    │ │ PROD Approval    │
    │ (Auto)      │ │ (Auto)       │ │ (Manual)         │
    │             │ │              │ │                  │
    │Depends on:  │ │ Depends on:  │ │ Depends on:      │
    │CI_Build:OK  │ │ CI_Build:OK  │ │ CI_Build:OK      │
    │             │ │              │ │ CR#: Required    │
    │             │ │              │ │ Branch: main     │
    │             │ │              │ │                  │
    │Pool:        │ │ Pool:        │ │ Pool: Prod       │
    │EUS-Shared   │ │ EUS-Shared   │ │ SCUS-Prod        │
    └─────────────┘ │ ┌──────────────┘ │                  
        │           │ │                │                  
        ▼           ▼ ▼                ▼                  
    ┌────────────────────────┐    ┌──────────────────────┐
    │ DEPLOYMENT STEPS       │    │ APPROVAL STEP        │
    │ (Same for all envs)    │    │                      │
    │                        │    │ Task:                │
    │ 1. Install kubelogin   │    │ pipelineapproval.yaml│
    │ 2. Download artifacts  │    │                      │
    │ 3. Clone manifest repo │    │ Action:              │
    │ 4. Check deploy file   │    │ WAIT for Human       │
    │ 5. Update tag in yaml  │    │ Review               │
    │ 6. Commit & push       │    │                      │
    │ 7. Create PR           │    │ Approvers:           │
    │ 8. Merge PR (auto)     │    │ • Change Manager     │
    │ 9. ArgoCD syncs        │    │ • Security Team      │
    │                        │    │ • Ops Lead           │
    └────────────────────────┘    │                      │
                                  │ Decision:            │
                                  │ ✓ APPROVE or         │
                                  │ ✗ REJECT             │
                                  └──────────────────────┘
                                        │
                    ┌───────────────────┴───────────────────┐
                    │                                       │
                    ▼ APPROVED                      ▼ REJECTED
            ┌──────────────────┐              ┌──────────────┐
            │ STAGE 5: PROD    │              │ Pipeline     │
            │ Deployment       │              │ STOPS        │
            │                  │              │              │
            │ Action: ACR Copy │              │ No Prod      │
            │ - Import Image   │              │ Deployment   │
            │   nonprod → prod │              │              │
            │ - Update yaml    │              │ Notify:      │
            │ - Create PR      │              │ Team         │
            │ - Merge PR       │              └──────────────┘
            │ - ArgoCD syncs   │
            │                  │
            │ Strategy:        │
            │ Canary Rollout   │
            │ (if enabled)     │
            │                  │
            └──────────┬───────┘
                       │
                       ▼
            ┌────────────────────────┐
            │ ARGO ROLLOUT STARTS    │
            │                        │
            │ Version: old → new     │
            │ Traffic: 0% → 100%     │
            │                        │
            │ Step 1: 20% (5 min)   │
            │   └─ Monitor metrics   │
            │                        │
            │ Step 2: 40% (5 min)   │
            │   └─ Monitor metrics   │
            │                        │
            │ Step 3: 60% (5 min)   │
            │   └─ Monitor metrics   │
            │                        │
            │ Step 4: 80% (5 min)   │
            │   └─ Monitor metrics   │
            │                        │
            │ Step 5: 100%          │
            │   └─ Completion       │
            │                        │
            │ IF metrics GOOD:      │
            │   └─ ✓ PROMOTE        │
            │       Old version     │
            │       terminated      │
            │                        │
            │ IF metrics FAIL:      │
            │   └─ ✗ ROLLBACK       │
            │       New version     │
            │       terminated      │
            │       Old version     │
            │       restored        │
            └────────────────────────┘

                       │
                       ▼
         ┌─────────────────────────────────┐
         │ MONITORING POST-DEPLOYMENT      │
         │                                 │
         │ • Prometheus metrics ✓ STABLE   │
         │ • AppDynamics APM ✓ NORMAL      │
         │ • Error rate ✓ < 0.1%           │
         │ • Latency ✓ < 500ms p95         │
         │ • Kiali mesh ✓ HEALTHY          │
         │ • Jaeger traces ✓ NORMAL        │
         │ • Alerts ✓ NO CRITICAL          │
         │                                 │
         │ Status: ✓ GREEN (Deployment OK) │
         └─────────────────────────────────┘
```

---

## 3. HELM CHART RENDERING FLOW

```
User runs:
  helm install -f values-prod.yaml \
               -f values-bluegreen.yaml \
               potato-sourcing ./umbrellachart

                           │
                           ▼
        ┌──────────────────────────────────────┐
        │ UMBRELLACHART Chart.yaml             │
        │ version: 2.2.4-cronjob               │
        │                                      │
        │ dependencies:                        │
        │  - app-chart v1.3.2                  │
        │  - platform-chart v1.3.3             │
        │                                      │
        │ condition: app-chart.enabled = true  │
        │ condition: platform-chart.enabled    │
        └──────────────────────────────────────┘
                           │
                ┌──────────┴──────────┐
                │                     │
                ▼                     ▼
    ┌─────────────────────┐  ┌──────────────────────┐
    │ APP-CHART           │  │ PLATFORM-CHART       │
    │ v1.3.2              │  │ v1.3.3               │
    │                     │  │                      │
    │ Templates/          │  │ Templates/           │
    │ - deployment.yaml   │  │ - hpa.yaml           │
    │ - rollout.yaml      │  │ - pdb.yaml           │
    │ - service.yaml      │  │ - virtualservice.yaml│
    │ - cronjob.yaml      │  │ - destinationrule.yaml
    │ - configmap.yaml    │  │ - envoyfilter.yaml   │
    │ - serviceaccount.yaml│ │ - kedascaledobject.yaml
    │ - experiment.yaml   │  │ - pv.yaml            │
    │ - statefulset.yaml  │  │ - pvc.yaml           │
    │ - _helpers.tpl      │  │ - storageclass.yaml  │
    │                     │  │ - secretProviderClass.yaml
    │ Renders:            │  │ - gw-patch-job.yaml  │
    │                     │  │ - _helpers.tpl       │
    │ ┌─────────────────┐ │  │                      │
    │ │ Deployment      │ │  │ Renders:             │
    │ │ spec:           │ │  │                      │
    │ │   image: ACR:.  │ │  │ ┌──────────────────┐ │
    │ │   replicas: 3   │ │  │ │ HPA              │ │
    │ │   resources:    │ │  │ │ minReplicas: 2   │ │
    │ │     limits:     │ │  │ │ maxReplicas: 10  │ │
    │ │     1024Mi      │ │  │ │ targetCPU: 70%   │ │
    │ └─────────────────┘ │  │ └──────────────────┘ │
    │                     │  │                      │
    │ ┌─────────────────┐ │  │ ┌──────────────────┐ │
    │ │ Service         │ │  │ │ VirtualService   │ │
    │ │ spec:           │ │  │ │ hosts: [API]     │ │
    │ │   type: ClusterIP│ │  │ │ routes:          │ │
    │ │   port: 8000    │ │  │ │   /api → v1 100% │ │
    │ │   selector:     │ │  │ │ retries:         │ │
    │ │     app: potato │ │  │ │   attempts: 3    │ │
    │ └─────────────────┘ │  │ └──────────────────┘ │
    │                     │  │                      │
    │ ┌─────────────────┐ │  │ ┌──────────────────┐ │
    │ │ Rollout         │ │  │ │ DestinationRule  │ │
    │ │ strategy:       │ │  │ │ subsets:         │ │
    │ │   blueGreen     │ │  │ │   - v1           │ │
    │ │ blueGreen:      │ │  │ │ trafficPolicy:   │ │
    │ │   preview: 3    │ │  │ │   outlier:       │ │
    │ │   autoPromo: T  │ │  │ │     5xx: 5 errors│ │
    │ │   autoPromoSecs│ │  │ │     baseEject: 30│ │
    │ │     : 30        │ │  │ │ s                │ │
    │ └─────────────────┘ │  │ └──────────────────┘ │
    │                     │  │                      │
    │ ┌─────────────────┐ │  │ ┌──────────────────┐ │
    │ │ ConfigMap       │ │  │ │ KEDA Scaled      │ │
    │ │ data:           │ │  │ │ Object           │ │
    │ │   APP_ENV: prod │ │  │ │ triggers:        │ │
    │ │   LOG_LEVEL:    │ │  │ │   - kafka:       │ │
    │ │     INFO        │ │  │ │     lagThreshold │ │
    │ └─────────────────┘ │  │ │     : 100        │ │
    │                     │  │ └──────────────────┘ │
    │ ┌─────────────────┐ │  │                      │
    │ │ ServiceAccount  │ │  │ ┌──────────────────┐ │
    │ │ metadata:       │ │  │ │ PDB              │ │
    │ │   name: potato  │ │  │ │ minAvailable: 1  │ │
    │ │                 │ │  │ │                  │ │
    │ └─────────────────┘ │  │ └──────────────────┘ │
    └─────────────────────┘  └──────────────────────┘
                │                     │
                │                     │
                └─────────────┬───────┘
                              │
                              ▼
                ┌──────────────────────────────┐
                │ VALUES OVERRIDE HIERARCHY    │
                │                              │
                │ FINAL VALUES = base +        │
                │   values-prod.yaml +         │
                │   values-bluegreen.yaml      │
                │                              │
                │ Merged in order:             │
                │ 1. umbrellachart/values.yaml │
                │ 2. app-chart/values.yaml     │
                │ 3. platform-chart/values.yaml│
                │ 4. values-prod.yaml          │
                │ 5. values-bluegreen.yaml     │
                └──────────────────────────────┘
                              │
                              ▼
                ┌──────────────────────────────┐
                │ HELM TEMPLATE ENGINE         │
                │                              │
                │ Process all templates with:  │
                │ - Global values              │
                │ - Merged overrides           │
                │ - Conditional blocks (if)    │
                │ - Loops (range)              │
                │ - Helper functions           │
                │                              │
                │ Output: Raw YAML manifests   │
                └──────────────────────────────┘
                              │
                              ▼
                ┌──────────────────────────────┐
                │ FINAL KUBERNETES MANIFESTS   │
                │                              │
                │ Generated files:             │
                │                              │
                │ deployment.yaml              │
                │ service.yaml                 │
                │ hpa.yaml                     │
                │ pdb.yaml                     │
                │ virtualservice.yaml          │
                │ destinationrule.yaml         │
                │ kedascaledobject.yaml        │
                │ configmap.yaml               │
                │ serviceaccount.yaml          │
                │ ... and more                 │
                └──────────────────────────────┘
                              │
                              ▼
                ┌──────────────────────────────┐
                │ HELM INSTALLS TO CLUSTER     │
                │                              │
                │ kubectl apply {manifests}    │
                │                              │
                │ Objects created in namespace:│
                │ pep-eiap-apps-prod           │
                │                              │
                │ Status: All resources synced │
                └──────────────────────────────┘
```

---

## 4. ARGOCD GITOPS SYNC FLOW

```
┌────────────────────────────────────────────────────────────────┐
│ DEVELOPER / CI PIPELINE                                        │
│                                                                │
│ Updates Git:                                                   │
│  git add dev/cluster/potato-sourcing-matrix-api/helm-values.yaml
│  git commit -m "deployment 20240315.5"                        │
│  git push origin dev                                          │
└────────────────────────┬───────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────────┐
         │ GitOps Repository (Git)           │
         │ potato-sourcing-argocd-configs    │
         │                                   │
         │ Structure:                        │
         │ dev/                              │
         │  └── pep-eiap-nonprod-eus-global-01-aks/
         │       └── potato-sourcing-matrix-api/
         │            └── helm-values.yaml   │
         │                tag: 20240315.5    │
         │                replicas: 3        │
         │                resources: ...     │
         └────────┬────────────────────────┘
                  │ Git webhook
                  │ (Polling every 3min)
                  ▼
         ┌───────────────────────────────────┐
         │ ARGOCD CONTROLLER                 │
         │ (Running in pep-eiap-argocd ns)   │
         │                                   │
         │ Action: Detect Change             │
         │ - Poll Git repo                   │
         │ - Compare desired vs actual       │
         │ - Status: OUT_OF_SYNC             │
         └────────┬────────────────────────┘
                  │
                  ▼
         ┌───────────────────────────────────┐
         │ HELM TEMPLATE ENGINE              │
         │ (Inside ArgoCD)                   │
         │                                   │
         │ Input: helm-values.yaml           │
         │ Input: umbrellachart/             │
         │                                   │
         │ Process:                          │
         │ 1. Load base values.yaml          │
         │ 2. Merge helm-values.yaml         │
         │ 3. Render templates               │
         │ 4. Generate manifests             │
         │                                   │
         │ Output: Final YAML manifests      │
         └────────┬────────────────────────┘
                  │
                  ▼
         ┌───────────────────────────────────┐
         │ SYNC STRATEGY                     │
         │                                   │
         │ Policy: Auto (if enabled)         │
         │ - Automatically sync              │
         │ - Don't wait for manual approval  │
         │                                   │
         │ Pruning: Enabled                  │
         │ - Delete k8s objects not in Git   │
         │                                   │
         │ Self-Healing: Enabled             │
         │ - Reconcile if manual changes     │
         └────────┬────────────────────────┘
                  │
                  ▼
         ┌───────────────────────────────────┐
         │ SYNC TO KUBERNETES                │
         │                                   │
         │ kubectl apply -f manifests.yaml   │
         │                                   │
         │ Actions:                          │
         │ 1. Create/Update Deployment       │
         │ 2. Create/Update Service          │
         │ 3. Create/Update ConfigMap        │
         │ 4. Create/Update Secrets (ref)    │
         │ 5. Create/Update HPA              │
         │ 6. Create/Update VirtualService   │
         │ 7. Create/Update DestinationRule  │
         │ 8. Create/Update PDB              │
         │ 9. ... (all manifests)            │
         │                                   │
         │ Namespace: pep-eiap-apps-dev      │
         └────────┬────────────────────────┘
                  │
                  ▼
    ┌──────────────────────────────────────────┐
    │ KUBERNETES CLUSTER                       │
    │                                          │
    │ Deployment Controller:                   │
    │ - Sees new image tag: 20240315.5        │
    │ - Creates new ReplicaSet                 │
    │ - Scales up new pods                     │
    │ - Health checks (readiness/liveness)     │
    │                                          │
    │ Pod Status:                              │
    │ 1. Init containers: ✓ COMPLETE         │
    │ 2. App container: ▶ RUNNING            │
    │ 3. Sidecar (Envoy): ▶ RUNNING          │
    │ 4. Readiness probe: ✓ PASS             │
    │ 5. Liveness probe: ✓ PASS              │
    │                                          │
    │ Service endpoint: Active ✓              │
    │ Traffic: Routing to new pods ✓          │
    │                                          │
    │ Deployment Status:                       │
    │ Replicas: 3 Ready, 3 Updated            │
    │                                          │
    └────────┬─────────────────────────────────┘
             │
             ▼
    ┌──────────────────────────────────────────┐
    │ ARGOCD SYNC COMPLETE                     │
    │                                          │
    │ Status: ✓ SYNCED                        │
    │ Health: ✓ HEALTHY                       │
    │ Message: Deployment successful          │
    │                                          │
    │ Timestamp: 2024-03-15 10:45:30          │
    └────────┬─────────────────────────────────┘
             │
             ▼
    ┌──────────────────────────────────────────┐
    │ MONITORING POST-SYNC                     │
    │                                          │
    │ ArgoCD UI:                               │
    │ - Application: SYNCED ✓                  │
    │ - Deployment: HEALTHY ✓                  │
    │                                          │
    │ Metrics Observed:                        │
    │ - Pod CPU: 45% (within limits)          │
    │ - Pod Memory: 256MB (within limits)     │
    │ - Request latency: 150ms (normal)       │
    │ - Error rate: 0% (healthy)              │
    │                                          │
    │ Result: Deployment ✓ SUCCESSFUL         │
    └──────────────────────────────────────────┘
```

---

## 5. ISTIO SERVICE MESH TRAFFIC FLOW

```
CLIENT REQUEST
    │
    │ https://potato-sourcing-matrix-api.eiap.pepsico.io/api/v1/sourcing
    │
    ▼
┌────────────────────────────────────────────┐
│ ISTIO INGRESS GATEWAY                      │
│ (Deployed in istio-system namespace)       │
│                                            │
│ Gateway CRD:                               │
│   name: main-gateway                       │
│   namespace: pep-eiap                      │
│   selector: istio=ingressgateway           │
│                                            │
│ Server Config:                             │
│   port: 443 (HTTPS)                        │
│   tls:                                     │
│     mode: SIMPLE                           │
│     credentialName: main-gateway-cert      │
│   hosts:                                   │
│     - *.eiap.pepsico.io                    │
│     - *.pepsico.io                         │
└────────┬───────────────────────────────────┘
         │ TLS termination
         │ (SSL/TLS handshake)
         │
         ▼
┌────────────────────────────────────────────┐
│ ENVOY PROXY (Sidecar Proxy)                │
│ (Inbound listener on port 15000)           │
│                                            │
│ Receives: Decrypted HTTP request           │
│ Host: potato-sourcing-matrix-api           │
│ Path: /api/v1/sourcing                     │
│ Method: GET                                │
│                                            │
│ Listener Chain:                            │
│  1. HTTP/1.1 connection pool               │
│  2. Routes → Match Rules                   │
│  3. Apply Filters                          │
│  4. Add Headers (CORS, etc.)               │
│  5. Apply Retry Logic                      │
│  6. Connect to Destination                 │
└────────┬───────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────┐
│ VIRTUALSERVICE (Routing Rules)                 │
│ Name: potato-sourcing-matrix-api               │
│ Namespace: pep-eiap-apps                       │
│                                                │
│ http:                                          │
│  - match:                                      │
│      uri:                                      │
│        prefix: "/api"                          │
│    route:                                      │
│      - destination:                            │
│          host: potato-sourcing-matrix-api      │
│          subset: v1                            │
│        weight: 100 (or graduated in canary)    │
│    timeout: 10s                                │
│    retries:                                    │
│      attempts: 3                               │
│      perTryTimeout: 5s                         │
│    corsPolicy:                                 │
│      allowOrigins:                             │
│        - exact: https://ui.eiap.pepsico.io    │
│      allowMethods: [GET, POST, PUT]           │
│      allowHeaders: [content-type, auth]       │
│                                                │
│ Matching Result:                               │
│  ✓ URI matches /api prefix                     │
│  ✓ Route to: potato-sourcing-matrix-api:v1    │
│  ✓ Weight: 100%                                │
│  ✓ Apply: Timeout (10s), Retries (3x)         │
└────────┬────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ DESTINATIONRULE (Load Balancing)           │
│ Name: potato-sourcing-matrix-api           │
│                                            │
│ subsets:                                   │
│   - name: v1                               │
│     labels:                                │
│       version: v1                          │
│                                            │
│ trafficPolicy:                             │
│   connectionPool:                          │
│     tcp:                                   │
│       maxConnections: 100                  │
│     http:                                  │
│       http1MaxPendingRequests: 100         │
│       maxRequestsPerConnection: 10         │
│   outlierDetection:                        │
│     consecutive5xxErrors: 5                │
│     interval: 30s                          │
│     baseEjectionTime: 30s                  │
│     maxEjectionPercent: 100                │
│     minRequestVolume: 10                   │
│                                            │
│ Load Balancing Algorithm: ROUND_ROBIN     │
│ (default)                                  │
│                                            │
│ Subset v1 Resolution:                      │
│  - Select pods with label version=v1      │
│  - Found: 3 pods                           │
│    1. potato-sourcing-pod-1                │
│    2. potato-sourcing-pod-2                │
│    3. potato-sourcing-pod-3                │
└────────┬────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ OUTLIER DETECTION LOGIC                    │
│ (Continuous monitoring)                    │
│                                            │
│ Rules:                                     │
│  - If 5 consecutive 5xx errors → eject    │
│  - Check interval: 30s                     │
│  - Ejection time: 30s                      │
│  - Max ejected: 100%                       │
│  - Minimum traffic: 10 requests            │
│                                            │
│ Current Pods:                              │
│  1. pod-1: 200 (OK) ✓                      │
│  2. pod-2: 200 (OK) ✓                      │
│  3. pod-3: 200 (OK) ✓                      │
│                                            │
│ Status: All healthy, no ejections          │
└────────┬────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ LOAD BALANCER (Round Robin)                │
│                                            │
│ Available Pods:                            │
│  1. potato-sourcing-pod-1:8000             │
│  2. potato-sourcing-pod-2:8000             │
│  3. potato-sourcing-pod-3:8000             │
│                                            │
│ Rotation:                                  │
│  Request 1 → pod-1 ✓                       │
│  Request 2 → pod-2 ✓                       │
│  Request 3 → pod-3 ✓                       │
│  Request 4 → pod-1 ✓                       │
│  ...                                       │
│                                            │
│ Selected Pod: pod-1 (Turn 1 of 3)          │
└────────┬────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ SERVICE (Kubernetes) - Headless for Istio │
│ Name: potato-sourcing-matrix-api           │
│ Type: ClusterIP (or Headless)              │
│ Port: 8000                                 │
│                                            │
│ Endpoints:                                 │
│  - 10.240.1.10:8000 (pod-1)               │
│  - 10.240.1.11:8000 (pod-2)               │
│  - 10.240.1.12:8000 (pod-3)               │
│                                            │
│ Proxy forwards to: 10.240.1.10:8000       │
└────────┬────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ APPLICATION POD-1                          │
│                                            │
│ Container: potato-sourcing-api            │
│ Image: ...:20240315.5                     │
│ Port: 8000                                │
│                                            │
│ Process Request:                           │
│  GET /api/v1/sourcing                      │
│  ├─ Auth: Check header                     │
│  ├─ Route: /api/v1/sourcing → handler     │
│  ├─ Query DB: SELECT ...                   │
│  ├─ Build response: JSON                   │
│  └─ Return: 200 OK + body                  │
│                                            │
│ Sidecar: Envoy (Istio proxy)              │
│  ├─ Intercepts inbound traffic            │
│  ├─ Injects tracing headers (Jaeger)      │
│  ├─ Records metrics (Prometheus)          │
│  ├─ APM agent (AppDynamics sidecar)       │
│  └─ Logs requests                         │
│                                            │
└────────┬────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ RESPONSE: 200 OK                           │
│ Body: JSON list of sourcing data           │
│                                            │
│ Trace:                                     │
│  Headers Added:                            │
│    x-trace-id: abc123...                   │
│    x-span-id: def456...                    │
│                                            │
│ Metrics Recorded:                          │
│  - http_requests_total{status=200}         │
│  - http_request_duration_seconds (150ms)  │
│  - http_requests_by_status_code            │
│                                            │
│ Logs:                                      │
│  2024-03-15 10:45:30 GET /api/v1/sourcing  │
│  Status: 200, Duration: 150ms              │
│                                            │
└────────┬────────────────────────────────────┘
         │
         ▼
         RESPONSE SENT TO CLIENT
         ✓ Success
         ✓ Latency: 150ms
         ✓ Metrics collected
         ✓ Trace recorded
         ✓ Logged
```

---

## 6. DEPLOYMENT STRATEGY COMPARISON

```
┌─────────────────────────────────────────────────────────────────────┐
│ DEPLOYMENT STRATEGY COMPARISON                                      │
└─────────────────────────────────────────────────────────────────────┘

╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║  STRATEGY 1: STANDARD ROLLING DEPLOYMENT (Dev/QA)                   ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝

  TIME ──────────────────────────────────────────────────────────────►
   0%  │ ▓▓▓▓▓  (3 old pods running)
       │
   10% │ ▓▓▓   ░░  (2 old, 1 new)
       │
   20% │ ▓▓   ░░░  (2 old, 2 new)
       │
   30% │ ▓   ░░░░  (1 old, 3 new)
       │
   40% │     ░░░░░  (0 old, 3 new) - Complete
       │
  100% │ ✓ DEPLOYMENT COMPLETE
       │
   Components Used:
   • Deployment (standard Kubernetes)
   • Rolling update strategy (1 pod at a time)
   • No metrics analysis
   • No automatic rollback (manual only)
   
   Rollback Process:
   helm rollback <release>


╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║  STRATEGY 2: CANARY DEPLOYMENT (Prod with Argo Rollouts)            ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝

  TIME ──────────────────────────────────────────────────────────────►
   
  Phase 1 - Traffic 20%
   0%  │ ▓▓▓▓▓▓▓▓▓  (9 old pods: 90% traffic)
       │ ░         (1 new pod: 10% traffic - WAIT)
       │
   5%  │ Metrics Check:
       │  • Success rate: 99.8% ✓
       │  • Latency p95: 145ms ✓
       │  • Error rate: 0% ✓
       │ → PROCEED TO NEXT STEP
       │
  
  Phase 2 - Traffic 40%
  10%  │ ▓▓▓▓▓▓   (6 old pods: 60% traffic)
       │ ░░░░     (4 new pods: 40% traffic - WAIT)
       │
  15%  │ Metrics Check:
       │  • Success rate: 99.9% ✓
       │  • Latency p95: 150ms ✓
       │  • Error rate: 0% ✓
       │ → PROCEED TO NEXT STEP
       │
  
  Phase 3 - Traffic 60%
  20%  │ ▓▓▓      (3 old pods: 40% traffic)
       │ ░░░░░░   (7 new pods: 60% traffic - WAIT)
       │
  25%  │ Metrics Check:
       │  • Success rate: 99.85% ✓
       │  • Latency p95: 148ms ✓
       │  • Error rate: 0.1% ✓
       │ → PROCEED TO NEXT STEP
       │
  
  Phase 4 - Traffic 80%
  30%  │ ▓       (1 old pod: 20% traffic)
       │ ░░░░░░░░░  (9 new pods: 80% traffic - WAIT)
       │
  35%  │ Metrics Check:
       │  • Success rate: 99.75% ✓
       │  • Latency p95: 155ms ✓
       │  • Error rate: 0.2% ✓
       │ → PROCEED TO FINAL
       │
  
  Phase 5 - Traffic 100%
  40%  │         (0 old pods)
       │ ░░░░░░░░░░  (10 new pods: 100% traffic)
       │
  45%  │ ✓ PROMOTION COMPLETE
       │   Old version terminated
       │
  100% │ ✓ CANARY ROLLOUT COMPLETE
       │
   Features:
   • Argo Rollouts CRD
   • Progressive traffic shift
   • Automated metric analysis
   • AnalysisTemplate monitors health
   • Automatic promotion on success
   • Automatic rollback on failure
   
   Analysis Template Triggers:
   - If error_rate > 5% → ROLLBACK
   - If latency_p95 > 500ms → ROLLBACK
   - If success_rate < 95% → ROLLBACK
   
   Rollback Process (Automatic):
   1. Analysis fails
   2. AnalysisRun sets result: FAILED
   3. Argo Rollout detects failure
   4. Shifts traffic back to old version
   5. New version terminated
   6. Deployment restored


╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║  STRATEGY 3: BLUE-GREEN DEPLOYMENT (Argo Rollouts)                  ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝

  PHASE 1 - BLUE ACTIVE (Current Production)
  
  TIME ──────────────────────────────────────────────────────────────►
   0%  │ ▓▓▓▓▓▓▓▓▓▓  BLUE (10 pods - all traffic)
       │            
       │ Clients → Service → BLUE pods
       │
       │ Status:
       │ • All traffic flowing through BLUE
       │ • No new deployment yet
       │ • System stable
       │
  
  PHASE 2 - GREEN DEPLOYED (Preview)
  
  10%  │ ▓▓▓▓▓▓▓▓▓▓  BLUE (10 pods - all traffic)
       │ ░░░        GREEN (3 preview pods)
       │
       │ Clients → Service → BLUE pods (100% traffic)
       │ Test   → GREEN pods (no traffic yet)
       │
       │ Action: Run integration tests on GREEN
       │ Tests performed:
       │  • Smoke tests ✓
       │  • API validation ✓
       │  • Database connectivity ✓
       │
       │ If tests PASS:
       │  → PROCEED TO PROMOTION
       │
       │ If tests FAIL:
       │  → ABORT (GREEN terminated, BLUE continues)
       │
  
  PHASE 3 - TRAFFIC SWITCH (Promotion)
  
  20%  │ ▓▓▓▓▓▓▓▓▓▓  BLUE (still running, no traffic)
       │ ░░░░░░░░░░  GREEN (10 pods - all traffic NOW)
       │
       │ Clients → Service → GREEN pods (100% traffic)
       │
       │ Status:
       │ • Traffic switched instantly
       │ • BLUE still running (fallback)
       │ • Monitoring GREEN metrics
       │
       │ If metrics GOOD (30s):
       │  → DELETE BLUE
       │  → SUCCESS
       │
       │ If metrics BAD (immediate):
       │  → ROLLBACK: Switch traffic back to BLUE
       │  → DELETE GREEN
       │  → FAILURE (manual investigation)
       │
  
  PHASE 4 - BLUE TERMINATED
  
  30%  │                    (BLUE pods deleted)
       │ ░░░░░░░░░░  GREEN (10 pods - all traffic)
       │
       │ ✓ BLUE-GREEN DEPLOYMENT COMPLETE
       │
   Features:
   • Two complete environments (BLUE + GREEN)
   • Zero-downtime deployment
   • Instant traffic switchover
   • Full rollback capability
   • Parallel testing possible
   
   Comparison:
   • Canary: Gradual rollout, early issue detection
   • Blue-Green: Instant switchover, complete rollback


╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║  RISK vs ROLLOUT TIME vs TRAFFIC IMPACT                              ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝

   Rolling Deployment:
   ├─ Risk: MEDIUM (issues caught at 50% traffic)
   ├─ Rollout Time: FAST (5-10 minutes)
   └─ Traffic Impact: GRADUAL (rolling)
   
   Canary Deployment:
   ├─ Risk: LOW (issues caught early at 20% traffic)
   ├─ Rollout Time: SLOW (30-40 minutes)
   └─ Traffic Impact: VERY GRADUAL (10% steps)
   
   Blue-Green Deployment:
   ├─ Risk: VERY LOW (full test before switch)
   ├─ Rollout Time: MEDIUM (15-20 minutes)
   └─ Traffic Impact: INSTANT (0 to 100%)
```

---

**End of Architecture Diagrams Document**

Generated: October 29, 2026
