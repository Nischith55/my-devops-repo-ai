# Custom Domain Traffic Flow - Complete End-to-End Explanation

## Table of Contents
1. [Quick Overview](#quick-overview)
2. [Complete Traffic Journey](#complete-traffic-journey)
3. [Step-by-Step Flow](#step-by-step-flow)
4. [Your Infrastructure Setup](#your-infrastructure-setup)
5. [Real Example from Your Repos](#real-example-from-your-repos)
6. [DNS Resolution](#dns-resolution)
7. [Load Balancer to Pod](#load-balancer-to-pod)
8. [Service Mesh Processing (Istio)](#service-mesh-processing-istio)
9. [Return Traffic](#return-traffic)
10. [Complete Visual Flow](#complete-visual-flow)

---

## Quick Overview

When you enter: `https://argocd.pfnainfra.gw01.aks02.eus.prod.azure.intra.pepsico.com`

```
Domain Name
    ↓
DNS Lookup (Azure Private DNS)
    ↓
Public IP (LoadBalancer Service)
    ↓
Azure Load Balancer (External)
    ↓
Istio Ingress Gateway (Pod)
    ↓
Istio VirtualService Rules
    ↓
Destination Service (argocd-server.argocd.svc.cluster.local)
    ↓
Destination Pod
    ↓
Response back to user
```

---

## Complete Traffic Journey

### **Stage 1: User Makes Request**

```
User Browser
  https://argocd.pfnainfra.gw01.aks02.eus.prod.azure.intra.pepsico.com

Request Contains:
├─ Domain: argocd.pfnainfra.gw01.aks02.eus.prod.azure.intra.pepsico.com
├─ Protocol: HTTPS (TLS 1.2 or 1.3)
├─ Port: 443 (default for HTTPS)
└─ Path: / (or any path like /api/v1)
```

---

## Step-by-Step Flow

### **STEP 1: DNS Resolution**

```
┌─────────────────────────────────────────────────────────┐
│ User's Computer / Browser                               │
│                                                           │
│ "What is the IP for argocd.pfnainfra.gw01..."?          │
│ Sends DNS query                                          │
└─────────────────────────────────────────────────────────┘
                        ↓
              DNS Server Receives Query
                        ↓
┌─────────────────────────────────────────────────────────┐
│ Azure Private DNS Zone                                  │
│ (managed by Terraform/Azure)                            │
│                                                           │
│ Zone: intra.pepsico.com                                 │
│ Records:                                                 │
│ ├─ argocd.pfnainfra.gw01.aks02.eus.prod                 │
│ │   └─ Points to: 20.45.123.45 (Public IP)              │
│ ├─ pod-info.sbox.gw01.aks03.eus.nonprod                 │
│ │   └─ Points to: 20.45.234.56 (Public IP)              │
│ └─ ... more DNS records                                 │
└─────────────────────────────────────────────────────────┘
                        ↓
            DNS Response Sent to Browser
            
Response:
├─ Domain: argocd.pfnainfra.gw01.aks02.eus.prod.azure.intra.pepsico.com
├─ IP Address: 20.45.123.45
└─ TTL: 300 (cache for 5 minutes)
```

**Where DNS comes from in your repos:**
```
Terraform (eip-infra-azure-terraform-support)
    └─ Azure Private DNS Zone resource
    └─ DNS records created for each service
```

---

### **STEP 2: Browser Connects to Public IP**

```
┌─────────────────────────────────────────────────────────┐
│ Browser                                                 │
│                                                           │
│ "I'll connect to 20.45.123.45:443"                      │
│ Initiates TCP connection                                │
│ Performs TLS Handshake (HTTPS)                          │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ Azure Cloud (Data Center)                               │
│                                                           │
│ Public IP: 20.45.123.45                                 │
│ (Created by Terraform for LoadBalancer)                 │
└─────────────────────────────────────────────────────────┘
                        ↓
        Azure Load Balancer (External)
        
        Routing rules:
        ├─ Destination Port: 443
        ├─ Protocol: HTTPS
        └─ Backend Pool: Kubernetes nodes
```

**Where LoadBalancer comes from in your repos:**
```
Terraform (eip-infra-azure-terraform-support)
    └─ Azure LoadBalancer resource
    └─ Public IP resource
    └─ Backend pool contains AKS node IPs
    └─ Forwarding rules map port 443 → backend port
```

---

### **STEP 3: Traffic Enters Kubernetes Cluster**

```
┌──────────────────────────────────────────────────────────────┐
│ Azure Load Balancer                                          │
│ Receives traffic on 20.45.123.45:443                         │
└──────────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────────┐
│ AKS Cluster Nodes                                            │
│                                                               │
│ Kernel networking layer receives traffic                     │
│ (iptables rules route to services)                           │
└──────────────────────────────────────────────────────────────┘
                        ↓
              Kubernetes Service Lookup
              
              Looking for service on port 443
              Service type: LoadBalancer
              Name: istio-ingressgateway
              Namespace: istio-system
```

---

### **STEP 4: Istio Ingress Gateway Pod**

```
┌──────────────────────────────────────────────────────────────┐
│ Kubernetes Service (istio-ingressgateway)                    │
│                                                               │
│ Service:                                                      │
│ ├─ Name: istio-ingressgateway                                │
│ ├─ Namespace: istio-system                                   │
│ ├─ Type: LoadBalancer                                        │
│ ├─ External IP: 20.45.123.45 (Azure Public IP)              │
│ └─ Port: 443 → Pod Port: 8443                                │
│                                                               │
│ Selector: istio=ingressgateway                               │
│ Pods matching this selector:                                 │
│ ├─ istio-ingressgateway-xxxxx (Pod 1)                        │
│ ├─ istio-ingressgateway-yyyyy (Pod 2)                        │
│ └─ istio-ingressgateway-zzzzz (Pod 3)                        │
└──────────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────────┐
│ Ingress Gateway Pod Details                                  │
│                                                               │
│ Container: istio-proxy (Envoy proxy)                         │
│ ├─ Listening on: 0.0.0.0:8443 (port inside pod)             │
│ ├─ Protocol: HTTPS (handles TLS termination)                │
│ └─ Configuration: From Istio Gateway resource               │
│                                                               │
│ Envoy Proxy receives:                                        │
│ ├─ SNI: argocd.pfnainfra.gw01.aks02.eus.prod...             │
│ ├─ Port: 443 (forwarded as 8443)                            │
│ ├─ TLS Certificate: From Kubernetes secret                  │
│ └─ Matches Gateway.spec.servers[].hosts                     │
└──────────────────────────────────────────────────────────────┘
```

---

### **STEP 5: Gateway Matching**

At this point, Istio Ingress Gateway checks the **Gateway resource**:

```yaml
# From your repo: argocd-cv-gw.yaml
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: argocd-cv-gw
  namespace: argocd
spec:
  selector:
    istio: pep-pfna-ingress-gw01  # Selects the ingress gateway pod
  servers:
  - hosts:
    - dummy-passthrough-argocd.pfna.sch.gw01.aks01.scus.prod.azure.intra.pepsico.com
    - argocd.pfnainfra.gw01.aks02.eus.prod.azure.intra.pepsico.com  # ← MATCHES!
    name: argocd-cv-gw-tls-443
    port:
      name: https-argocd-cv-gw-tls-443
      number: 443
      protocol: https
    tls:
      mode: PASSTHROUGH  # TLS handled transparently, no termination needed
      minProtocolVersion: TLSV1_2
      maxProtocolVersion: TLSV1_3
```

**What happens:**
```
Incoming traffic to argocd.pfnainfra.gw01.aks02.eus.prod...
    ↓
Gateway resource checks:
├─ Is the domain in hosts list? ✓ YES → argocd.pfnainfra.gw01.aks02.eus.prod...
├─ Is the port correct? ✓ YES → 443
├─ Is the protocol correct? ✓ YES → https
└─ TLS requirements met? ✓ YES → TLS 1.2 or 1.3
    ↓
ACCEPT - Gateway passes request to VirtualService
```

---

### **STEP 6: VirtualService Routing**

Gateway accepts the request and passes it to **VirtualService**:

```yaml
# From your repo: argocd-vs.yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: argocd-vs
  namespace: argocd
spec:
  gateways:
  - argocd/argocd-cv-gw  # ← Points to the Gateway above
  hosts:
  - argocd.pfnainfra.gw01.aks02.eus.prod.azure.intra.pepsico.com  # ← MATCHES incoming domain
  http:
  - match:
    - ignoreUriCase: true
      uri:
        prefix: /  # Matches any path starting with /
    route:
    - destination:
        host: argocd-server.argocd.svc.cluster.local  # ← Destination service
        port:
          number: 80  # ← Destination service port
```

**What happens:**
```
Incoming request with:
├─ Domain: argocd.pfnainfra.gw01.aks02.eus.prod...
├─ Path: /
└─ Port: 443 (from browser)

VirtualService checks:
├─ Is domain in hosts? ✓ YES
├─ Does path match? ✓ YES (/ matches prefix: /)
└─ Apply route rule
    ↓
Route destination:
├─ Service: argocd-server
├─ Namespace: argocd
├─ Port: 80

Result:
└─ Forward to: argocd-server.argocd.svc.cluster.local:80
```

---

### **STEP 7: Service to Pod Routing**

```
┌──────────────────────────────────────────────────────────────┐
│ Kubernetes Service: argocd-server                            │
│                                                               │
│ Service Definition:                                          │
│ ├─ Name: argocd-server                                       │
│ ├─ Namespace: argocd                                         │
│ ├─ Type: ClusterIP                                           │
│ ├─ Port: 80                                                  │
│ └─ Selector: app=argocd-server                               │
│                                                               │
│ Kubernetes finds pods matching selector:                     │
│ ├─ argocd-server-0 (Pod 1)                                   │
│ ├─ argocd-server-1 (Pod 2)                                   │
│ └─ argocd-server-2 (Pod 3)                                   │
│                                                               │
│ Service uses load balancing: (ROUND_ROBIN)                   │
│ Request 1 → Pod 1                                            │
│ Request 2 → Pod 2                                            │
│ Request 3 → Pod 3                                            │
│ Request 4 → Pod 1 (cycle repeats)                            │
└──────────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────────┐
│ Destination Pod: argocd-server-0                             │
│                                                               │
│ Pod Structure:                                               │
│ ├─ Container 1: argocd-server (application)                  │
│ │   └─ Listening on: localhost:8080 (internal)              │
│ │                                                             │
│ ├─ Container 2: istio-proxy (Envoy sidecar)                 │
│ │   └─ Listening on: 0.0.0.0:15006 (inbound traffic)        │
│ │                                                             │
│ └─ iptables rules intercept traffic:                        │
│    ├─ Traffic to port 80 → Envoy port 15006                │
│    └─ Envoy processes rules from DestinationRule             │
└──────────────────────────────────────────────────────────────┘
```

**Traffic interception by Envoy sidecar:**
```
Incoming traffic from LoadBalancer (port 80)
    ↓
iptables rule intercepts: *:80
    ↓
Redirect to Envoy proxy (listening on port 15006)
    ↓
Envoy checks DestinationRule policies:
├─ Load balancing: ROUND_ROBIN
├─ Connection pool limits
├─ Timeout: 10s
├─ Retries: 3 attempts
└─ Circuit breaker settings
    ↓
Envoy forwards to application (localhost:8080)
    ↓
argocd-server application receives request
└─ Processes and sends response
```

---

### **STEP 8: Inside Application Pod**

```
┌──────────────────────────────────────────────────────────────┐
│ argocd-server Application Container                          │
│                                                               │
│ Application logic:                                           │
│ 1. Receives request on port 8080                             │
│ 2. Processes the request                                     │
│ 3. Generates response (HTTP 200 OK)                          │
│ 4. Sends response back                                       │
│                                                               │
│ Example Response:                                            │
│ ├─ Status: 200 OK                                            │
│ ├─ Content-Type: application/json                            │
│ ├─ Body: {"version": "2.8.0", "status": "healthy"}          │
│ └─ Total time: 50ms                                          │
└──────────────────────────────────────────────────────────────┘
```

---

## STEP 9: Return Traffic Path

```
Response from application (port 8080)
    ↓
Envoy sidecar intercepts outgoing traffic
    ↓
Envoy adds telemetry data:
├─ Request latency: 50ms
├─ Response status: 200
├─ Response size: 256 bytes
└─ Timestamp: 2024-01-15T10:30:45Z
    ↓
Sent to Prometheus for monitoring
    ↓
Response sent back through Istio Ingress Gateway
    ↓
Istio Gateway (Envoy) receives response
    ↓
TLS encryption (PASSTHROUGH mode - already encrypted from app)
    ↓
Sent back to user's browser
    ↓
Browser displays response
```

---

## Your Infrastructure Setup

### **Where Each Component is Built:**

#### **1. Infrastructure Layer (Terraform)**
```
eip-infra-azure-terraform-support/src/pfna/prod/common-tf-config/
├─ azure-kubernetes-services/
│  ├─ main.tf          → Creates AKS cluster
│  ├─ variables.tf     → Input variables for cluster
│  └─ outputs.tf       → Exports cluster info
│
├─ azure-load-balancer/
│  └─ Creates LoadBalancer service Public IP
│
└─ azure-dns/
   └─ Creates Private DNS Zone
      └─ DNS records for services
```

**What Terraform creates:**
```
1. AKS Cluster (Kubernetes)
2. Virtual Network
3. Public IP (for LoadBalancer)
4. Azure Load Balancer (routes external traffic)
5. Private DNS Zone (resolves domain names)
```

---

#### **2. Kubernetes & Istio Installation (Ansible/K8s)**
```
eip-infra-k8s-support/
├─ aks-post-provisioning.yml  → Installs Istio, networking
│
eip-infra-k8s-argocd-support/
├─ Defines Gateway resources
└─ Defines VirtualService resources
```

**What gets installed:**
```
1. Istio Control Plane (istiod)
2. Istio Ingress Gateway
3. Prometheus (metrics)
4. Grafana (dashboards)
5. Jaeger (distributed tracing)
```

---

#### **3. Service Configuration (Helm + ArgoCD)**
```
eip-helm-chart/
├─ platform-chart/
│  └─ templates/
│     ├─ virtualservice.yaml     → Templated VirtualService
│     ├─ destinationrule.yaml    → Load balancing policies
│     └─ gateway.yaml            → Ingress gateway config
│
└─ app-chart/
   └─ templates/
      ├─ deployment.yaml         → Application pods
      ├─ service.yaml            → Service definition
      └─ serviceaccount.yaml      → RBAC

eip-infra-k8s-argocd-support/
├─ pfna/prod/.../argocd-configs/
│  ├─ istio-gw/                  → Gateway resources
│  ├─ virtualservice/             → VirtualService resources
│  └─ configmaps/                 → Configuration
```

**What values are used:**
```
From values-pod-info.yaml:
├─ Domain: pod-info.sbox.gw01.aks03.eus.nonprod.azure.intra.pepsico.com
├─ Service: pod-info-helm
├─ Port: 9898
├─ Namespace: sscsi
├─ Gateway: istio-system/istio-in-gateway-01
└─ Load Balancer: ROUND_ROBIN
```

---

## Real Example from Your Repos

### **Example 1: ArgoCD Service**

**Terraform creates infrastructure:**
```hcl
# Creates AKS cluster
module "aks_cluster" {
  source = ".../modules/azure_kubernetes_services"
  
  cluster_name = "pep-pfna-cit-prod-eus-infra-02-aks"
  location     = "eastus"
}

# Creates Public IP for LoadBalancer
resource "azurerm_public_ip" "lb" {
  name                = "pfna-lb-public-ip"
  location            = "eastus"
  resource_group_name = "pfna-prod-rg"
  allocation_method   = "Static"
}
```

**ArgoCD pod is deployed:**
```yaml
# argocd-server pod
apiVersion: v1
kind: Pod
metadata:
  name: argocd-server-0
  namespace: argocd
spec:
  containers:
  - name: argocd-server
    image: argoproj/argocd-server:v2.8.0
    ports:
    - containerPort: 8080
  - name: istio-proxy  # ← Sidecar injected by Istio
    image: istio/proxyv2:1.18.0
    ports:
    - containerPort: 15006  # Envoy listening port
```

**Gateway tells Istio how to accept traffic:**
```yaml
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: argocd-cv-gw
  namespace: argocd
spec:
  selector:
    istio: pep-pfna-ingress-gw01  # Selects the ingress gateway
  servers:
  - hosts:
    - argocd.pfnainfra.gw01.aks02.eus.prod.azure.intra.pepsico.com  # ← Your custom domain
    port:
      number: 443
      protocol: https
```

**VirtualService tells Istio where to send traffic:**
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: argocd-vs
  namespace: argocd
spec:
  gateways:
  - argocd/argocd-cv-gw
  hosts:
  - argocd.pfnainfra.gw01.aks02.eus.prod.azure.intra.pepsico.com
  http:
  - route:
    - destination:
        host: argocd-server.argocd.svc.cluster.local  # ← Where to route
        port:
          number: 80
```

**Service knows which pods to target:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: argocd-server
  namespace: argocd
spec:
  type: ClusterIP
  port: 80
  targetPort: 8080
  selector:
    app: argocd-server  # ← Selects argocd-server-0, -1, -2 pods
```

---

### **Example 2: Pod-Info Service**

From your `values-pod-info.yaml`:

```yaml
global:
  namespace: sscsi
  fullnameOverride: "pod-info-helm"

virtualService: 
  enabled: true
  hosts: 
  - pod-info.sbox.gw01.aks03.eus.nonprod.azure.intra.pepsico.com  # ← Custom domain
  gateways:
  - istio-system/istio-in-gateway-01  # ← Which gateway
  routes:
  - prefix: /
    routingDestinations:
    - destinationService: pod-info-helm
      port: 9898

app-chart:
  replicaCount: 3
  labels:
    app: pod-info-helm
  image:    
    repository: pepeiapnonprodcommonacr.azurecr.io/pep/pod-info
    tag: "20230915.14"
  command:
  - ./podinfo
  - --port=9898
```

**Traffic flow for pod-info:**
```
https://pod-info.sbox.gw01.aks03.eus.nonprod.azure.intra.pepsico.com
    ↓
DNS resolves to Public IP (20.45.234.56)
    ↓
LoadBalancer routes to istio-ingressgateway pod
    ↓
Gateway checks: domain = pod-info.sbox.gw01.aks03.eus.nonprod...? ✓
    ↓
VirtualService routes to pod-info-helm service:9898
    ↓
Service load-balances to pod-info-helm pod (3 replicas)
    ↓
Envoy sidecar intercepts and routes to localhost:9898
    ↓
podinfo application responds
```

---

## DNS Resolution

### **How DNS Records are Created:**

```
Terraform creates:
1. Azure Private DNS Zone
   └─ intra.pepsico.com
   
2. DNS Records (A records)
   ├─ argocd.pfnainfra.gw01.aks02.eus.prod → 20.45.123.45
   ├─ pod-info.sbox.gw01.aks03.eus.nonprod → 20.45.234.56
   └─ ... more records
   
3. Public IPs (for LoadBalancer)
   ├─ 20.45.123.45 (Primary LoadBalancer IP)
   └─ 20.45.234.56 (Secondary LoadBalancer IP)
```

### **DNS Query Resolution Flow:**

```
Browser needs IP for: argocd.pfnainfra.gw01.aks02.eus.prod.azure.intra.pepsico.com
    ↓
Query sent to: Azure Private DNS resolver
    ↓
Azure DNS checks:
├─ Zone: intra.pepsico.com? ✓ Found
├─ Record name: argocd.pfnainfra.gw01.aks02.eus.prod? ✓ Found
└─ Record type: A (IPv4)? ✓ Found
    ↓
Returns: 20.45.123.45
    ↓
Browser connects to: 20.45.123.45:443
```

---

## Load Balancer to Pod

### **Azure LoadBalancer Routing:**

```
┌─────────────────────────────────────────────────┐
│ Azure Cloud (Public Internet)                   │
│                                                  │
│ Public IP: 20.45.123.45                         │
│ Protocol: TCP/443 (HTTPS)                       │
└─────────────────────────────────────────────────┘
              ↓ (Incoming traffic)
┌─────────────────────────────────────────────────┐
│ Azure Load Balancer                             │
│                                                  │
│ Rules:                                          │
│ ├─ Frontend IP: 20.45.123.45                    │
│ ├─ Frontend Port: 443                           │
│ ├─ Backend Pool: AKS Nodes                      │
│ └─ Backend Port: 30443 (NodePort for service)   │
└─────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────┐
│ AKS Cluster Nodes                               │
│                                                  │
│ Node 1: 10.0.1.10                               │
│ Node 2: 10.0.1.11                               │
│ Node 3: 10.0.1.12                               │
│                                                  │
│ Each node has:                                  │
│ ├─ kernel iptables rules                        │
│ └─ kube-proxy watching for service changes      │
└─────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────┐
│ Kubernetes Service: istio-ingressgateway        │
│                                                  │
│ Type: LoadBalancer                              │
│ Port 443 → Pod Port 8443                        │
│ Selector: istio=ingressgateway                  │
└─────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────┐
│ Istio Ingress Gateway Pod                       │
│ (running on one of the nodes)                   │
│                                                  │
│ Container: istio-proxy                          │
│ Listening on: 0.0.0.0:8443                      │
│ Protocol: HTTPS                                 │
└─────────────────────────────────────────────────┘
```

---

## Service Mesh Processing (Istio)

### **Complete Istio Processing at Ingress Gateway:**

```
Traffic arrives at Envoy Proxy in Ingress Gateway Pod
    ↓
├─ TLS Handshake? (if mode = SIMPLE)
│   └─ Verify certificate from Kubernetes secret
│
├─ Extract SNI hostname from TLS Client Hello
│   └─ Example: argocd.pfnainfra.gw01.aks02.eus.prod...
│
└─ Check Gateway resources in ALL namespaces
    └─ Find matching host in any Gateway.servers[].hosts[]
    └─ Match: argocd/argocd-cv-gw
        ↓
    Check VirtualService pointing to this Gateway
    └─ Match gateways: [argocd/argocd-cv-gw]
    └─ Match hosts: [argocd.pfnainfra.gw01.aks02.eus.prod...]
        ↓
    Apply routing rules (http[].route[])
    ├─ If path matches: / → route to destination
    └─ Destination: argocd-server.argocd.svc.cluster.local:80
        ↓
    Check DestinationRule (if exists)
    ├─ Load balancing: ROUND_ROBIN
    ├─ Connection pool: max 100 connections
    ├─ Timeout: 10 seconds
    ├─ Retries: 3 attempts
    └─ Circuit breaker: 5 consecutive errors = open
        ↓
    Forward traffic to Service Pods
    ├─ Pod 1: argocd-server-0
    ├─ Pod 2: argocd-server-1
    └─ Pod 3: argocd-server-2
```

---

## Complete Visual Flow

```
┌──────────────────────────────────────────────────────────────────────┐
│ EXTERNAL WORLD                                                       │
│                                                                       │
│ User enters URL in browser:                                          │
│ https://argocd.pfnainfra.gw01.aks02.eus.prod.azure.intra.pepsico.com│
└──────────────────────────────────────────────────────────────────────┘
                                    ↓
┌──────────────────────────────────────────────────────────────────────┐
│ STEP 1: DNS RESOLUTION (Azure Private DNS)                           │
│                                                                       │
│ Domain → 20.45.123.45 (Public IP)                                    │
└──────────────────────────────────────────────────────────────────────┘
                                    ↓
┌──────────────────────────────────────────────────────────────────────┐
│ STEP 2: AZURE PUBLIC INTERNET                                        │
│                                                                       │
│ Browser connects to: 20.45.123.45:443                                │
│ TLS Handshake established                                            │
└──────────────────────────────────────────────────────────────────────┘
                                    ↓
┌──────────────────────────────────────────────────────────────────────┐
│ STEP 3: AZURE LOAD BALANCER                                          │
│                                                                       │
│ Public IP: 20.45.123.45:443                                          │
│ ├─ Checks backend pool (AKS Nodes)                                  │
│ ├─ Selects healthy node (e.g., Node 1)                              │
│ └─ Forwards to Node:30443                                            │
└──────────────────────────────────────────────────────────────────────┘
                                    ↓
┌──────────────────────────────────────────────────────────────────────┐
│ STEP 4: AKS NODE NETWORK                                             │
│                                                                       │
│ Traffic arrives on Node 1                                            │
│ ├─ Kernel iptables intercepts port 30443                            │
│ ├─ Kube-proxy has rules for service: istio-ingressgateway           │
│ └─ Routes to Pod IP: 10.244.2.15                                    │
└──────────────────────────────────────────────────────────────────────┘
                                    ↓
┌──────────────────────────────────────────────────────────────────────┐
│ STEP 5: ISTIO INGRESS GATEWAY POD                                    │
│                                                                       │
│ Pod: istio-ingressgateway-xxxxx                                      │
│ Namespace: istio-system                                              │
│ IP: 10.244.2.15                                                      │
│                                                                       │
│ Containers:                                                          │
│ ├─ istio-proxy (Envoy on :8443)                                     │
│ │   └─ Receives traffic on port 8443                                │
│ │   └─ SNI: argocd.pfnainfra.gw01.aks02.eus.prod...                │
│ │                                                                    │
│ └─ (Other containers)                                               │
│                                                                       │
│ Envoy checks Gateway resources:                                      │
│ └─ Finds: argocd/argocd-cv-gw (matches host)                        │
└──────────────────────────────────────────────────────────────────────┘
                                    ↓
┌──────────────────────────────────────────────────────────────────────┐
│ STEP 6: VIRTUALSERVICE ROUTING                                       │
│                                                                       │
│ VirtualService: argocd-vs                                            │
│ Namespace: argocd                                                    │
│                                                                       │
│ Routing Logic:                                                       │
│ ├─ Host matches? argocd.pfnainfra.gw01.aks02.eus.prod... ✓          │
│ ├─ Path matches? / (prefix) ✓                                        │
│ └─ Route to: argocd-server.argocd.svc.cluster.local:80              │
└──────────────────────────────────────────────────────────────────────┘
                                    ↓
┌──────────────────────────────────────────────────────────────────────┐
│ STEP 7: SERVICE TO POD DISCOVERY                                     │
│                                                                       │
│ Service: argocd-server.argocd.svc.cluster.local:80                   │
│                                                                       │
│ Service finds matching pods:                                         │
│ ├─ Selector: app=argocd-server                                      │
│ ├─ Pod 1: argocd-server-0 (IP: 10.244.1.20)                         │
│ ├─ Pod 2: argocd-server-1 (IP: 10.244.1.21)                         │
│ └─ Pod 3: argocd-server-2 (IP: 10.244.1.22)                         │
│                                                                       │
│ Load Balancer selects: Pod 1 (Round Robin)                           │
└──────────────────────────────────────────────────────────────────────┘
                                    ↓
┌──────────────────────────────────────────────────────────────────────┐
│ STEP 8: DESTINATION POD                                              │
│                                                                       │
│ Pod: argocd-server-0                                                 │
│ Namespace: argocd                                                    │
│ IP: 10.244.1.20                                                      │
│                                                                       │
│ Pod Containers:                                                      │
│ ├─ istio-proxy (Envoy sidecar)                                      │
│ │   ├─ Listening on: 0.0.0.0:15006                                  │
│ │   ├─ iptables intercepts traffic to :80                           │
│ │   ├─ Routes to Envoy                                              │
│ │   ├─ Applies DestinationRule policies                             │
│ │   │   ├─ Load Balancer: ROUND_ROBIN                               │
│ │   │   ├─ Timeout: 10s                                             │
│ │   │   └─ Retries: 3 attempts                                      │
│ │   └─ Forwards to localhost:8080                                   │
│ │                                                                    │
│ └─ argocd-server (Application)                                      │
│    ├─ Listening on: localhost:8080                                  │
│    ├─ Receives request                                              │
│    ├─ Processes request                                             │
│    └─ Sends response (HTTP 200 OK)                                  │
└──────────────────────────────────────────────────────────────────────┘
                                    ↓
┌──────────────────────────────────────────────────────────────────────┐
│ STEP 9: RESPONSE BACK THROUGH ENVOY SIDECAR                          │
│                                                                       │
│ Application response:                                                │
│ ├─ Status: 200 OK                                                    │
│ ├─ Content: HTML/JSON                                                │
│ └─ Size: 256 bytes                                                   │
│                                                                       │
│ Envoy intercepts response:                                           │
│ ├─ Collects metrics                                                  │
│ │   ├─ Latency: 50ms                                                │
│ │   ├─ Status: 200                                                  │
│ │   └─ Bytes: 256                                                   │
│ ├─ Sends to Prometheus (monitoring)                                 │
│ └─ Forwards response back                                            │
└──────────────────────────────────────────────────────────────────────┘
                                    ↓
┌──────────────────────────────────────────────────────────────────────┐
│ STEP 10: BACK THROUGH SERVICE & INGRESS                              │
│                                                                       │
│ Response path:                                                       │
│ argocd-server-0 → Service → Ingress Gateway → LoadBalancer           │
│                                                                       │
│ Envoy at Ingress Gateway:                                            │
│ ├─ Receives response                                                 │
│ ├─ Applies TLS encryption (if needed)                                │
│ └─ Sends back to browser                                             │
└──────────────────────────────────────────────────────────────────────┘
                                    ↓
┌──────────────────────────────────────────────────────────────────────┐
│ STEP 11: BACK TO USER BROWSER                                        │
│                                                                       │
│ Browser receives:                                                    │
│ ├─ HTTPS response (encrypted)                                        │
│ ├─ Status: 200 OK                                                    │
│ ├─ HTML content                                                      │
│ └─ Displays in browser                                               │
│                                                                       │
│ User sees: ArgoCD UI loaded successfully                             │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Summary Table

| Layer | Component | Location | Purpose |
|-------|-----------|----------|---------|
| **DNS** | Azure Private DNS | Cloud | Resolves domain to IP |
| **Network** | Public IP + LB | Azure | Routes external traffic |
| **Ingress** | Istio Gateway Pod | K8s | Listens for incoming connections |
| **Routing** | VirtualService | K8s | Routes based on host/path |
| **Discovery** | Kubernetes Service | K8s | Finds backend pods |
| **Processing** | Envoy Sidecar | Pod | Applies policies, monitoring |
| **Application** | App Container | Pod | Processes actual request |

---

## Key Takeaways

1. **DNS** - Custom domain resolves to Public IP (managed by Terraform)
2. **LoadBalancer** - Distributes traffic to AKS nodes (Azure resource)
3. **Gateway** - Istio resource telling ingress which domains to accept
4. **VirtualService** - Istio resource defining routing rules
5. **Service** - Kubernetes discovery for backend pods
6. **Envoy Sidecar** - Intercepts traffic at pod level, applies policies
7. **Application** - Receives traffic on localhost:port from Envoy

**All coordinated by:**
- **Terraform** - Infrastructure
- **Helm** - Package deployment
- **ArgoCD** - Configuration management
- **Istio** - Service mesh
- **Kubernetes** - Orchestration
