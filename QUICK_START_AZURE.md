# Quick Start: Azure Deployment

Fast-track guide to get your backend deployed to Azure.

## Prerequisites Checklist

- [ ] Azure CLI installed
- [ ] Logged into Azure (`az login`)
- [ ] GitHub repository access

## 5-Minute Setup

### 1. Create Azure Resources (5 commands)

```bash
# Set variables (CHANGE THESE if names are taken)
REGISTRY_NAME="runningtracker"
RG="running-tracker-rg"
DB_PASSWORD="ChangeMe123!@#"

# Create everything
az group create --name $RG --location eastus

az acr create --resource-group $RG --name $REGISTRY_NAME --sku Basic --admin-enabled true

az containerapp env create --name running-tracker-env --resource-group $RG --location eastus

az postgres flexible-server create \
  --resource-group $RG \
  --name running-tracker-db \
  --location eastus \
  --admin-user dbadmin \
  --admin-password "$DB_PASSWORD" \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --version 15 \
  --public-access 0.0.0.0

az postgres flexible-server db create \
  --resource-group $RG \
  --server-name running-tracker-db \
  --database-name running_tracker_prod
```

### 2. Get Your Subscription ID

```bash
az account show --query id -o tsv
```

Copy this ID.

### 3. Create Service Principal

```bash
az ad sp create-for-rbac \
  --name "running-tracker-github" \
  --role contributor \
  --scopes /subscriptions/YOUR_SUBSCRIPTION_ID/resourceGroups/running-tracker-rg \
  --sdk-auth
```

Replace `YOUR_SUBSCRIPTION_ID` with the ID from step 2.

Copy the entire JSON output.

### 4. Add GitHub Secrets

Go to: `https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions/new`

Add these 3 secrets:

| Secret Name | Value |
|-------------|-------|
| `AZURE_CREDENTIALS` | The JSON from step 3 |
| `DATABASE_URL` | `postgresql://dbadmin:ChangeMe123!@#@running-tracker-db.postgres.database.azure.com/running_tracker_prod?sslmode=require` |
| `JWT_SECRET` | Run: `openssl rand -base64 32` and paste result |

### 5. Deploy Backend

```bash
git add .
git commit -m "Add Azure deployment"
git push origin production
```

### 6. Get API Gateway URL

Wait for the GitHub Action to complete (~5-10 minutes), then:

```bash
az containerapp show \
  --name api-gateway \
  --resource-group running-tracker-rg \
  --query properties.configuration.ingress.fqdn \
  -o tsv
```

### 7. Update Frontend

Add one more GitHub secret:

| Secret Name | Value |
|-------------|-------|
| `VITE_API_URL` | `https://YOUR_API_GATEWAY_URL_FROM_STEP_6` |

### 8. Update CORS

Get your Static Web App URL (e.g., `https://green-glacier-0b13c9310.1.azurestaticapps.net`), then:

```bash
az containerapp update \
  --name api-gateway \
  --resource-group running-tracker-rg \
  --set-env-vars \
    ALLOWED_ORIGINS="https://YOUR_STATIC_WEB_APP_URL,http://localhost:5173"
```

### 9. Redeploy Frontend

```bash
git commit --allow-empty -m "Update API URL"
git push origin production
```

## Test It!

1. Visit your Static Web App URL
2. Register a new account
3. Login
4. Create a training plan

## Troubleshooting

**"Failed to fetch" error?**
- Check CORS: Did you add your Static Web App URL in step 8?
- Check API URL secret: Is `VITE_API_URL` set correctly in GitHub secrets?

**Can't connect to database?**
- Verify `DATABASE_URL` format is correct
- Check firewall allows Azure services (0.0.0.0 rule)

**GitHub Action fails?**
- Verify `AZURE_CREDENTIALS` secret is valid
- Check ACR name is unique and matches workflow

**Still stuck?**
See full documentation: [AZURE_DEPLOYMENT.md](./AZURE_DEPLOYMENT.md)

## Useful Commands

```bash
# View all container apps
az containerapp list --resource-group running-tracker-rg --output table

# View logs
az containerapp logs show --name api-gateway --resource-group running-tracker-rg --follow

# Restart a service
az containerapp revision restart --name api-gateway --resource-group running-tracker-rg

# Delete everything
az group delete --name running-tracker-rg --yes
```

## Cost Estimate

- Container Apps: ~$15-30/month
- PostgreSQL Flexible Server (Burstable): ~$15/month
- Container Registry (Basic): ~$5/month
- Static Web Apps: Free tier

**Total**: ~$35-50/month

To reduce costs, scale down database tier or use container apps scale-to-zero.
