-- =====================================================
-- UPDATE EXISTING DATABASE TO USE PLAIN TEXT PASSWORDS
-- =====================================================
-- Run this if you already have tables but want to switch
-- from hashed_password to plain text password
-- =====================================================

-- Step 1: Add 'password' column if it doesn't exist
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS password TEXT;

-- Step 2: If you have hashed_password column, you can drop it (optional)
-- ALTER TABLE users DROP COLUMN IF EXISTS hashed_password;

-- Step 3: Update admin user with plain text password
UPDATE users 
SET password = 'admin123'
WHERE email = 'admin@cyber.com';

-- Step 4: Make password column NOT NULL (after updating existing users)
-- ALTER TABLE users ALTER COLUMN password SET NOT NULL;

-- Step 5: Verify
SELECT email, password, role 
FROM users 
WHERE email = 'admin@cyber.com';

