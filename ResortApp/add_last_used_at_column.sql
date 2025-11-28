-- Migration: Add last_used_at column to assigned_services table
-- This column tracks when a service was last used (marked during checkout)

-- Add the column (nullable, as existing records won't have this value)
ALTER TABLE assigned_services 
ADD COLUMN IF NOT EXISTS last_used_at TIMESTAMP NULL;

-- Add a comment to document the column
COMMENT ON COLUMN assigned_services.last_used_at IS 'Timestamp when service was last used (set during checkout)';

-- Optional: Create an index for faster queries if needed
-- CREATE INDEX IF NOT EXISTS idx_assigned_services_last_used_at ON assigned_services(last_used_at);



