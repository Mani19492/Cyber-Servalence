-- =====================================================
-- Cyber Servalence Database Setup for Supabase
-- =====================================================
-- Run this SQL in your Supabase SQL Editor
-- https://app.supabase.com -> Your Project -> SQL Editor

-- =====================================================
-- 1. CREATE TABLES (Matching your schema)
-- =====================================================

-- Users table for authentication
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'viewer',
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Persons table for storing face embeddings
CREATE TABLE IF NOT EXISTS persons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT,
    metadata JSONB,
    embedding TEXT,  -- Stored as text/JSON string
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_persons_name ON persons(name);

-- Cameras table for managing camera streams
CREATE TABLE IF NOT EXISTS cameras (
    id TEXT PRIMARY KEY,
    rtsp_url TEXT NOT NULL,
    location TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Detections table for logging face recognitions
CREATE TABLE IF NOT EXISTS detections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id UUID REFERENCES persons(id),
    camera_id TEXT REFERENCES cameras(id),
    timestamp TIMESTAMPTZ,
    confidence NUMERIC,
    snapshot_path TEXT,
    raw_metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_detections_person ON detections(person_id);
CREATE INDEX IF NOT EXISTS idx_detections_camera ON detections(camera_id);
CREATE INDEX IF NOT EXISTS idx_detections_timestamp ON detections(timestamp);

-- =====================================================
-- 2. CREATE ADMIN USER
-- =====================================================

-- Insert admin user with hashed password (admin123)
-- The password hash is verified to work with bcrypt.checkpw()
INSERT INTO users (email, hashed_password, role)
VALUES (
    'admin@cyber.com',
    '$2b$12$8snmfPTbSjzN33Uf4ZZSkeWKnX/scYP1hXDwXSTP5llR2vUTYJaR2',
    'admin'
)
ON CONFLICT (email) DO UPDATE
SET 
    hashed_password = EXCLUDED.hashed_password,
    role = EXCLUDED.role;

-- =====================================================
-- 3. VERIFY SETUP
-- =====================================================

-- Check if tables were created
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('users', 'persons', 'cameras', 'detections')
ORDER BY table_name;

-- Check if admin user was created
SELECT id, email, role, created_at 
FROM users 
WHERE email = 'admin@cyber.com';

-- =====================================================
-- DONE! 
-- =====================================================
-- Your database is now set up. You can login with:
-- Email: admin@cyber.com
-- Password: admin123
