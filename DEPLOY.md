# Deploying Slangify

Slangify is an always-on Discord bot. It holds a persistent gateway WebSocket,
so it needs a long-running process — **not** serverless / scale-to-zero. The
current deployment target is **Azure Container Instances (ACI)**, using a Docker
image stored in **Azure Container Registry (ACR)**.

## Architecture

```
Mac (build) --buildx--> image (linux/amd64) --push--> ACR --pull--> ACI (runs 24/7)
```

- **ACR** — cloud image store (the registry: `slangifyacr`).
- **ACI** — runs the container always-on with `--restart-policy Always`.
- Secrets (`DISCORD_TOKEN`, `GEMINI_API_KEY`) are injected at runtime as
  **secure environment variables** — never baked into the image.

> **Arch note:** Apple Silicon builds ARM images by default; ACI runs x86.
> Always build with `--platform linux/amd64` or the container won't start.

---

## Prerequisites

- Docker Desktop running (provides the build engine).
- Azure CLI: `brew install azure-cli`, then `az login`.
- One-time per subscription, register the resource providers:
  ```bash
  az provider register --namespace Microsoft.ContainerRegistry
  az provider register --namespace Microsoft.ContainerInstance
  # wait until both report Registered:
  az provider show --namespace Microsoft.ContainerRegistry --query registrationState -o tsv
  ```

Names used below (change if yours differ):

| Thing | Value |
|-------|-------|
| Resource group | `slangify-rg` |
| Registry (ACR) | `slangifyacr` |
| Container (ACI) | `slangify-bot` |
| Image | `slangify` |

---

## First-time setup

```bash
# Resource group (a folder for all related Azure resources)
az group create --name slangify-rg --location eastus

# Registry (name must be globally unique, lowercase, no dashes)
az acr create --resource-group slangify-rg --name slangifyacr \
  --sku Basic --admin-enabled true
```

---

## Build & push the image

Server-side build (`az acr build`) is **blocked on student/sponsored
subscriptions** (`TasksOperationsNotAllowed`). Build locally and push instead:

```bash
# Authenticate Docker to the registry
az acr login --name slangifyacr

# Cross-build x86 image and push in one step
docker buildx build --platform linux/amd64 \
  -t slangifyacr.azurecr.io/slangify:v1 --push .

# Verify the tag landed
az acr repository show-tags --name slangifyacr --repository slangify
```

---

## Deploy to ACI

```bash
# Get registry pull credentials
az acr credential show --name slangifyacr   # note username + a password

# Create the container (fill in <...> placeholders)
az container create \
  --resource-group slangify-rg \
  --name slangify-bot \
  --image slangifyacr.azurecr.io/slangify:v1 \
  --registry-login-server slangifyacr.azurecr.io \
  --registry-username <acr-user> \
  --registry-password <acr-pass> \
  --secure-environment-variables DISCORD_TOKEN=<token> GEMINI_API_KEY=<key> \
  --restart-policy Always \
  --os-type Linux --cpu 1 --memory 1
```

Get `<token>` / `<key>` from `.env`. Pass them on the command line — do not
commit them anywhere.

---

## Updating after a code change

ACI does not hot-swap the image. Bump the tag, then delete and recreate:

```bash
docker buildx build --platform linux/amd64 \
  -t slangifyacr.azurecr.io/slangify:v2 --push .

az container delete -g slangify-rg -n slangify-bot --yes
az container create ... --image slangifyacr.azurecr.io/slangify:v2 ...   # same flags, new tag
```

---

## Operating the bot

```bash
# Logs (one-shot) / live stream
az container logs   -g slangify-rg -n slangify-bot
az container attach -g slangify-rg -n slangify-bot

# State (expect: Running)
az container show -g slangify-rg -n slangify-bot --query instanceView.state -o tsv

# Stop (save credit) / start again
az container stop  -g slangify-rg -n slangify-bot
az container start -g slangify-rg -n slangify-bot
```

A healthy boot logs the bot logging in and connecting to the gateway. If it
crash-loops, the logs usually show a missing env var or an image pull error.

---

## Cost & longevity

- ACI bills for vCPU + memory while running. The `--cpu 1 --memory 1` values
  in the create command are the smallest supported allocation for a Linux
  container *group*, so they are the cheapest reliable always-on ACI option.
  `az container stop` when idle to conserve credit.
- This runs on Azure student credit, which expires. The `Dockerfile` makes the
  bot portable — the same image runs on Heroku, DigitalOcean App Platform, or
  any container host when it's time to migrate.
