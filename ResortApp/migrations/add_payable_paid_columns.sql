-- Migration to add is_payable and is_paid columns to stock_issue_details table
-- Run this SQL script in your PostgreSQL database

ALTER TABLE stock_issue_details 
ADD COLUMN IF NOT EXISTS is_payable BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS is_paid BOOLEAN DEFAULT FALSE;

-- Verify the columns were added
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'stock_issue_details' 
AND column_name IN ('is_payable', 'is_paid');
