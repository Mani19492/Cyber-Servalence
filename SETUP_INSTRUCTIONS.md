# Supabase Database Setup Instructions

## Step 1: Create Supabase Project

1. Go to https://app.supabase.com
2. Sign in or create an account
3. Click "New Project"
4. Fill in your project details
5. Wait for the project to be created

## Step 2: Enable Vector Extension (for face embeddings)

1. In your Supabase project, go to **Database** → **Extensions**
2. Search for "vector" or "pgvector"
3. Enable the **pgvector** extension
4. Click "Enable"

## Step 3: Update .env File

1. Go to your Supabase project **Settings** → **API**
2. Copy your **Project URL** (supabase_url)
3. Copy your **anon public** key (supabase_key)
4. Update the `.env` file in the project root:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
FERNET_KEY=KYS-64QjEcP37xXZ7oFkJovna_g6Zxd40B6vnxaKmrI=
JWT_SECRET=7i1-PNqMNvrn5SZL7AmAfVa0b5oTE10K2-348dumxvQ
```

## Step 4: Run SQL Setup Script

1. In your Supabase project, go to **SQL Editor**
2. Click **New Query**
3. Copy and paste the entire contents of `supabase_setup.sql`
4. Click **Run** (or press Ctrl+Enter)
5. You should see "Success. No rows returned" or similar success message

## Step 5: Verify Setup

Run this query in SQL Editor to verify:

```sql
-- Check tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('users', 'persons', 'cameras', 'detections');

-- Check admin user
SELECT id, email, role, created_at 
FROM users 
WHERE email = 'admin@cyber.com';
```

You should see:
- 4 tables created
- 1 admin user with email `admin@cyber.com`

## Step 6: Test Login

1. Start your backend: `python run.py`
2. Go to http://localhost:3000
3. Login with:
   - **Email**: `admin@cyber.com`
   - **Password**: `admin123`

## Troubleshooting

### If login still fails:
1. Check that the password hash in the database matches:
   ```sql
   SELECT email, password FROM users WHERE email = 'admin@cyber.com';
   ```
   Should show: `$2b$12$QSTA2RaUs3CYu4hH3p1/2uH4eTwLFn248bQXfyYsWnCGKaIflXuyq`

2. If the hash is different, delete and recreate the user:
   ```sql
   DELETE FROM users WHERE email = 'admin@cyber.com';
   INSERT INTO users (email, password, role)
   VALUES (
       'admin@cyber.com',
       '$2b$12$QSTA2RaUs3CYu4hH3p1/2uH4eTwLFn248bQXfyYsWnCGKaIflXuyq',
       'admin'
   );
   ```

### If vector extension error:
- Make sure pgvector extension is enabled in Supabase
- The extension is required for face embeddings storage

### If tables already exist:
- The SQL uses `CREATE TABLE IF NOT EXISTS`, so it's safe to run multiple times
- The admin user insert uses `ON CONFLICT`, so it will update if already exists

