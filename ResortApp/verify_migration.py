import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL
database_url = os.getenv("DATABASE_URL")

if not database_url:
    print("ERROR: DATABASE_URL not found in environment variables")
    exit(1)

print(f"Connecting to database...")

try:
    # Connect to database
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    # Check if columns exist
    cursor.execute("""
        SELECT column_name, data_type, column_default
        FROM information_schema.columns
        WHERE table_name = 'stock_issue_details'
        AND column_name IN ('is_payable', 'is_paid')
        ORDER BY column_name;
    """)
    
    columns = cursor.fetchall()
    
    if columns:
        print("\n✓ Migration columns found:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]} (default: {col[2]})")
    else:
        print("\n✗ Migration columns NOT found in stock_issue_details table")
    
    # Also check all columns in the table
    cursor.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'stock_issue_details'
        ORDER BY ordinal_position;
    """)
    
    all_columns = cursor.fetchall()
    print(f"\nAll columns in stock_issue_details table ({len(all_columns)} total):")
    for col in all_columns:
        print(f"  - {col[0]}: {col[1]}")
    
    cursor.close()
    conn.close()
    
    print("\n✓ Verification complete")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    exit(1)
