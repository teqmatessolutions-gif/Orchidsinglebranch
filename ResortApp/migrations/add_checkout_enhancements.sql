-- Migration script to add enhanced checkout features
-- Run this after updating the models

-- Add advance_deposit to bookings table
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS advance_deposit FLOAT DEFAULT 0.0;

-- Add advance_deposit to package_bookings table
ALTER TABLE package_bookings ADD COLUMN IF NOT EXISTS advance_deposit FLOAT DEFAULT 0.0;

-- Create checkout_verifications table
CREATE TABLE IF NOT EXISTS checkout_verifications (
    id SERIAL PRIMARY KEY,
    checkout_id INTEGER NOT NULL REFERENCES checkouts(id) ON DELETE CASCADE,
    room_number VARCHAR NOT NULL,
    housekeeping_status VARCHAR DEFAULT 'pending',
    housekeeping_notes TEXT,
    housekeeping_approved_by VARCHAR,
    housekeeping_approved_at TIMESTAMP,
    consumables_audit_data JSONB,
    consumables_total_charge FLOAT DEFAULT 0.0,
    asset_damages JSONB,
    asset_damage_total FLOAT DEFAULT 0.0,
    key_card_returned BOOLEAN DEFAULT FALSE,
    key_card_fee FLOAT DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create checkout_payments table for split payments
CREATE TABLE IF NOT EXISTS checkout_payments (
    id SERIAL PRIMARY KEY,
    checkout_id INTEGER NOT NULL REFERENCES checkouts(id) ON DELETE CASCADE,
    payment_method VARCHAR NOT NULL,
    amount FLOAT NOT NULL,
    transaction_id VARCHAR,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add enhanced fields to checkouts table
ALTER TABLE checkouts ADD COLUMN IF NOT EXISTS late_checkout_fee FLOAT DEFAULT 0.0;
ALTER TABLE checkouts ADD COLUMN IF NOT EXISTS consumables_charges FLOAT DEFAULT 0.0;
ALTER TABLE checkouts ADD COLUMN IF NOT EXISTS asset_damage_charges FLOAT DEFAULT 0.0;
ALTER TABLE checkouts ADD COLUMN IF NOT EXISTS key_card_fee FLOAT DEFAULT 0.0;
ALTER TABLE checkouts ADD COLUMN IF NOT EXISTS advance_deposit FLOAT DEFAULT 0.0;
ALTER TABLE checkouts ADD COLUMN IF NOT EXISTS tips_gratuity FLOAT DEFAULT 0.0;
ALTER TABLE checkouts ADD COLUMN IF NOT EXISTS guest_gstin VARCHAR;
ALTER TABLE checkouts ADD COLUMN IF NOT EXISTS is_b2b BOOLEAN DEFAULT FALSE;
ALTER TABLE checkouts ADD COLUMN IF NOT EXISTS invoice_number VARCHAR UNIQUE;
ALTER TABLE checkouts ADD COLUMN IF NOT EXISTS invoice_pdf_path VARCHAR;
ALTER TABLE checkouts ADD COLUMN IF NOT EXISTS gate_pass_path VARCHAR;
ALTER TABLE checkouts ADD COLUMN IF NOT EXISTS feedback_sent BOOLEAN DEFAULT FALSE;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_checkout_verifications_checkout_id ON checkout_verifications(checkout_id);
CREATE INDEX IF NOT EXISTS idx_checkout_payments_checkout_id ON checkout_payments(checkout_id);
CREATE INDEX IF NOT EXISTS idx_checkouts_invoice_number ON checkouts(invoice_number);


