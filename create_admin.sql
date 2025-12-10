-- Quick SQL to create/update admin user
-- Run this in Supabase SQL Editor

-- First, delete existing admin if any
DELETE FROM users WHERE email = 'admin@cyber.com';

-- Create admin user with correct bcrypt hash for password "admin123"
-- Generated hash that works with bcrypt.checkpw()
INSERT INTO users (email, hashed_password, role)
VALUES (
    'admin@cyber.com',
    '$2b$12$8snmfPTbSjzN33Uf4ZZSkeWKnX/scYP1hXDwXSTP5llR2vUTYJaR2',
    'admin'
);

-- Verify it was created
SELECT id, email, role, 
       substring(hashed_password, 1, 30) as password_hash_preview,
       created_at 
FROM users 
WHERE email = 'admin@cyber.com';

