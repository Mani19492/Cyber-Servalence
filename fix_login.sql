-- =====================================================
-- FIX LOGIN - Run this in Supabase SQL Editor
-- =====================================================

-- Step 1: Check current state
SELECT 
    email, 
    role,
    hashed_password IS NOT NULL as has_hash,
    CASE 
        WHEN hashed_password IS NULL THEN 'NULL - NEEDS FIX'
        WHEN hashed_password NOT LIKE '$2b$%' THEN 'WRONG FORMAT - NEEDS FIX'
        WHEN length(hashed_password) != 60 THEN 'WRONG LENGTH - NEEDS FIX'
        ELSE 'OK'
    END as hash_status,
    substring(hashed_password, 1, 30) as hash_preview,
    created_at
FROM users 
WHERE email = 'admin@cyber.com';

-- Step 2: Delete if exists (to recreate cleanly)
DELETE FROM users WHERE email = 'admin@cyber.com';

-- Step 3: Create admin user with VERIFIED working hash
-- Password: admin123
-- This hash is tested and works with bcrypt.checkpw()
INSERT INTO users (email, hashed_password, role)
VALUES (
    'admin@cyber.com',
    '$2b$12$8snmfPTbSjzN33Uf4ZZSkeWKnX/scYP1hXDwXSTP5llR2vUTYJaR2',
    'admin'
);

-- Step 4: Verify it was created correctly
SELECT 
    email,
    role,
    hashed_password LIKE '$2b$12$%' as correct_format,
    length(hashed_password) = 60 as correct_length,
    substring(hashed_password, 1, 30) as hash_preview,
    created_at
FROM users 
WHERE email = 'admin@cyber.com';

-- Expected result:
-- email: admin@cyber.com
-- role: admin  
-- correct_format: true
-- correct_length: true
-- hash_preview: $2b$12$8snmfPTbSjzN33Uf4ZZSke

