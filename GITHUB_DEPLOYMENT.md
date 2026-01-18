# 🚀 GitHub & Deployment Guide

## 📦 Step 1: Push to GitHub

### Initialize Git Repository

```bash
# Initialize git
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Movie Seat Booking System"
```

### Create GitHub Repository

1. Go to [GitHub](https://github.com) and log in
2. Click the **"+"** icon in the top right → **"New repository"**
3. Repository name: `seat-booking-system` (or your preferred name)
4. Description: `Production-ready Django seat booking system with concurrency control`
5. Keep it **Public** or **Private** (your choice)
6. **DO NOT** initialize with README (we already have one)
7. Click **"Create repository"**

### Push to GitHub

```bash
# Add remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/seat-booking-system.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## 🌐 Step 2: Deploy to Render (Recommended - Free Tier)

### Why Render?
- ✅ Free tier available
- ✅ Automatic deployments from GitHub
- ✅ Free PostgreSQL database
- ✅ Easy setup
- ✅ No credit card required for free tier

### Deployment Steps:

1. **Sign up at [Render](https://render.com)**
   - Use your GitHub account for easy integration

2. **Create a New Web Service**
   - Click **"New +"** → **"Web Service"**
   - Connect your GitHub repository
   - Select `seat-booking-system`

3. **Configure the Web Service**
   ```
   Name: seat-booking-system
   Region: Choose closest to you
   Branch: main
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn seat_booking.wsgi:application
   ```

4. **Add Environment Variables**
   Click **"Advanced"** → **"Add Environment Variable"**:
   
   ```
   SECRET_KEY = <generate a random secret key>
   DEBUG = False
   ALLOWED_HOSTS = .onrender.com
   ```

   To generate a SECRET_KEY, run locally:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

5. **Create PostgreSQL Database**
   - Go to Dashboard → **"New +"** → **"PostgreSQL"**
   - Name: `seat-booking-db`
   - Database: `seat_booking`
   - User: `seat_booking_user`
   - Region: Same as web service
   - Click **"Create Database"**

6. **Link Database to Web Service**
   - Copy the **Internal Database URL** from your PostgreSQL dashboard
   - Go back to your Web Service → **"Environment"**
   - Add environment variable:
     ```
     DATABASE_URL = <paste the internal database URL>
     ```

7. **Deploy!**
   - Click **"Create Web Service"**
   - Render will automatically deploy your app
   - Wait 5-10 minutes for the first deployment

8. **Run Migrations & Seed Data**
   - Once deployed, go to **"Shell"** tab
   - Run:
     ```bash
     python manage.py migrate
     python manage.py seed_data
     ```

9. **Access Your App**
   - Your app will be available at: `https://seat-booking-system.onrender.com`

---

## 🚀 Alternative: Deploy to Railway

### Why Railway?
- ✅ $5 free credit monthly
- ✅ Very fast deployments
- ✅ Automatic PostgreSQL setup
- ✅ Great developer experience

### Deployment Steps:

1. **Sign up at [Railway](https://railway.app)**

2. **Create New Project**
   - Click **"New Project"**
   - Select **"Deploy from GitHub repo"**
   - Connect and select your repository

3. **Add PostgreSQL**
   - Click **"+ New"** → **"Database"** → **"Add PostgreSQL"**
   - Railway automatically creates `DATABASE_URL`

4. **Configure Environment Variables**
   - Click on your service → **"Variables"**
   - Add:
     ```
     SECRET_KEY = <your-secret-key>
     DEBUG = False
     ALLOWED_HOSTS = .railway.app
     ```

5. **Deploy**
   - Railway automatically deploys on every push to main
   - First deployment takes ~5 minutes

6. **Run Migrations**
   - Go to your service → **"Settings"** → **"Deploy"**
   - Or use Railway CLI:
     ```bash
     railway run python manage.py migrate
     railway run python manage.py seed_data
     ```

---

## 🎯 Alternative: Deploy to Heroku

### Prerequisites:
```bash
# Install Heroku CLI
# Windows: Download from https://devcenter.heroku.com/articles/heroku-cli
```

### Deployment Steps:

```bash
# Login to Heroku
heroku login

# Create app
heroku create seat-booking-system

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set SECRET_KEY="your-secret-key-here"
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=".herokuapp.com"

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate
heroku run python manage.py seed_data

# Open app
heroku open
```

---

## 🔧 Post-Deployment Checklist

After deploying, verify:

- [ ] App loads successfully
- [ ] Database migrations completed
- [ ] Seed data loaded
- [ ] Static files serving correctly
- [ ] Admin panel accessible at `/admin/`
- [ ] API endpoints working
- [ ] Seat booking flow functional
- [ ] No errors in logs

### Test Your Deployment:

1. **Visit your app URL**
2. **Test the booking flow:**
   - Select a show
   - Hold seats
   - Confirm booking
3. **Check admin panel:**
   - Go to `/admin/`
   - Login with superuser credentials
4. **Run API tests:**
   ```bash
   # Update test_api.py with your production URL
   python test_api.py
   ```

---

## 🔄 Continuous Deployment

### Automatic Deployments

Both Render and Railway support automatic deployments:

1. **Make changes locally**
2. **Commit and push:**
   ```bash
   git add .
   git commit -m "Your changes"
   git push origin main
   ```
3. **Platform automatically deploys** the new version

---

## 🐛 Troubleshooting

### Common Issues:

**1. Static files not loading**
```bash
# Run collectstatic
python manage.py collectstatic --noinput
```

**2. Database connection errors**
- Verify `DATABASE_URL` is set correctly
- Check database is in same region as web service

**3. Application errors**
- Check logs in platform dashboard
- Verify all environment variables are set
- Ensure `DEBUG=False` in production

**4. Migration errors**
```bash
# Reset migrations (only if needed)
python manage.py migrate --run-syncdb
```

---

## 📊 Monitoring Your App

### View Logs:

**Render:**
- Dashboard → Your Service → **"Logs"** tab

**Railway:**
- Your Service → **"Deployments"** → Click deployment → **"View Logs"**

**Heroku:**
```bash
heroku logs --tail
```

---

## 🎉 Success!

Your seat booking system is now live! 🚀

**Share your app:**
- GitHub: `https://github.com/YOUR_USERNAME/seat-booking-system`
- Live App: `https://your-app.onrender.com` (or your chosen platform)

---

## 📝 Next Steps

1. **Custom Domain** (Optional)
   - Add your own domain in platform settings
   
2. **SSL Certificate**
   - Automatically provided by Render/Railway/Heroku

3. **Monitoring**
   - Set up error tracking (Sentry)
   - Add uptime monitoring

4. **Backups**
   - Enable automatic database backups in platform settings

---

**Need Help?**
- Check platform documentation
- Review deployment logs
- Verify environment variables
- Test locally first with `DEBUG=False`
