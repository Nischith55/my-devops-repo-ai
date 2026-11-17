# Istio Service Mesh - Complete Guide

## Table of Contents
1. [What is Istio?](#what-is-istio)
2. [Core Architecture](#core-architecture)
3. [How Istio Works - Step by Step](#how-istio-works-step-by-step)
4. [Key Components Explained](#key-components-explained)
5. [Traffic Management](#traffic-management)
6. [Security Features](#security-features)
7. [Observability](#observability)
8. [Installation Process](#installation-process)
9. [Real-World Example](#real-world-example)
10. [Istio in Your Project](#istio-in-your-project)

---

## What is Istio?

**Istio is a Service Mesh** - it's a dedicated infrastructure layer that handles communication between microservices.

### Simple Analogy:
```
Without Istio:
App A → (send request) → App B
(App A manages: retries, timeouts, security, monitoring)

With Istio:
App A → Istio Proxy → (send request) → Istio Proxy → App B
(Istio manages: retries, timeouts, security, monitoring - automatically!)
```

### Why do you need it?
- **Service-to-service communication** management
- **Traffic control** (load balancing, canary deployments)
- **Security** (mTLS encryption, authorization policies)
- **Observability** (monitoring, tracing, logging)
- **Resilience** (circuit breakers, retries)

---

## Core Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐          ┌──────────────┐                 │
│  │   Pod A      │          │   Pod B      │                 │
│  │  ┌────────┐  │          │  ┌────────┐  │                 │
│  │  │ App    │  │          │  │ App    │  │                 │
│  │  └────────┘  │          │  └────────┘  │                 │
│  │  ┌────────┐  │          │  ┌────────┐  │                 │
│  │  │ Envoy  │◄─┼──────────┼─►│ Envoy  │  │                 │
│  │  │ Proxy  │  │          │  │ Proxy  │  │                 │
│  │  └────────┘  │          │  └────────┘  │                 │
│  └──────────────┘          └──────────────┘                 │
│         ▲                          ▲                          │
│         │ (Injects config)         │ (Injects config)        │
│         └──────────┬───────────────┘                          │
│                    │                                          │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Istio Control Plane                                    │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │ │
│  │  │  Istiod      │  │  Pilot       │  │  Galley      │  │ │
│  │  │  (unified)   │  │  (config)    │  │  (validation)│  │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## How Istio Works - Step by Step

### **STEP 1: Installation**
```
1. Deploy Istio Control Plane (Istiod, Prometheus, Grafana, Jaeger)
   └─ Watches for new pods in labeled namespaces
   
2. Label namespace for sidecar injection:
   kubectl label namespace default istio-injection=enabled
   
3. Restart pods (or deploy new ones)
```

### **STEP 2: Sidecar Injection**
```
When you create a pod in an labeled namespace:

1. Kubernetes Mutating Webhook intercepts pod creation
2. Webhook INJECTS an Envoy proxy sidecar into pod
3. Pod now has 2 containers:
   - Your application (App)
   - Envoy proxy (sidecar)

Result: Pod = [App Container] + [Envoy Sidecar Container]
```

### **STEP 3: Configuration**
```
You define YAML resources:

VirtualService    → How to route traffic
DestinationRule   → Load balancing, connection pool
Gateway           → Ingress rules
PeerAuthentication→ mTLS policies
AuthorizationPolicy→ Access control
```

### **STEP 4: Traffic Interception**
```
1. Your app sends request to another service
   App → localhost:8080/api

2. Kernel iptables rules intercept traffic
   (installed by Istio init container)

3. Routes traffic to Envoy proxy
   localhost:8080 → Envoy (port 15000)

4. Envoy proxy applies rules from ControlPlane
   - Load balancing
   - Retries
   - Timeouts
   - Rate limiting

5. Envoy sends to destination
   Envoy → Service Pod
```

### **STEP 5: Destination Processing**
```
At destination pod:

1. Kernel routes incoming traffic to Envoy
2. Envoy receives and applies rules
3. Envoy forwards to local application
4. Response goes back through Envoy
5. Envoy sends back to source Envoy
6. Source Envoy delivers to application
```

---

## Key Components Explained

### **1. Istiod (Control Plane)**
```
Core of Istio - single unified control plane

Contains:
├─ Pilot       → Manages ServiceEntry, DestinationRule, VirtualService
├─ Citadel     → Manages certificates, mTLS
├─ Galley      → Validates configurations
└─ Webhook     → Injects sidecars into pods
```

### **2. Envoy Proxy (Data Plane)**
```
Lightweight proxy running in each pod

Does:
├─ Traffic filtering
├─ Load balancing
├─ Circuit breaking
├─ Retry logic
├─ Rate limiting
├─ mTLS encryption
└─ Telemetry collection
```

### **3. Configuration Objects**

#### **VirtualService**
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: my-service
spec:
  hosts:
  - my-service
  http:
  - match:
    - uri:
        prefix: "/api/v1"
    route:
    - destination:
        host: my-service
        port:
          number: 8080
        subset: v1
      weight: 90
    - destination:
        host: my-service
        port:
          number: 8080
        subset: v2
      weight: 10
```

**What it does:**
- Routes traffic to `my-service`
- 90% to v1, 10% to v2 (Canary deployment)
- Match by URI prefix

#### **DestinationRule**
```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: my-service
spec:
  host: my-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 50
        maxRequestsPerConnection: 2
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
```

**What it does:**
- Defines subsets (v1, v2)
- Connection pooling limits
- Circuit breaker (outlierDetection)
- Load balancing policies

#### **Gateway**
```yaml
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: my-gateway
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "example.com"
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: SIMPLE
      credentialName: my-certs
    hosts:
    - "example.com"
```

**What it does:**
- Ingress entry point
- HTTP/HTTPS termination
- Certificate handling

---

## Traffic Management

### **Load Balancing**
```
DestinationRule → trafficPolicy → loadBalancer

Options:
- ROUND_ROBIN      → Default, rotate through instances
- LEAST_REQUEST    → Send to instance with least requests
- RANDOM           → Random selection
- PASSTHROUGH      → Use original destination
- CONSISTENT_HASH  → Same client → Same instance
```

### **Retry Logic**
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: retry-example
spec:
  hosts:
  - my-service
  http:
  - route:
    - destination:
        host: my-service
    retries:
      attempts: 3
      perTryTimeout: 2s
      retryOn: 5xx,reset,connect-failure
```

**What happens:**
1. Request fails → 500 error
2. Envoy retries (attempt 2) → Fails
3. Envoy retries (attempt 3) → Fails
4. Returns error to client

### **Circuit Breaker**
```yaml
outlierDetection:
  consecutive5xxErrors: 5      # 5 errors = open circuit
  interval: 30s                 # Check every 30 seconds
  baseEjectionTime: 30s         # Remove instance for 30s
  maxEjectionPercent: 50        # Max 50% of instances down
  splitExternalLocalOriginErrors: true
```

**What happens:**
```
Normal:   ✓ ✓ ✓ ✓ ✓ ✓ → Requests flowing

Error:    ✗ ✗ ✗ ✗ ✗ ✗ → 5 errors detected
          
Trigger:  Circuit opens → STOP sending traffic to this instance

Wait:     30 seconds pass

Recover:  Send 1 test request → If OK, resume traffic
```

---

## Security Features

### **mTLS (Mutual TLS)**
```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
spec:
  mtls:
    mode: STRICT  # Enforce mTLS for all traffic
```

**What happens:**
```
Without mTLS:
Client → Plain HTTP → Server
(Anyone can intercept)

With mTLS (STRICT):
Client → (Client cert) → Istio Proxy → Encrypted TLS → Istio Proxy → (Verify server cert) → Server
(Automatic encryption & certificate verification)
```

**Istio automatically:**
- Generates certificates
- Rotates certificates (every 24 hours)
- Stores in Kubernetes secrets
- Enforces mutual authentication

### **Authorization Policies**
```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: allow-api
spec:
  selector:
    matchLabels:
      app: api-service
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/default/sa/frontend"]
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/api/*"]
```

**What it does:**
- Allow requests from `frontend` service account
- Only GET/POST methods
- Only to paths starting with `/api/`
- All other traffic → DENIED

---

## Observability

### **What Istio Collects**

```
1. METRICS
   - Request rate (req/sec)
   - Error rate (4xx, 5xx)
   - Latency (p50, p95, p99)
   - Traffic volume
   
2. LOGS
   - Request/response details
   - Access logs
   - Error logs

3. TRACES
   - Full request path through system
   - Latency at each hop
   - Where time is spent
```

### **Observability Stack**
```
Envoy Proxies (collect metrics)
         ↓
Prometheus (scrapes every 15s)
         ↓
Grafana (visualizes)
         ↓
Dashboards show:
- Service topology
- Request rates
- Error rates
- Latency
```

### **Distributed Tracing (Jaeger)**
```
Request: Client → Service A → Service B → Service C

Jaeger shows:
┌─ Trace ID: 12345
├─ Span 1: Client → A (50ms)
├─ Span 2: A → B (30ms)
└─ Span 3: B → C (20ms)
Total: 100ms
```

---

## Installation Process

### **Prerequisites**
```
1. Kubernetes cluster (1.20+)
2. kubectl configured
3. Helm (optional, can use istioctl)
4. 4GB RAM, 2 CPU minimum
```

### **Installation Steps**

#### **Option 1: Using istioctl (Recommended)**
```bash
# 1. Download Istio
curl -L https://istio.io/downloadIstio | sh -
cd istio-1.18.0

# 2. Add istioctl to PATH
export PATH=$PWD/bin:$PATH

# 3. Install with default profile
istioctl install --set profile=demo -y

# 4. Enable sidecar injection for namespace
kubectl label namespace default istio-injection=enabled

# 5. Verify installation
kubectl get pods -n istio-system
```

#### **Option 2: Using Helm**
```bash
# 1. Add Istio Helm repo
helm repo add istio https://istio-release.storage.googleapis.com/charts
helm repo update

# 2. Create namespace
kubectl create namespace istio-system

# 3. Install Istio base
helm install istio-base istio/base -n istio-system

# 4. Install Istiod
helm install istiod istio/istiod -n istio-system \
  --set global.hub=docker.io/istio \
  --set global.tag=1.18.0

# 5. Install Ingress Gateway
helm install istio-ingressgateway istio/gateway \
  -n istio-system \
  --set service.type=LoadBalancer

# 6. Enable sidecar injection
kubectl label namespace default istio-injection=enabled
```

### **Post-Installation**
```bash
# Verify all pods are running
kubectl get pods -n istio-system

# Check sidecar injection is working
kubectl run nginx --image=nginx
kubectl get pods default -o jsonpath='{.items[0].spec.containers[*].name}'
# Output: nginx istio-proxy (2 containers = success!)
```

---

## Real-World Example

### **Scenario: Blue-Green Deployment with Istio**

**Setup:**
- Running version 1.0 (Blue) - 100% traffic
- Deploy version 2.0 (Green) - 0% traffic
- Gradually shift traffic to 2.0

### **Step 1: Deploy both versions**
```bash
# Both v1 and v2 running
kubectl run my-app-v1 --image=myapp:v1 --labels=version=v1
kubectl run my-app-v2 --image=myapp:v2 --labels=version=v2
```

### **Step 2: Create DestinationRule (subsets)**
```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: my-app
spec:
  host: my-app
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
```

### **Step 3: Create VirtualService (traffic split)**
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: my-app
spec:
  hosts:
  - my-app
  http:
  - route:
    - destination:
        host: my-app
        subset: v1
      weight: 100  # All traffic to v1
    - destination:
        host: my-app
        subset: v2
      weight: 0    # No traffic to v2
```

### **Step 4: Gradually shift traffic**
```yaml
# After 5 minutes - 80% v1, 20% v2
- destination:
    host: my-app
    subset: v1
  weight: 80
- destination:
    host: my-app
    subset: v2
  weight: 20

# After 10 minutes - 50% v1, 50% v2
- destination:
    host: my-app
    subset: v1
  weight: 50
- destination:
    host: my-app
    subset: v2
  weight: 50

# After 15 minutes - 0% v1, 100% v2
- destination:
    host: my-app
    subset: v1
  weight: 0
- destination:
    host: my-app
    subset: v2
  weight: 100
```

### **Result:**
```
Time:      0min    5min    10min   15min
v1:        100%    80%     50%     0%
v2:        0%      20%     50%     100%
           Blue    Phase 1 Phase 2 Green
```

---

## Istio in Your Project

Your repositories show Istio is deployed with:

### **Installation Method:**
- Helm charts (in `eip-helm-chart/`)
- Platform chart includes service mesh configuration

### **Key Configurations:**
```yaml
# From your platform-chart values.yaml:
- Service mesh enabled
- mTLS configured
- Traffic policies defined
- Observability stack (Prometheus, Grafana, Jaeger)
```

### **How it works in YOUR system:**
```
1. Terraform (eip-infra-azure-terraform-support)
   └─ Creates AKS cluster
   
2. Ansible/ArgoCD (eip-infra-k8s-support)
   └─ Installs Istio via Helm
   
3. Helm Charts (eip-helm-chart)
   └─ Configures service mesh policies
   └─ Defines traffic routing rules
   
4. Application Deployment
   └─ Pod gets Envoy sidecar injected
   └─ Service-to-service communication through Istio
   └─ Istio applies security, traffic, and observability policies
```

---

## Quick Summary

| Component | Purpose |
|-----------|---------|
| **Istiod** | Control plane - manages configuration |
| **Envoy** | Data plane - proxies traffic in each pod |
| **VirtualService** | Defines routing rules |
| **DestinationRule** | Load balancing, circuit breakers |
| **Gateway** | Ingress entry point |
| **PeerAuthentication** | mTLS security |
| **AuthorizationPolicy** | Access control |
| **Prometheus/Grafana** | Metrics visualization |
| **Jaeger** | Distributed tracing |

**The Magic:** Istio automatically handles all service-to-service communication without changing your application code!

---

**Next Step:** Would you like me to show you the specific Istio configurations in your repositories and how they're deployed?
