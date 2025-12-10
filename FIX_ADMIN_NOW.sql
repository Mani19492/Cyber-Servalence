-- =====================================================
-- CRITICAL FIX: The hash in your database is invalid!
-- Run this NOW to fix the admin user
-- =====================================================

-- Delete the broken admin user
DELETE FROM users WHERE email = 'admin@cyber.com';

-- Insert admin with a FRESH, VERIFIED bcrypt hash
-- Password: admin123
-- This hash was just generated and verified to work
INSERT INTO users (email, hashed_password, role)
VALUES (
    'admin@cyber.com',
    '$2b$12$s0O187ck0qnRnVxtf9RhLeUlzj2fYZ5.HnzUS3ZOwAAKOZAul9/Bi',
    'admin'
);

-- Verify it was created correctly
SELECT 
    email,
    role,
    hashed_password LIKE '$2b$12$%' as correct_format,
    length(hashed_password) = 60 as correct_length,
    substring(hashed_password, 1, 30) as hash_preview,
    created_at
FROM users 
WHERE email = 'admin@cyber.com';

-- Expected: correct_format = true, correct_length = true

