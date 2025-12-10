# Testing Login - Step by Step

## Step 1: Check if Admin User Exists in Database

Run this SQL in Supabase SQL Editor:

```sql
SELECT id, email, role, 
       hashed_password,
       substring(hashed_password, 1, 30) as hash_preview,
       length(hashed_password) as hash_length,
       created_at 
FROM users 
WHERE email = 'admin@cyber.com';
```

**Expected Result:**
- Should return 1 row
- `hashed_password` should start with `$2b$12$`
- `hash_length` should be 60 characters

## Step 2: Use Debug Endpoint

After restarting your backend, visit:

```
http://localhost:8000/debug/user/admin@cyber.com
```

This will show:
- If user exists
- The password hash stored
- Test password verification result

## Step 3: Recreate Admin User

If the hash is wrong or missing, run this SQL:

```sql
-- Delete existing
DELETE FROM users WHERE email = 'admin@cyber.com';

-- Insert with correct hash
INSERT INTO users (email, hashed_password, role)
VALUES (
    'admin@cyber.com',
    '$2b$12$8snmfPTbSjzN33Uf4ZZSkeWKnX/scYP1hXDwXSTP5llR2vUTYJaR2',
    'admin'
);

-- Verify
SELECT email, substring(hashed_password, 1, 30) as hash, role 
FROM users 
WHERE email = 'admin@cyber.com';
```

## Step 4: Test Password Hash Directly

Run this in Python to verify the hash works:

```python
import bcrypt

hash = '$2b$12$8snmfPTbSjzN33Uf4ZZSkeWKnX/scYP1hXDwXSTP5llR2vUTYJaR2'
password = 'admin123'

result = bcrypt.checkpw(password.encode('utf-8'), hash.encode('utf-8'))
print(f"Password verification: {result}")  # Should be True
```

## Step 5: Check Backend Logs

When you try to login, check the backend console output. It will show:
- If user was found
- The hash retrieved from database
- Password verification result
- Any errors

## Common Issues:

1. **User doesn't exist**: Run the SQL from Step 3
2. **Hash is wrong format**: Make sure it starts with `$2b$12$` and is 60 characters
3. **Hash is NULL**: The SQL insert didn't work, check for errors
4. **Backend not reading from DB**: Check `.env` file has correct Supabase credentials

