
import os

file_path = r'c:\releasing\orchid\ResortApp\app\api\checkout.py'

new_content_block = """    if payload.asset_damages:
        from app.models.inventory import AssetRegistry, WasteLog, InventoryTransaction, LocationStock
        from app.curd.inventory import generate_waste_log_number
        
        # Determine room object once
        room_obj = db.query(Room).filter(Room.number == checkout_request.room_number).first()
        
        for asset in payload.asset_damages:
            asset_dict = asset.dict()
            # Asset damage is always charged
            asset_charge = asset.replacement_cost
            total_missing_charges += asset_charge
            
            asset_dict['missing_item_charge'] = asset_charge
            asset_dict['unit_price'] = asset.replacement_cost
            asset_dict['missing_qty'] = 1  # Treat as 1 unit damaged
            asset_dict['is_fixed_asset'] = True
            
            missing_items_details.append({
                "item_name": asset.item_name,
                "item_code": "ASSET",
                "missing_qty": 1,
                "unit_price": asset.replacement_cost,
                "total_charge": asset_charge,
                "is_fixed_asset": True,
                "notes": asset.notes
            })
            
            inventory_data_with_charges.append(asset_dict) 
            
            # Find the Asset Registry Record
            asset_registry_id = getattr(asset, 'asset_registry_id', None)
            item_id = getattr(asset, 'item_id', None)
            
            asset_record = None
            if asset_registry_id:
                asset_record = db.query(AssetRegistry).filter(AssetRegistry.id == asset_registry_id).first()
            elif item_id and room_obj and room_obj.inventory_location_id:
                asset_record = db.query(AssetRegistry).filter(
                    AssetRegistry.item_id == item_id,
                    AssetRegistry.current_location_id == room_obj.inventory_location_id,
                    AssetRegistry.status == "active"
                ).first()
            
            if asset_record:
                # 1. Update Asset Status
                asset_record.status = "damaged"
                asset_record.notes = f"Damaged during checkout. {{asset.notes or ''}}"
                print(f"[CHECKOUT] Updated AssetRegistry ID {{asset_record.id}} status to 'damaged'")
                
                # 2. Create Waste Log
                waste_log_num = generate_waste_log_number(db)
                waste_log = WasteLog(
                    log_number=waste_log_num,
                    item_id=asset_record.item_id,
                    is_food_item=False,
                    location_id=asset_record.current_location_id,
                    quantity=1,
                    unit="pcs",
                    reason_code="Damaged",
                    action_taken="Charged to Guest",
                    notes=f"Damaged asset during checkout - Room {{checkout_request.room_number}}. {{asset.notes or ''}}",
                    reported_by=current_user.id,
                    waste_date=datetime.utcnow()
                )
                db.add(waste_log)
                print(f"[CHECKOUT] Created waste log {{waste_log_num}} for damaged asset")
                
                # 3. Create Damage Transaction
                damage_txn = InventoryTransaction(
                    item_id=asset_record.item_id,
                    transaction_type="waste_spoilage",
                    quantity=1,
                    unit_price=asset_record.item.unit_price if asset_record.item else 0,
                    total_amount=asset.replacement_cost,
                    reference_number=waste_log_num,
                    notes=f"Damaged asset at checkout - Room {{checkout_request.room_number}}",
                    created_by=current_user.id
                )
                db.add(damage_txn)
                print(f"[CHECKOUT] Created damage transaction for asset")
                
                # 4. Deduct LocationStock (The Fix)
                if asset_record.current_location_id:
                    loc_stock = db.query(LocationStock).filter(
                        LocationStock.location_id == asset_record.current_location_id,
                        LocationStock.item_id == asset_record.item_id
                    ).first()
                    if loc_stock and loc_stock.quantity > 0:
                        loc_stock.quantity -= 1
                        loc_stock.last_updated = datetime.utcnow()
                        print(f"[CHECKOUT] Deducted LocationStock for damaged asset: {{loc_stock.quantity + 1}} -> {{loc_stock.quantity}}")
"""

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_index = -1
end_index = -1

for i, line in enumerate(lines):
    if "if payload.asset_damages:" in line:
        start_index = i
    if "if inventory_data_with_charges:" in line and start_index != -1 and i > start_index:
        end_index = i
        break

if start_index != -1 and end_index != -1:
    print(f"Found block: Lines {start_index+1} to {end_index}")
    # Adjust end_index to exclude the 'if inventory...' line itself?
    # Yes, we want to replace up to it.
    
    # We also need to preserve indentation for new_content_block (it is already indented 4 spaces?)
    # The snippet implies 4 spaces.
    
    new_lines = lines[:start_index] + [new_content_block + "\n"] + lines[end_index:]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("Successfully replaced block.")
else:
    print("Could not find start/end markers.")
