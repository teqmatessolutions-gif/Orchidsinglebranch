
import sys
import os
from sqlalchemy import func

# Add root directory to path
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models.inventory import PurchaseMaster, InventoryTransaction, InventoryItem, PurchaseDetail

def verify_accounting():
    db = SessionLocal()
    try:
        print("--- Verifying Ledger Math ---")

        # 1. Calculate Total Purchases (AP)
        # Assuming all purchases are on credit for this matching exercise
        total_purchases = db.query(func.sum(PurchaseMaster.total_amount)).scalar() or 0.0
        # Use cgst, sgst, igst columns as per model
        total_tax = db.query(
            func.sum(PurchaseMaster.cgst) + 
            func.sum(PurchaseMaster.sgst) + 
            func.sum(PurchaseMaster.igst)
        ).scalar() or 0.0
        net_purchase_value = total_purchases - total_tax

        print(f"1. Total Purchases (Accounts Payable): {total_purchases:,.2f}")
        print(f"2. Total Tax (IGST/CGST/SGST):       {total_tax:,.2f}")
        print(f"3. Net Goods Value (Base Purchase):    {net_purchase_value:,.2f}")

        # 2. Calculate Usage (COGS)
        # Look for transactions that reduce stock (Transfer Out, Usage) but NOT just moving between internal locations if strictly tracking value. 
        # However, usually COGS is realized when item leaves 'Asset' locations.
        # Let's sum up transactions tagged as 'Transfer Out' or 'usage' that define COGS.
        # Based on previous context, 'Transfer Out' seems to be the trigger for COGS in this specific user scenario.
        
        # 3. Calculate COGS (Backend matches exact string "out")
        cogs = db.query(func.sum(InventoryTransaction.total_amount))\
            .filter(InventoryTransaction.transaction_type == "out")\
            .scalar() or 0.0

        print(f"4. Cost of Goods Sold (Usage/Issue):   {cogs:,.2f}")

        # NEW: 4.5 Calculate Opening Balance / Adjustments
        # Find Inventory Ledger ID
        from app.models.account import AccountLedger, JournalEntryLine, JournalEntry
        inv_ledger = db.query(AccountLedger).filter(AccountLedger.name == "Inventory Asset (Stock)").first()
        adjustments = 0.0
        if inv_ledger:
            # Sum Debits to Inventory that are NOT from Purchase (Ref type != purchase)
            # Actually, easiest is to just see the Ledger Balance directly?
            # But sticking to formula: Expected = Net Purchase + Adjustments - COGS
            
            # Let's get total debits that are Manual Adjustments
            adjustments = db.query(func.sum(JournalEntryLine.amount))\
                .join(JournalEntryLine.entry)\
                .filter(
                    JournalEntryLine.debit_ledger_id == inv_ledger.id,
                    JournalEntry.reference_type == "manual_adjustment"
                ).scalar() or 0.0
            print(f"4.5 Opening Balance / Adjustments:     {adjustments:,.2f}")

        # 3. Calculate Expected Inventory Asset
        if net_purchase_value: net_purchase_value = float(net_purchase_value)
        if cogs: cogs = float(cogs)
        if adjustments: adjustments = float(adjustments)
        
        expected_inventory = net_purchase_value + adjustments - cogs
        print(f"5. Calculated Ending Inventory:        {expected_inventory:,.2f}")

        # 4. Compare with Actual Ledger Entries (if they exist as strict rows, usually they are calculated on fly or stored)
        # But we can check current stock value sum
        current_stock_value = db.query(func.sum(InventoryItem.current_stock * InventoryItem.unit_price)).scalar() or 0.0
        print(f"6. Actual Current Stock Value (DB):    {current_stock_value:,.2f}")

        # 5. Check Delta
        delta = expected_inventory - current_stock_value
        print(f"--------------------------------------------------")
        if abs(delta) < 1.0:
            print("✅ MATCH: Accounting Equation Matches Stock Value!")
        else:
            print(f"❌ MISMATCH: Difference of {delta:,.2f}")
            print("Possible reasons: Stock update without transaction, price change, or initial stock entry.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify_accounting()
