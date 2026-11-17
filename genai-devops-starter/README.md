# GenAI DevOps Starter (Beginner, Spoon-Fed)

You wanted a brand-new, end-to-end starter from the architecture:

**User → Streamlit UI → FastAPI → vLLM runtime → HuggingFace model**

This repo now contains that full baseline with:

- Backend API (`FastAPI`)
- Frontend UI (`Streamlit`)
- Dockerfiles for image build
- Kaniko job manifests (build without Docker daemon on your laptop)
- Kubernetes manifest for deployment
- Unit tests

---

## 1) What each part does

## A) `frontend/app.py`
- Shows chat UI to user
- Sends prompt to backend `/chat`
- Displays answer

## B) `backend/main.py`
- Exposes:
  - `GET /health`
  - `POST /chat`
- Validates input (`prompt`, `temperature`, `max_tokens`)
- Calls LLM client

## C) `backend/llm_client.py`
- If `MOCK_MODE=true`: fake answer (for learning / no GPU)
- If `MOCK_MODE=false`: calls vLLM OpenAI-compatible endpoint

## D) `Dockerfile.backend` and `Dockerfile.frontend`
- Define image build steps
- Used by Kaniko to create container images

## E) `kaniko/*.yaml`
- Kubernetes Job definitions that run Kaniko builder
- Push backend/frontend images to your registry

## F) `k8s/genai-app.yaml`
- Deploys backend + frontend in Kubernetes
- Creates internal service for backend
- Exposes frontend via `NodePort`

---

## 2) Project layout

```text
genai-devops-starter/
├─ backend/
│  ├─ config.py
│  ├─ llm_client.py
│  └─ main.py
├─ frontend/
│  └─ app.py
├─ tests/
│  └─ test_api.py
├─ kaniko/
│  ├─ backend-kaniko-job.yaml
│  ├─ frontend-kaniko-job.yaml
│  └─ README.md
├─ k8s/
│  └─ genai-app.yaml
├─ Dockerfile.backend
├─ Dockerfile.frontend
├─ .dockerignore
├─ .env.example
├─ requirements.txt
└─ README.md
```

---

## 3) Phase-1: Run locally first (no Docker needed)

This helps you understand flow before cluster deployment.

### Step 1: Create virtual environment

```powershell
cd "c:\Users\2249525\Downloads\my project\genai-devops-starter"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 2: Install dependencies

```powershell
pip install -r requirements.txt
```

### Step 3: Create `.env`

```powershell
Copy-Item .env.example .env
```

### Step 4: Start backend

```powershell
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Step 5: Start frontend (new terminal)

```powershell
cd "c:\Users\2249525\Downloads\my project\genai-devops-starter"
.\.venv\Scripts\Activate.ps1
streamlit run frontend/app.py --server.address 0.0.0.0 --server.port 8501
```

Open `http://localhost:8501`

---

## 4) Phase-2: Build images using Kaniko (no Docker on laptop)

You will run Kaniko jobs inside Kubernetes.

### Files used
- `kaniko/backend-kaniko-job.yaml`
- `kaniko/frontend-kaniko-job.yaml`

### You must edit placeholders in those files

1. `REPLACE_WITH_REGISTRY` (example: `myacr.azurecr.io`)
2. `claimName: genai-source-pvc` (PVC containing your source under `/workspace`)
3. `secretName: regcred` (registry credentials)

Detailed notes: `kaniko/README.md`

---

## 4.1) Org-standard flow (same pattern as potato-sourcing repos)

This repo is now aligned to the same model:

1. Azure DevOps pipeline (`azure-pipeline.yaml`) runs tests.
2. Pipeline runs Kaniko job in AKS namespace to build/push image.
3. Pipeline updates image tag in `potato-sourcing-argocd-configs` for target env.
4. ArgoCD auto-sync applies new release to cluster.

So your laptop does **not** need Docker daemon installation.

Pipeline file added: `genai-devops-starter/azure-pipeline.yaml`

---

## 5) Phase-3: Deploy to Kubernetes

Manifest: `k8s/genai-app.yaml`

Before apply:
- Replace both image names:
  - `REPLACE_WITH_REGISTRY/genai-backend:latest`
  - `REPLACE_WITH_REGISTRY/genai-frontend:latest`

What deploy file creates:
- Namespace `genai-app`
- ConfigMap for app settings
- Backend deployment + service
- Frontend deployment + NodePort service

---

## 6) Tests

```powershell
cd "c:\Users\2249525\Downloads\my project\genai-devops-starter"
.\.venv\Scripts\Activate.ps1
pytest -q
```

---

## 7) What info I need from you next (to finish real deploy)

Please share these 8 items:

1. **Container Registry URL**
   - Example: `mycompany.azurecr.io`

2. **Kubernetes cluster access**
   - Do you already have `kubectl` access? (yes/no)

3. **Namespace for Kaniko jobs**
   - Current examples use `kaniko`

4. **Where source code is mounted for Kaniko**
   - PVC name that maps repo at `/workspace`

5. **Registry secret name**
   - current placeholder: `regcred`

6. **Target namespace for app**
   - current: `genai-app` (can change)

7. **Do you have GPU node for vLLM now?**
   - yes/no
   - if yes, which GPU type?

8. **Do you want external URL now or internal-only first?**
   - internal only (simpler)
   - external domain (needs ingress/gateway + DNS)

---

## 8) Current defaults (safe for beginners)

From `.env.example`:
- `MOCK_MODE=true` (works without GPU)
- backend on `:8000`
- frontend on `:8501`

So you can learn the full request/response flow first, then switch to real vLLM.

---

## 9) Next immediate action for you

1) Run Phase-1 local app.
2) Share the 8 items above.
3) I will then give you exact Kaniko + deploy commands for your environment and help test live traffic end-to-end.
