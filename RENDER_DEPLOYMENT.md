# Deployment Guide for Render

## Problem Fixed

The static files (CSS, JS) were not loading on production because:
1. `collectstatic` was not being run during deployment
2. No build script was configured in Render

## Solution

Created `build.sh` that:
- Installs dependencies
- **Runs `collectstatic` to collect all static files**
- Runs database migrations
- Creates admin user if needed

## Deployment Steps

### Option 1: Using render.yaml (Recommended)

1. **Push changes to GitHub:**
   ```bash
   git add build.sh render.yaml
   git commit -m "Add Render deployment configuration"
   git push
   ```

2. **In Render Dashboard:**
   - Go to your service settings
   - Click "Deploy" → "Deploy latest commit"
   - Or connect via "Blueprint" and select `render.yaml`

### Option 2: Manual Configuration

1. **In Render Dashboard:**
   - Go to your web service
   - Settings → Build & Deploy

2. **Set Build Command:**
   ```bash
   ./build.sh
   ```

3. **Set Start Command:**
   ```bash
   cd backend && gunicorn config.wsgi:application --workers 2 --bind 0.0.0.0:$PORT
   ```

4. **Environment Variables (must be set):**
   - `DJANGO_DEBUG=False`
   - `DJANGO_SECRET_KEY=<generate-random-key>`
   - `DATABASE_URL=<your-postgres-url>`
   - `DJANGO_ALLOWED_HOSTS=<your-render-url>`
   - `IS_BEHIND_PROXY=True`
   - `USE_TLS=True`

5. **Deploy:**
   - Click "Manual Deploy" → "Deploy latest commit"

## Verification

After deployment:
1. Check build logs for "Build completed successfully!"
2. Visit your site - static files should load
3. Check browser console - no 404 errors

## Static Files Configuration

The project uses **WhiteNoise** to serve static files in production:
- Configuration: `backend/config/settings/base.py` (lines 213-229)
- Static files collected to: `backend/staticfiles/`
- WhiteNoise compression enabled for production

## Troubleshooting

If static files still don't load:

1. **Check build logs:**
   ```
   Render Dashboard → Your Service → Logs
   ```
   Look for "Collecting static files" message

2. **Verify STATIC_ROOT:**
   ```bash
   ls backend/staticfiles/
   ```
   Should contain `admin/`, `css/`, `js/`, etc.

3. **Check DEBUG setting:**
   ```
   DJANGO_DEBUG must be False in production
   ```

4. **Verify WhiteNoise middleware:**
   Should be in MIDDLEWARE list (line 99 of base.py)
