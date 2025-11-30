#!/usr/bin/env python3
"""
Setup Chart of Accounts (COA) for Orchid Resort
Creates all required account groups and ledgers for automatic accounting
"""

from app.database import SessionLocal
from app.models.account import AccountGroup, AccountLedger, AccountType
from sqlalchemy import and_

db = SessionLocal()

def get_or_create_group(name: str, account_type: AccountType, description: str = None) -> AccountGroup:
    """Get existing group or create new one"""
    group = db.query(AccountGroup).filter(
        and_(AccountGroup.name == name, AccountGroup.account_type == account_type)
    ).first()
    
    if not group:
        group = AccountGroup(
            name=name,
            account_type=account_type,
            description=description,
            is_active=True
        )
        db.add(group)
        db.flush()
        print(f"✅ Created Account Group: {name}")
    else:
        print(f"ℹ️  Account Group already exists: {name}")
    
    return group

def get_or_create_ledger(
    name: str,
    group: AccountGroup,
    code: str = None,
    module: str = None,
    description: str = None,
    balance_type: str = "debit",
    tax_type: str = None,
    tax_rate: float = None,
    bank_name: str = None
) -> AccountLedger:
    """Get existing ledger or create new one"""
    ledger = db.query(AccountLedger).filter(
        and_(AccountLedger.name == name, AccountLedger.group_id == group.id)
    ).first()
    
    if not ledger:
        ledger = AccountLedger(
            name=name,
            code=code,
            group_id=group.id,
            module=module,
            description=description,
            balance_type=balance_type,
            opening_balance=0.0,
            is_active=True,
            tax_type=tax_type,
            tax_rate=tax_rate,
            bank_name=bank_name
        )
        db.add(ledger)
        db.flush()
        print(f"  ✅ Created Ledger: {name}")
    else:
        print(f"  ℹ️  Ledger already exists: {name}")
    
    return ledger

try:
    print("\n" + "="*60)
    print("SETTING UP CHART OF ACCOUNTS")
    print("="*60 + "\n")
    
    # ============================================
    # 🟢 A. ASSETS (What you Own)
    # ============================================
    print("\n🟢 ASSETS GROUP")
    print("-" * 60)
    
    # Current Assets Group
    current_assets_group = get_or_create_group(
        "Current Assets",
        AccountType.ASSET,
        "Assets that can be converted to cash within one year"
    )
    
    # Current Asset Ledgers
    get_or_create_ledger("Cash in Hand", current_assets_group, "CA001", "Asset", "Front Desk Petty Cash")
    get_or_create_ledger("Bank Account (SBI)", current_assets_group, "CA002", "Asset", "SBI Bank Account", bank_name="SBI")
    get_or_create_ledger("Bank Account (HDFC)", current_assets_group, "CA003", "Asset", "HDFC Bank Account", bank_name="HDFC")
    get_or_create_ledger("Accounts Receivable (Guest)", current_assets_group, "CA004", "Booking", "Money owed by Corporate Guests/OTAs")
    get_or_create_ledger("Inventory Asset (Stock)", current_assets_group, "CA005", "Inventory", "Value of stock in Kitchen/Store")
    
    # Input Tax Credit (ITC) - Assets
    get_or_create_ledger("Input CGST", current_assets_group, "CA006", "Tax", "GST Receivable from Govt (CGST)", tax_type="CGST", tax_rate=0.0)
    get_or_create_ledger("Input SGST", current_assets_group, "CA007", "Tax", "GST Receivable from Govt (SGST)", tax_type="SGST", tax_rate=0.0)
    get_or_create_ledger("Input IGST", current_assets_group, "CA008", "Tax", "GST Receivable from Govt (IGST)", tax_type="IGST", tax_rate=0.0)
    get_or_create_ledger("Input CGST (RCM)", current_assets_group, "CA009", "Tax", "Input CGST under Reverse Charge", tax_type="CGST", tax_rate=0.0)
    get_or_create_ledger("Input SGST (RCM)", current_assets_group, "CA010", "Tax", "Input SGST under Reverse Charge", tax_type="SGST", tax_rate=0.0)
    get_or_create_ledger("Input IGST (RCM)", current_assets_group, "CA011", "Tax", "Input IGST under Reverse Charge", tax_type="IGST", tax_rate=0.0)
    
    # Fixed Assets Group
    fixed_assets_group = get_or_create_group(
        "Fixed Assets",
        AccountType.ASSET,
        "Long-term assets used in business operations"
    )
    
    # Fixed Asset Ledgers
    get_or_create_ledger("Property & Plant", fixed_assets_group, "FA001", "Asset", "Resort Building, Land")
    get_or_create_ledger("Furniture & Fixtures", fixed_assets_group, "FA002", "Asset", "Beds, Sofas, Tables")
    get_or_create_ledger("Equipment", fixed_assets_group, "FA003", "Asset", "ACs, Generators, Kitchen Ovens")
    
    # ============================================
    # 🔴 B. LIABILITIES (What you Owe)
    # ============================================
    print("\n🔴 LIABILITIES GROUP")
    print("-" * 60)
    
    current_liabilities_group = get_or_create_group(
        "Current Liabilities",
        AccountType.LIABILITY,
        "Obligations due within one year"
    )
    
    # Current Liability Ledgers
    get_or_create_ledger("Accounts Payable (Vendor)", current_liabilities_group, "CL001", "Purchase", "Money owed to Vendors", balance_type="credit")
    get_or_create_ledger("Advance Deposits", current_liabilities_group, "CL002", "Booking", "Money received from guests for future stays", balance_type="credit")
    
    # Output Tax (Duties & Taxes Payable)
    get_or_create_ledger("Output CGST", current_liabilities_group, "CL003", "Tax", "GST collected to be paid to Govt (CGST)", balance_type="credit", tax_type="CGST", tax_rate=0.0)
    get_or_create_ledger("Output SGST", current_liabilities_group, "CL004", "Tax", "GST collected to be paid to Govt (SGST)", balance_type="credit", tax_type="SGST", tax_rate=0.0)
    get_or_create_ledger("Output IGST", current_liabilities_group, "CL005", "Tax", "GST collected to be paid to Govt (IGST)", balance_type="credit", tax_type="IGST", tax_rate=0.0)
    
    # RCM Liability
    get_or_create_ledger("Output CGST (RCM Payable)", current_liabilities_group, "CL006", "Tax", "Tax to be paid on Reverse Charge (CGST)", balance_type="credit", tax_type="CGST", tax_rate=0.0)
    get_or_create_ledger("Output SGST (RCM Payable)", current_liabilities_group, "CL007", "Tax", "Tax to be paid on Reverse Charge (SGST)", balance_type="credit", tax_type="SGST", tax_rate=0.0)
    get_or_create_ledger("Output IGST (RCM Payable)", current_liabilities_group, "CL008", "Tax", "Tax to be paid on Reverse Charge (IGST)", balance_type="credit", tax_type="IGST", tax_rate=0.0)
    
    # ============================================
    # 🔵 C. INCOME (Revenue)
    # ============================================
    print("\n🔵 INCOME GROUP")
    print("-" * 60)
    
    # Direct Income Group
    direct_income_group = get_or_create_group(
        "Direct Income (Operating)",
        AccountType.REVENUE,
        "Revenue from primary business operations"
    )
    
    # Direct Income Ledgers
    get_or_create_ledger("Room Revenue (Taxable)", direct_income_group, "DI001", "Booking", "Sales from Stay", balance_type="credit")
    get_or_create_ledger("Food Revenue (Taxable)", direct_income_group, "DI002", "Food", "Sales from Restaurant", balance_type="credit")
    get_or_create_ledger("Service Revenue (Taxable)", direct_income_group, "DI003", "Service", "Laundry, Spa, Events", balance_type="credit")
    get_or_create_ledger("Package Revenue (Taxable)", direct_income_group, "DI004", "Booking", "Package bookings revenue", balance_type="credit")
    
    # Indirect Income Group
    indirect_income_group = get_or_create_group(
        "Indirect Income",
        AccountType.REVENUE,
        "Revenue from non-operating activities"
    )
    
    # Indirect Income Ledgers
    get_or_create_ledger("Interest Income", indirect_income_group, "II001", "Income", "Interest earned on deposits", balance_type="credit")
    get_or_create_ledger("Scrap Sales", indirect_income_group, "II002", "Income", "Revenue from selling scrap/waste", balance_type="credit")
    
    # ============================================
    # 🟠 D. EXPENSES (Costs)
    # ============================================
    print("\n🟠 EXPENSES GROUP")
    print("-" * 60)
    
    # Direct Expenses Group
    direct_expenses_group = get_or_create_group(
        "Direct Expenses (Cost of Sales)",
        AccountType.EXPENSE,
        "Expenses directly related to revenue generation"
    )
    
    # Direct Expense Ledgers
    get_or_create_ledger("Cost of Goods Sold (COGS)", direct_expenses_group, "DE001", "Purchase", "Raw materials consumed in Kitchen")
    get_or_create_ledger("Housekeeping Consumables", direct_expenses_group, "DE002", "Purchase", "Soaps, Shampoos used")
    get_or_create_ledger("Consumables Expense", direct_expenses_group, "DE003", "Purchase", "General consumables expense")
    
    # Indirect Expenses Group
    indirect_expenses_group = get_or_create_group(
        "Indirect Expenses (Overhead)",
        AccountType.EXPENSE,
        "Operating expenses not directly tied to revenue"
    )
    
    # Indirect Expense Ledgers
    get_or_create_ledger("Staff Salaries", indirect_expenses_group, "IE001", "Expense", "Employee salary expenses")
    get_or_create_ledger("Utilities", indirect_expenses_group, "IE002", "Expense", "Electricity, Water, Internet")
    get_or_create_ledger("Repairs & Maintenance", indirect_expenses_group, "IE003", "Expense", "Maintenance and repair costs")
    get_or_create_ledger("Marketing & Ads", indirect_expenses_group, "IE004", "Expense", "Advertising and marketing expenses")
    get_or_create_ledger("General Expense", indirect_expenses_group, "IE005", "Expense", "General operating expenses")
    
    # RCM Expense Ledgers (for different nature of supply)
    get_or_create_ledger("GTA Expense", indirect_expenses_group, "IE006", "Expense", "Goods Transport Agency (RCM)")
    get_or_create_ledger("Legal Services Expense", indirect_expenses_group, "IE007", "Expense", "Legal Services (RCM)")
    get_or_create_ledger("Import of Service Expense", indirect_expenses_group, "IE008", "Expense", "Import of Services (RCM)")
    get_or_create_ledger("Security Services Expense", indirect_expenses_group, "IE009", "Expense", "Security Services (RCM)")
    get_or_create_ledger("Purchase Expense", indirect_expenses_group, "IE010", "Purchase", "General purchase expenses")
    
    # Discount Ledger
    get_or_create_ledger("Discount Allowed", indirect_expenses_group, "IE011", "Expense", "Discounts given to customers")
    
    # Commit all changes
    db.commit()
    
    print("\n" + "="*60)
    print("✅ CHART OF ACCOUNTS SETUP COMPLETE!")
    print("="*60)
    print("\nSummary:")
    print(f"  - Account Groups: {db.query(AccountGroup).filter(AccountGroup.is_active == True).count()}")
    print(f"  - Account Ledgers: {db.query(AccountLedger).filter(AccountLedger.is_active == True).count()}")
    print("\nAll accounts are ready for automatic journal entry creation.")
    print("="*60 + "\n")
    
except Exception as e:
    print(f'\n❌ Error: {e}')
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()

