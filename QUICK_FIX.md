# QUICK FIX - Login Issue

## The Problem
The password hash in your database is **invalid/corrupted**. The hash stored doesn't work with bcrypt verification.

## Solution: Use Backend API to Create Admin

Since the SQL hashes aren't working, let's use the backend API which will generate a correct hash:

### Step 1: Make sure backend is running

### Step 2: Call the admin init endpoint

Using curl:
```bash
curl -X POST http://localhost:8000/admin/init
```

Or using Python:
```python
import requests
response = requests.post("http://localhost:8000/admin/init")
print(response.json())
```

Or visit in browser:
```
http://localhost:8000/admin/init
```

This will:
1. Check if admin exists
2. If not, create it with a properly hashed password
3. Return the status

### Step 3: Test Login

After calling `/admin/init`, try logging in:
- Email: `admin@cyber.com`
- Password: `admin123`

### Alternative: Manual SQL Fix

If you prefer SQL, delete the existing user and let the backend create it:

```sql
-- Delete broken user
DELETE FROM users WHERE email = 'admin@cyber.com';
```

Then call `POST /admin/init` endpoint.

The backend's `hash_password()` function uses the same bcrypt library that `verify_password()` uses, so they're guaranteed to be compatible!

