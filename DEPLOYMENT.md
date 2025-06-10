# DSA Questions Manager - Deployment Guide

## Dependencies

Your project uses the following Python packages:

```
Flask==3.1.1
Flask-Login==0.6.3
Flask-SQLAlchemy==3.1.1
Werkzeug==3.1.3
gunicorn==23.0.0
psycopg2-binary==2.9.10
SQLAlchemy==2.0.41
email-validator==2.2.0
```

## Deploying to Render

### Step 1: Prepare Your Repository
1. Push all your code to a GitHub repository
2. Ensure these files are included:
   - `requirements.txt` (already created)
   - `Procfile` (already created)
   - `runtime.txt` (already created)
   - `render.yaml` (already created)

### Step 2: Create Render Account
1. Go to [render.com](https://render.com) and sign up
2. Connect your GitHub account

### Step 3: Deploy Using Render Blueprint (Recommended)
1. In Render dashboard, click "New" → "Blueprint"
2. Connect your GitHub repository
3. Render will automatically detect the `render.yaml` file
4. This will create both:
   - PostgreSQL database
   - Web service

### Step 4: Manual Deployment (Alternative)
If you prefer manual setup:

#### Create Database:
1. Click "New" → "PostgreSQL"
2. Name: `dsa-questions-db`
3. Database Name: `dsa_questions`
4. User: `dsa_user`
5. Select free tier
6. Create database

#### Create Web Service:
1. Click "New" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `dsa-questions-manager`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT main:app`
   - **Python Version**: Select Python 3.11

#### Set Environment Variables:
In your web service settings, add:
- `SESSION_SECRET`: Generate a random string (32+ characters)
- `DATABASE_URL`: Copy from your PostgreSQL database's "External Database URL"

### Step 5: Environment Variables

#### Required Variables:
- `DATABASE_URL`: PostgreSQL connection string (automatically set if using blueprint)
- `SESSION_SECRET`: Random secret key for sessions

#### Example values:
```
DATABASE_URL=postgresql://username:password@host:port/database_name
SESSION_SECRET=your-super-secret-random-string-here
```

### Step 6: Database Setup
The application will automatically create the necessary tables when it starts for the first time.

### Step 7: Access Your Application
Once deployed, your app will be available at: `https://your-app-name.onrender.com`

## Local Development

### Database Connection
For local development, set these environment variables:
```bash
export DATABASE_URL="postgresql://username:password@localhost:5432/dsa_questions"
export SESSION_SECRET="your-local-secret-key"
```

### Running Locally
```bash
pip install -r requirements.txt
python main.py
```

## Troubleshooting

### Common Issues:
1. **Database connection errors**: Verify DATABASE_URL is correct
2. **Session errors**: Ensure SESSION_SECRET is set
3. **Build failures**: Check requirements.txt has all dependencies

### Database Migration:
If you need to reset the database:
1. Access Render PostgreSQL dashboard
2. Connect to database console
3. Run: `DROP TABLE IF EXISTS users, dsa_question CASCADE;`
4. Restart your web service

## Features
- User authentication (signup/login)
- Password hashing and security
- Personal question management
- Search and filtering
- Responsive design
- PostgreSQL database integration

Your application is ready for deployment on Render with full authentication and database functionality!