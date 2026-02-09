# Domain Configuration Guide for Firebase Hosting

## Current Setup
- Firebase Project: `ignite-ai-01`
- Default URL: https://ignite-ai-01.web.app
- Custom Domains to Configure:
  - `igniteai.in` → Landing page
  - `app.igniteai.in` → Full application

## Step 1: Update Backend CORS (Required First!)

Add these domains to backend CORS allow list in `projects/backend/main.py`:
- https://igniteai.in
- https://app.igniteai.in  
- https://ignite-ai-01.web.app (keep for testing)

## Step 2: Add Custom Domains in Firebase Console

### Via Firebase Console (Recommended - UI)
1. Go to: https://console.firebase.google.com/project/ignite-ai-01/hosting/sites
2. Click "Add custom domain"
3. Enter: `igniteai.in`
4. Firebase will provide TXT record for verification
5. Add TXT record to your domain DNS
6. Verify ownership
7. Firebase will provide A records
8. Update DNS with A records
9. Repeat for `app.igniteai.in`

### Via CLI (Alternative)
```bash
# Connect custom domain
firebase hosting:channel:create igniteai-in --site ignite-ai-01
firebase hosting:channel:create app-igniteai-in --site ignite-ai-01
```

## Step 3: DNS Configuration

Add these records to your domain registrar (e.g., GoDaddy, Namecheap):

### For igniteai.in (root domain):
```
Type: A
Name: @
Value: 151.101.1.195
Value: 151.101.65.195
TTL: 3600
```

### For app.igniteai.in (subdomain):
```
Type: A
Name: app
Value: 151.101.1.195
Value: 151.101.65.195
TTL: 3600
```

### SSL Verification (Firebase auto-provisions):
```
Type: TXT
Name: _acme-challenge
Value: <provided-by-firebase>
TTL: 3600
```

## Step 4: Update Firebase Hosting Config (Optional)

If you want different deployments for landing vs app:

```json
{
  "hosting": [
    {
      "target": "landing",
      "public": "dist/landing",
      "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
      "rewrites": [{"source": "**", "destination": "/index.html"}]
    },
    {
      "target": "app",
      "public": "projects/frontend/dist/frontend/browser",
      "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
      "rewrites": [{"source": "**", "destination": "/index.html"}]
    }
  ]
}
```

Then in `.firebaserc`:
```json
{
  "projects": {
    "default": "ignite-ai-01"
  },
  "targets": {
    "ignite-ai-01": {
      "hosting": {
        "landing": ["igniteai-in"],
        "app": ["ignite-ai-01", "app-igniteai-in"]
      }
    }
  }
}
```

## Step 5: Deploy
```bash
# Deploy to specific targets
firebase deploy --only hosting:landing
firebase deploy --only hosting:app

# Or deploy all
firebase deploy --only hosting
```

## Timeline
- DNS propagation: 5 minutes - 48 hours (usually <30 min)
- SSL certificate provisioning: Automatic after DNS verified (~15 min)

## Verification
```bash
# Check DNS propagation
dig igniteai.in
dig app.igniteai.in

# Test HTTPS after SSL provisioned
curl -I https://igniteai.in
curl -I https://app.igniteai.in
```
