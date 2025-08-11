# GitHub Secrets Configuration Guide

This file lists all the secrets you need to configure in your GitHub repository settings for the workflows to work properly.

## How to Set Up Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** > **Secrets and variables** > **Actions**
3. Click **New repository secret** for each secret below

## Required Secrets

### 🐳 Docker Registry

```
DOCKER_USERNAME=gopikant5jan
DOCKER_PASSWORD=your-dockerhub-password-or-token
```

### 🌐 Environment URLs

```
PRODUCTION_API_URL=https://api.insurge-ai.com
STAGING_API_URL=https://staging-api.insurge-ai.com
```

### 🗄️ Database Configuration

#### Production Database

```
PRODUCTION_DB_HOST=your-prod-db-host.com
PRODUCTION_DB_USER=prod_db_user
PRODUCTION_DB_PASSWORD=super-secure-prod-password
PRODUCTION_DB_NAME=insurge_ai_prod
```

#### Staging Database

```
STAGING_DB_HOST=your-staging-db-host.com
STAGING_DB_USER=staging_db_user
STAGING_DB_PASSWORD=secure-staging-password
STAGING_DB_NAME=insurge_ai_staging
```

### 🚀 Deployment Configuration

#### Production Server

```
PRODUCTION_HOST=your-prod-server.com
PRODUCTION_USER=deploy-user
PRODUCTION_SSH_KEY=-----BEGIN OPENSSH PRIVATE KEY-----
your-private-ssh-key-content-here
-----END OPENSSH PRIVATE KEY-----
```

#### Staging Server

```
STAGING_HOST=your-staging-server.com
STAGING_USER=deploy-user
STAGING_SSH_KEY=-----BEGIN OPENSSH PRIVATE KEY-----
your-staging-private-ssh-key-content-here
-----END OPENSSH PRIVATE KEY-----
```

### ☁️ AWS S3 Configuration

```
AWS_ACCESS_KEY_ID=AKIA1234567890EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
PRODUCTION_BACKUP_BUCKET=insurge-ai-prod-backups
STAGING_BACKUP_BUCKET=insurge-ai-staging-backups
```

### 🔍 Health Monitoring

```
HEALTH_CHECK_EMAIL=healthcheck@insurge-ai.com
HEALTH_CHECK_PASSWORD=health-check-user-password
```

### 📢 Notifications

```
SLACK_WEBHOOK=https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX
```

## Optional Secrets (for enhanced features)

### 🤖 AI Services

```
OPENAI_API_KEY=sk-1234567890abcdef1234567890abcdef1234567890abcdef
```

### 📧 Email Services (if you add email notifications)

```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-email-app-password
```

### 🔐 Additional Security

```
JWT_SECRET_KEY=your-super-secret-jwt-key-here
ENCRYPTION_KEY=your-encryption-key-for-sensitive-data
```

## Environment Variables vs Secrets

### Use **Secrets** for:

- Passwords and API keys
- Database credentials
- SSH private keys
- Webhook URLs
- Any sensitive information

### Use **Variables** (not secrets) for:

- Public configuration
- Non-sensitive URLs
- Feature flags
- Build configurations

## Setting Up SSH Keys

### 1. Generate SSH Key Pair

```bash
ssh-keygen -t rsa -b 4096 -C "github-actions@insurge-ai.com"
```

### 2. Add Public Key to Servers

Copy the public key (`id_rsa.pub`) to your server:

```bash
ssh-copy-id -i ~/.ssh/id_rsa.pub user@your-server.com
```

### 3. Add Private Key to GitHub Secrets

Copy the entire private key (`id_rsa`) content and add it as `PRODUCTION_SSH_KEY` or `STAGING_SSH_KEY`

## Database Backup Setup

### 1. Create S3 Buckets

```bash
aws s3 mb s3://insurge-ai-prod-backups
aws s3 mb s3://insurge-ai-staging-backups
```

### 2. Set Bucket Lifecycle Policy

Create a lifecycle policy to automatically delete old backups:

```json
{
  "Rules": [
    {
      "ID": "DeleteOldBackups",
      "Status": "Enabled",
      "Filter": { "Prefix": "database-backups/" },
      "Expiration": { "Days": 30 }
    }
  ]
}
```

## Slack Webhook Setup

1. Go to your Slack workspace
2. Navigate to **Apps** > **Incoming Webhooks**
3. Create a new webhook for your channel
4. Copy the webhook URL and add it as `SLACK_WEBHOOK` secret

## Security Best Practices

1. **Rotate secrets regularly** (every 3-6 months)
2. **Use least privilege principle** for all credentials
3. **Monitor secret usage** in GitHub Actions logs
4. **Never log sensitive information** in workflows
5. **Use different credentials** for staging and production
6. **Enable 2FA** on all service accounts

## Testing Secrets Setup

After setting up secrets, you can test them by:

1. **Triggering workflows** - Push code to trigger CI/CD
2. **Manual workflow dispatch** - Run workflows manually
3. **Check workflow logs** - Verify connections work
4. **Monitor deployments** - Ensure deployments succeed

## Troubleshooting

### Common Issues:

1. **Secret not found**: Make sure secret name matches exactly in workflow
2. **Permission denied**: Check SSH key and server permissions
3. **Database connection failed**: Verify database credentials and network access
4. **S3 upload failed**: Check AWS credentials and bucket permissions
5. **Slack notifications not working**: Verify webhook URL and permissions

### Debug Steps:

1. Check **Actions** tab for workflow run details
2. Review **job logs** for specific error messages
3. Test credentials manually before adding to secrets
4. Use **workflow_dispatch** trigger for manual testing

Remember: Never commit real secrets to your repository. Always use GitHub Secrets for sensitive information!
