# 🚀 Deploy NJIT Elective Advisor to Vercel

## ✅ Quick Vercel Deployment (5 minutes)

### 1. **Prepare Your Repository**
```bash
# Make sure you have these files (already created):
# ✅ vercel.json
# ✅ requirements.txt  
# ✅ app.py
# ✅ All your source files
```

### 2. **Deploy to Vercel**

#### Option A: GitHub Integration (Recommended)
1. **Push to GitHub** (if not already):
   ```bash
   git add .
   git commit -m "Ready for Vercel deployment"
   git push origin main
   ```

2. **Visit Vercel Dashboard**:
   - Go to [vercel.com](https://vercel.com)
   - Sign up/login with GitHub
   - Click "New Project"
   - Select your `NJITElectiveAdvisor` repository
   - Click "Deploy"

#### Option B: Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Follow the prompts:
# ? Set up and deploy "~/NJITElectiveAdvisor"? Y
# ? Which scope do you want to deploy to? [Your account]
# ? Link to existing project? N
# ? What's your project's name? njit-elective-advisor
# ? In which directory is your code located? ./
```

### 3. **Set Environment Variables**

In Vercel Dashboard → Project → Settings → Environment Variables:

```
SECRET_KEY = your-secret-key-here-generate-new-one
FLASK_ENV = production
FLASK_DEBUG = False
SESSION_COOKIE_SECURE = True
```

### 4. **Generate Secret Key**
```python
# Run this locally to generate a secure key:
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. **Test Your Deployment**
- Your app will be live at: `https://your-project-name.vercel.app`
- Test registration, login, and course recommendations
- Check that all features work

## 🔧 Vercel Configuration Explained

### `vercel.json` Contents:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ],
  "env": {
    "FLASK_ENV": "production"
  }
}
```

### What this does:
- **`builds`**: Tells Vercel to use Python runtime for `app.py`
- **`routes`**: Routes all URLs to your Flask app
- **`env`**: Sets production environment

## ✅ Vercel Advantages

### Why Vercel is Perfect:
- ✅ **Free tier**: Generous limits for student projects
- ✅ **Automatic HTTPS**: SSL certificates included
- ✅ **Global CDN**: Fast worldwide access
- ✅ **Auto-deploy**: Deploys on every git push
- ✅ **Custom domains**: Add your own domain easily
- ✅ **Environment variables**: Secure config management
- ✅ **Serverless**: Scales automatically
- ✅ **No server management**: Zero DevOps needed

### Vercel Free Tier Includes:
- ✅ 100GB bandwidth/month
- ✅ 100 deployments/day
- ✅ Serverless functions
- ✅ Custom domains
- ✅ Automatic HTTPS

## 🎯 Post-Deployment Steps

### 1. **Update Database**
Your SQLite database will work on Vercel, but data is ephemeral. For production:
- Data resets on each deployment
- Consider upgrading to PostgreSQL (Vercel Postgres)

### 2. **Custom Domain** (Optional)
```bash
# Add custom domain in Vercel dashboard
# Settings → Domains → Add domain
```

### 3. **Monitoring**
- Vercel provides analytics and logs
- Monitor in dashboard → Functions → View logs

## 🚨 Important Notes

### Database Limitation:
- SQLite files reset on deployment
- Users will need to re-register after updates
- For persistent data, consider:
  - **Vercel Postgres** (recommended)
  - **Supabase** (PostgreSQL)
  - **PlanetScale** (MySQL)

### Quick PostgreSQL Upgrade:
```bash
# Install psycopg2 for PostgreSQL
pip install psycopg2-binary

# Update DATABASE_URL in environment variables:
# DATABASE_URL=postgresql://username:password@host:port/database
```

## 🎉 Success!

Your NJIT Elective Advisor is now live on Vercel!

**Example URL**: `https://njit-elective-advisor-123.vercel.app`

### What Students Can Do:
- ✅ Register and create accounts
- ✅ Get personalized course recommendations  
- ✅ Save courses for future reference
- ✅ Explore 25+ interest categories
- ✅ Cross-department course discovery

**Ready for real student use!** 🎓✨