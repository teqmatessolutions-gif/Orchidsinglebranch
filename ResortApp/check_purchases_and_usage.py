"""
Check all current purchases and usage/transactions
Shows complete inventory flow
"""
from app.database import SessionLocal
from app.models.inventory import (
    PurchaseMaster, PurchaseDetail, InventoryTransaction, 
    InventoryItem, StockIssue, StockIssueDetail, LocationStock
)
from sqlalchemy import func

def check_purchases_and_usage():
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("INVENTORY PURCHASES AND USAGE REPORT")
        print("=" * 80)
        
        # 1. Check Purchases
        print("\n" + "=" * 80)
        print("1. PURCHASES")
        print("=" * 80)
        
        purchases = db.query(PurchaseMaster).all()
        
        if purchases:
            total_purchase_value = 0
            for purchase in purchases:
                print(f"\nPurchase #{purchase.id} - {purchase.purchase_number}")
                print(f"  Date: {purchase.purchase_date}")
                print(f"  Vendor: {purchase.vendor.name if purchase.vendor else 'N/A'}")
                print(f"  Total: ₹{purchase.total_amount}")
                total_purchase_value += purchase.total_amount or 0
                
                # Get details
                details = db.query(PurchaseDetail).filter(
                    PurchaseDetail.purchase_master_id == purchase.id
                ).all()
                
                if details:
                    print(f"  Items:")
                    for detail in details:
                        item = detail.item
                        print(f"    - {item.name}: {detail.quantity} {item.unit} @ ₹{detail.unit_price} = ₹{detail.total_amount}")
            
            print(f"\n  📊 Total Purchases: {len(purchases)}")
            print(f"  💰 Total Purchase Value: ₹{total_purchase_value:.2f}")
        else:
            print("\n  ⚠️  No purchases found!")
        
        # 2. Check Stock Issues (Transfers/Usage)
        print("\n" + "=" * 80)
        print("2. STOCK ISSUES (Transfers/Usage)")
        print("=" * 80)
        
        issues = db.query(StockIssue).all()
        
        if issues:
            for issue in issues:
                print(f"\nIssue #{issue.id} - {issue.issue_number}")
                print(f"  Date: {issue.issue_date}")
                print(f"  From: {issue.source_location.name if issue.source_location else 'N/A'}")
                print(f"  To: {issue.destination_location.name if issue.destination_location else 'N/A'}")
                
                # Get details
                details = db.query(StockIssueDetail).filter(
                    StockIssueDetail.issue_id == issue.id
                ).all()
                
                if details:
                    print(f"  Items:")
                    for detail in details:
                        item = detail.item
                        print(f"    - {item.name}: {detail.issued_quantity} {item.unit}")
            
            print(f"\n  📦 Total Stock Issues: {len(issues)}")
        else:
            print("\n  ⚠️  No stock issues found!")
        
        # 3. Check Inventory Transactions
        print("\n" + "=" * 80)
        print("3. INVENTORY TRANSACTIONS")
        print("=" * 80)
        
        transactions = db.query(InventoryTransaction).order_by(
            InventoryTransaction.created_at.desc()
        ).limit(20).all()
        
        if transactions:
            print("\n  Recent Transactions (last 20):")
            for txn in transactions:
                item = db.query(InventoryItem).filter(InventoryItem.id == txn.item_id).first()
                item_name = item.name if item else f"Item #{txn.item_id}"
                
                sign = "+" if txn.transaction_type in ["in", "transfer_in"] else "-"
                print(f"    {sign} {txn.quantity} {item_name} ({txn.transaction_type})")
                print(f"      Ref: {txn.reference_number}, Date: {txn.created_at}")
            
            # Count by type
            in_count = db.query(func.count(InventoryTransaction.id)).filter(
                InventoryTransaction.transaction_type == "in"
            ).scalar()
            
            out_count = db.query(func.count(InventoryTransaction.id)).filter(
                InventoryTransaction.transaction_type == "out"
            ).scalar()
            
            transfer_in_count = db.query(func.count(InventoryTransaction.id)).filter(
                InventoryTransaction.transaction_type == "transfer_in"
            ).scalar()
            
            transfer_out_count = db.query(func.count(InventoryTransaction.id)).filter(
                InventoryTransaction.transaction_type == "transfer_out"
            ).scalar()
            
            print(f"\n  📊 Transaction Summary:")
            print(f"    IN: {in_count}")
            print(f"    OUT: {out_count}")
            print(f"    Transfer IN: {transfer_in_count}")
            print(f"    Transfer OUT: {transfer_out_count}")
        else:
            print("\n  ⚠️  No transactions found!")
        
        # 4. Check Current Stock Levels
        print("\n" + "=" * 80)
        print("4. CURRENT STOCK LEVELS")
        print("=" * 80)
        
        items = db.query(InventoryItem).all()
        
        if items:
            print("\n  Item Name                    | Global Stock | Total Location Stock")
            print("  " + "-" * 76)
            
            for item in items:
                # Get total location stock
                total_loc_stock = db.query(func.sum(LocationStock.quantity)).filter(
                    LocationStock.item_id == item.id
                ).scalar() or 0
                
                global_stock = item.current_stock or 0
                
                status = "✅" if global_stock == total_loc_stock else "⚠️"
                
                print(f"  {status} {item.name:30} | {global_stock:12.2f} | {total_loc_stock:20.2f}")
        
        # 5. Check Location Stocks
        print("\n" + "=" * 80)
        print("5. LOCATION STOCKS")
        print("=" * 80)
        
        location_stocks = db.query(LocationStock).all()
        
        if location_stocks:
            from collections import defaultdict
            by_location = defaultdict(list)
            
            for ls in location_stocks:
                by_location[ls.location_id].append(ls)
            
            for loc_id, stocks in by_location.items():
                location = stocks[0].location
                loc_name = f"{location.building} - {location.room_area}" if location else f"Location {loc_id}"
                
                print(f"\n  📍 {loc_name}:")
                for stock in stocks:
                    item = stock.item
                    print(f"    - {item.name}: {stock.quantity} {item.unit}")
        else:
            print("\n  ⚠️  No location stocks found!")
        
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"\n  Total Purchases: {len(purchases)}")
        print(f"  Total Stock Issues: {len(issues)}")
        print(f"  Total Transactions: {db.query(func.count(InventoryTransaction.id)).scalar()}")
        print(f"  Total Items: {len(items)}")
        print(f"  Total Location Stocks: {len(location_stocks)}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_purchases_and_usage()
