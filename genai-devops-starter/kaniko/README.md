# Kaniko Build Guide (No Docker on Laptop)

This folder is for building images in Kubernetes using Kaniko.

## What these files do

- `backend-kaniko-job.yaml` builds `Dockerfile.backend`
- `frontend-kaniko-job.yaml` builds `Dockerfile.frontend`

Both push images to your container registry.

## You must replace these values first

1. `REPLACE_WITH_REGISTRY` in both job files
   - Example: `myacr.azurecr.io`

2. `claimName: genai-source-pvc`
   - Must point to a PVC that contains your source code at `/workspace`

3. `secretName: regcred`
   - Must contain registry auth in `.dockerconfigjson` format

## Registry secret format

The secret should be created as type `kubernetes.io/dockerconfigjson`.

## Build order

1. Run backend job
2. Run frontend job
3. Verify pushed images in registry
4. Deploy app from `../k8s/genai-app.yaml`

## Why Kaniko for you

- No Docker daemon needed on your local machine
- Secure image build inside Kubernetes
- Easy to automate in CI/CD later