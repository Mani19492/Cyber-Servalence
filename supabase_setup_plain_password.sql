-- =====================================================
-- Cyber Servalence Database Setup for Supabase
-- WITH PLAIN TEXT PASSWORDS (Development/Testing Only!)
-- =====================================================
-- ⚠️ WARNING: This uses plain text passwords!
-- DO NOT use this in production!
-- =====================================================

-- =====================================================
-- 1. CREATE TABLES
-- =====================================================

-- Users table - UPDATED to use 'password' instead of 'hashed_password'
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,  -- Plain text password (NOT SECURE!)
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
-- 2. CREATE ADMIN USER (with plain text password)
-- =====================================================

-- Insert admin user with PLAIN TEXT password (admin123)
INSERT INTO users (email, password, role)
VALUES (
    'admin@cyber.com',
    'admin123',  -- Plain text password
    'admin'
)
ON CONFLICT (email) DO UPDATE
SET 
    password = EXCLUDED.password,
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
SELECT id, email, role, 
       length(password) as password_length,
       created_at 
FROM users 
WHERE email = 'admin@cyber.com';

-- =====================================================
-- DONE! 
-- =====================================================
-- Your database is now set up with plain text passwords.
-- Login credentials:
-- Email: admin@cyber.com
-- Password: admin123
--
-- ⚠️ REMINDER: This is NOT secure for production use!

