# Deploying to FastAPI Cloud

This document outlines the exact steps and architectural decisions made to deploy the Dayflow backend to **FastAPI Cloud**.

FastAPI Cloud is an optimized deployment platform specifically built for FastAPI applications, using `uv` under the hood for extremely fast dependency installation and builds.

## 🏗️ Repository Structure for Deployment

FastAPI Cloud relies heavily on auto-detection to build and serve your app. To ensure seamless deployments, our repo follows these rules:

1. **The Entrypoint:** FastAPI Cloud automatically looks for a FastAPI `app` object in standard locations, notably `app/main.py`.
2. **The Runner Script:** Our local runner script was renamed from `main.py` to `run.py`. 
   * *Why?* If a `main.py` is present in the root directory, FastAPI Cloud prioritizes it. Since our root script is just a local Uvicorn wrapper and doesn't contain the actual `app` object, it would cause a startup crash. Renaming it ensures the cloud builder seamlessly auto-detects `app/main.py`.
3. **Dependencies:** We use a `requirements.txt` file.
   * *Important Node:* We **do not** use a `pyproject.toml` file. If a `pyproject.toml` is present, the cloud builder (`uv`) assumes this is a structured Python package and demands a `[project]` or `[build-system]` table. Deleting it allows `uv` to smoothly fall back to parsing `requirements.txt`.
4. **Python Version:** The Python runtime version is explicitly set using the `.python-version` file at the root of the project (currently set to `3.12`).

## 🚀 Initial Deployment Steps

To deploy this project from scratch from your local terminal, follow these steps:

1. **Install FastAPI CLI:** Ensure you have the `fastapi` CLI tool installed (which comes bundled when installing `fastapi[standard]`).
2. **Authenticate:** Log into your FastAPI Cloud account via the CLI:
   ```bash
   fastapi login
   ```
   *This automatically opens your browser to authenticate your device.*
3. **Deploy the Code:** Trigger the build and deploy pipeline directly from the CLI:
   ```bash
   fastapi deploy
   ```
   *The CLI will upload the code, and FastAPI Cloud will spin up a container, install dependencies using `uv`, and provide you with a live HTTPS URL.*

## 🔐 Environment Variables

Since `.env` files and sensitive credentials (like `serviceAccountKey.json`) are correctly ignored by git via `.gitignore`, they will not be uploaded during deployment.

You must set your environment variables manually in the cloud instance so the app can talk to MongoDB and Firebase. You can do this in two ways:

### Option A: Via the Dashboard
Go to your project in the [FastAPI Cloud Dashboard](https://dashboard.fastapicloud.com), navigate to **Settings > Environment Variables**, and paste your values.

### Option B: Via the CLI
Set variables directly from your terminal:
```bash
fastapi env set MONGO_URI "mongodb+srv://..."
fastapi env set FIREBASE_TYPE "service_account"
fastapi env set FIREBASE_PROJECT_ID "your-project-id"
fastapi env set FIREBASE_PRIVATE_KEY "-----BEGIN PRIVATE KEY-----\n..."
# (Repeat for all required backend credentials)
```

## 🔄 Redeployment Lifecycle

Every time you make bug fixes, add new routes, or modify database models locally, you need to push those changes to the live server.

**How to trigger a redeployment:**
Simply navigate to your project root in the terminal and run:
```bash
fastapi deploy
```

That's it! FastAPI Cloud handles the zero-downtime swap of your containers. You optionally also can commit your code to GitHub, but `fastapi deploy` is what actually pushes the new code state to the cloud provider.
