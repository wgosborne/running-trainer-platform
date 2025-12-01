# Azure Deployment Guide

This guide walks you through deploying the Running Tracker Platform to Azure using Container Apps and Static Web Apps.

## Architecture Overview

- **Frontend**: Azure Static Web Apps (already deployed)
- **Backend Services**: Azure Container Apps
  - API Gateway (public-facing)
  - Auth Service
  - Running Trainer Service
  - PDF Service
  - Strava Service
- **Database**: Azure Database for PostgreSQL

## Prerequisites

- Azure CLI installed (`az --version`)
- Azure subscription
- GitHub repository with Actions enabled
- Docker (for local testing)

## Step 1: Create Azure Resources

### 1.1 Login to Azure

```bash
az login
```

### 1.2 Create Resource Group

```bash
az group create \
  --name running-tracker-rg \
  --location eastus
```

### 1.3 Create Azure Container Registry (ACR)

```bash
az acr create \
  --resource-group running-tracker-rg \
  --name runningtracker \
  --sku Basic \
  --admin-enabled true
```

**Note**: The registry name must be globally unique. If `runningtracker` is taken, try `runningtracker<yourname>` or similar.

### 1.4 Create Container App Environment

```bash
az containerapp env create \
  --name running-tracker-env \
  --resource-group running-tracker-rg \
  --location eastus
```

### 1.5 Create Azure Database for PostgreSQL

```bash
# Create PostgreSQL Flexible Server
az postgres flexible-server create \
  --resource-group running-tracker-rg \
  --name running-tracker-db \
  --location eastus \
  --admin-user dbadmin \
  --admin-password '<YOUR_STRONG_PASSWORD>' \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --version 15 \
  --storage-size 32

# Create database
az postgres flexible-server db create \
  --resource-group running-tracker-rg \
  --server-name running-tracker-db \
  --database-name running_tracker_prod

# Allow Azure services to access the database
az postgres flexible-server firewall-rule create \
  --resource-group running-tracker-rg \
  --name running-tracker-db \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

**Save the connection string**:
```
postgresql://dbadmin:<YOUR_STRONG_PASSWORD>@running-tracker-db.postgres.database.azure.com/running_tracker_prod?sslmode=require
```

## Step 2: Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions → New repository secret

Add the following secrets:

### 2.1 Azure Credentials

Create a service principal:

```bash
az ad sp create-for-rbac \
  --name "running-tracker-github" \
  --role contributor \
  --scopes /subscriptions/<YOUR_SUBSCRIPTION_ID>/resourceGroups/running-tracker-rg \
  --sdk-auth
```

Copy the entire JSON output and add it as a secret named **`AZURE_CREDENTIALS`**

### 2.2 Database Connection String

**Secret name**: `DATABASE_URL`
**Value**: The PostgreSQL connection string from Step 1.5

### 2.3 JWT Secret

**Secret name**: `JWT_SECRET`
**Value**: Generate a random secret:

```bash
openssl rand -base64 32
```

### 2.4 Strava Credentials (Optional)

If using Strava integration:

**Secret name**: `STRAVA_CLIENT_ID`
**Value**: Your Strava app client ID

**Secret name**: `STRAVA_CLIENT_SECRET`
**Value**: Your Strava app client secret

### 2.5 Frontend API URL

This will be set after backend deployment (Step 4)

## Step 3: Deploy Backend Services

### 3.1 Update Workflow Variables

Edit `.github/workflows/azure-backend-deploy.yml` if needed:
- Update `AZURE_CONTAINER_REGISTRY` if you used a different name
- Update `RESOURCE_GROUP` if you used a different name
- Update `LOCATION` if you chose a different region

### 3.2 Trigger Deployment

Push to the `production` branch or manually trigger the workflow:

```bash
git add .
git commit -m "Configure Azure deployment"
git push origin production
```

Or manually from GitHub:
1. Go to Actions tab
2. Select "Deploy Backend to Azure Container Apps"
3. Click "Run workflow"

### 3.3 Verify Deployment

After the workflow completes, check your Container Apps:

```bash
az containerapp list \
  --resource-group running-tracker-rg \
  --output table
```

### 3.4 Get API Gateway URL

```bash
az containerapp show \
  --name api-gateway \
  --resource-group running-tracker-rg \
  --query properties.configuration.ingress.fqdn \
  -o tsv
```

This will output something like: `api-gateway.nicegrass-12345.eastus.azurecontainerapps.io`

Your full API URL is: `https://api-gateway.nicegrass-12345.eastus.azurecontainerapps.io`

## Step 4: Configure Frontend to Use Backend

### 4.1 Add Frontend Secret

Go to GitHub repository → Settings → Secrets → New repository secret

**Secret name**: `VITE_API_URL`
**Value**: `https://<your-api-gateway-fqdn>` (from Step 3.4)

### 4.2 Update API Gateway CORS

Add your Static Web App URL to the API Gateway's allowed origins.

First, get your Static Web App URL (something like `https://green-glacier-0b13c9310.1.azurestaticapps.net`)

Then update the API Gateway:

```bash
az containerapp update \
  --name api-gateway \
  --resource-group running-tracker-rg \
  --set-env-vars \
    ALLOWED_ORIGINS="https://green-glacier-0b13c9310.1.azurestaticapps.net,http://localhost:5173"
```

Replace `https://green-glacier-0b13c9310.1.azurestaticapps.net` with your actual Static Web App URL.

### 4.3 Redeploy Frontend

Push a commit to trigger frontend rebuild with the new API URL:

```bash
git commit --allow-empty -m "Update frontend API URL"
git push origin production
```

## Step 5: Verify Everything Works

1. **Test Backend Health**:
   ```bash
   curl https://<your-api-gateway-fqdn>/health
   ```

   Expected response: `{"status":"healthy","service":"api-gateway"}`

2. **Test Frontend**:
   - Navigate to your Static Web App URL
   - Try to register a new account
   - Login
   - Create a training plan

## Step 6: Initialize Database (First Time Only)

The Running Trainer service will automatically create tables on first run. To verify:

```bash
# Get running trainer logs
az containerapp logs show \
  --name running-trainer-service \
  --resource-group running-tracker-rg \
  --follow
```

If you need to manually initialize the database:

```bash
# Connect to PostgreSQL
az postgres flexible-server connect \
  --name running-tracker-db \
  --admin-user dbadmin \
  --admin-password '<YOUR_PASSWORD>'
```

## Troubleshooting

### Issue: Frontend shows "Failed to fetch"

**Solution**:
1. Verify the API Gateway is running: `az containerapp show --name api-gateway --resource-group running-tracker-rg`
2. Check CORS configuration includes your Static Web App URL
3. Verify `VITE_API_URL` secret is set correctly in GitHub

### Issue: Backend services can't connect to database

**Solution**:
1. Verify `DATABASE_URL` secret is correct
2. Check firewall rules allow Azure services
3. Check Container App logs:
   ```bash
   az containerapp logs show \
     --name running-trainer-service \
     --resource-group running-tracker-rg \
     --follow
   ```

### Issue: Services can't communicate with each other

**Solution**:
Container Apps in the same environment can communicate using their service names:
- `http://running-trainer-service`
- `http://auth-service`
- `http://pdf-service`
- `http://strava-service`

Verify they're all in the same Container App Environment.

### Issue: Deployment fails with image not found

**Solution**:
1. Check ACR credentials:
   ```bash
   az acr credential show --name runningtracker
   ```
2. Grant Container Apps pull access:
   ```bash
   az role assignment create \
     --assignee <container-app-identity> \
     --scope /subscriptions/<sub-id>/resourceGroups/running-tracker-rg/providers/Microsoft.ContainerRegistry/registries/runningtracker \
     --role AcrPull
   ```

## Cost Optimization

- **Container Apps**: Scale-to-zero for low-traffic services (Strava, PDF)
- **Database**: Use Burstable tier for development/testing
- **Container Registry**: Basic tier is sufficient for small teams

To enable scale-to-zero for Strava service:
```bash
az containerapp update \
  --name strava-service \
  --resource-group running-tracker-rg \
  --min-replicas 0
```

## Monitoring

### View Container App Metrics

```bash
# View all container apps status
az containerapp list \
  --resource-group running-tracker-rg \
  --output table

# View specific app logs
az containerapp logs show \
  --name api-gateway \
  --resource-group running-tracker-rg \
  --follow
```

### Set up Application Insights (Optional)

```bash
# Create Application Insights
az monitor app-insights component create \
  --app running-tracker-insights \
  --location eastus \
  --resource-group running-tracker-rg

# Get instrumentation key
az monitor app-insights component show \
  --app running-tracker-insights \
  --resource-group running-tracker-rg \
  --query instrumentationKey
```

Add the instrumentation key to your Container Apps as an environment variable.

## Cleanup

To delete all resources:

```bash
az group delete --name running-tracker-rg --yes --no-wait
```

## Summary

You now have:
- ✅ Frontend deployed to Azure Static Web Apps
- ✅ Backend microservices deployed to Azure Container Apps
- ✅ PostgreSQL database on Azure
- ✅ Automated CI/CD with GitHub Actions
- ✅ HTTPS enabled on all services
- ✅ Secure secrets management

Your app is production-ready!

## Next Steps

- Set up custom domain for frontend
- Configure monitoring and alerts
- Set up automated backups for database
- Implement rate limiting in API Gateway
- Add Application Insights for detailed monitoring
