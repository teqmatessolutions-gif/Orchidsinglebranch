from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
import uuid
from datetime import datetime
from app.utils.auth import get_db, get_current_user
from app.models.user import User
from app.curd import inventory as inventory_crud
from app.schemas.inventory import (
    InventoryCategoryCreate, InventoryCategoryUpdate, InventoryCategoryOut,
    InventoryItemCreate, InventoryItemUpdate, InventoryItemOut,
    VendorCreate, VendorUpdate, VendorOut,
    PurchaseMasterCreate, PurchaseMasterUpdate, PurchaseMasterOut,
    PurchaseDetailOut, InventoryTransactionOut,
    StockRequisitionCreate, StockRequisitionOut, StockRequisitionUpdate,
    StockIssueCreate, StockIssueOut,
    WasteLogCreate, WasteLogOut,
    LocationCreate, LocationOut,
    AssetMappingCreate, AssetMappingOut,
    AssetRegistryCreate, AssetRegistryOut, AssetRegistryUpdate
)

router = APIRouter(prefix="/inventory", tags=["Inventory"])

UPLOAD_DIR = "uploads/inventory_items"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Category Endpoints
@router.post("/categories", response_model=InventoryCategoryOut)
def create_category(
    category: InventoryCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return inventory_crud.create_category(db, category)


@router.get("/categories", response_model=List[InventoryCategoryOut])
def get_categories(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return inventory_crud.get_all_categories(db, skip=skip, limit=limit, active_only=active_only)


@router.put("/categories/{category_id}", response_model=InventoryCategoryOut)
def update_category(
    category_id: int,
    category: InventoryCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated = inventory_crud.update_category(db, category_id, category)
    if not updated:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated


@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if category exists
    category = inventory_crud.get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if category has active items
    from app.models.inventory import InventoryItem
    items_count = db.query(InventoryItem).filter(InventoryItem.category_id == category_id, InventoryItem.is_active == True).count()
    if items_count > 0:
        raise HTTPException(status_code=400, detail="Cannot delete category with active items")
        
    # Soft delete
    category.is_active = False
    db.commit()
    return {"message": "Category deleted successfully"}


# Item Endpoints
@router.post("/items", response_model=InventoryItemOut)
async def create_item(
    name: str = Form(...),
    item_code: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    category_id: int = Form(...),
    sub_category: Optional[str] = Form(None),
    hsn_code: Optional[str] = Form(None),
    unit: str = Form("pcs"),
    initial_stock: float = Form(0.0),
    min_stock_level: float = Form(0.0),
    max_stock_level: Optional[float] = Form(None),
    unit_price: float = Form(0.0),
    selling_price: Optional[float] = Form(None),
    gst_rate: float = Form(0.0),
    location: Optional[str] = Form(None),
    barcode: Optional[str] = Form(None),
    is_perishable: bool = Form(False),
    track_serial_number: bool = Form(False),
    is_sellable_to_guest: bool = Form(False),
    track_laundry_cycle: bool = Form(False),
    is_asset_fixed: bool = Form(False),
    maintenance_schedule_days: Optional[int] = Form(None),
    complimentary_limit: Optional[int] = Form(None),
    ingredient_yield_percentage: Optional[float] = Form(None),
    preferred_vendor_id: Optional[int] = Form(None),
    vendor_item_code: Optional[str] = Form(None),
    lead_time_days: Optional[int] = Form(None),
    is_active: bool = Form(True),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Verify category exists
        category = inventory_crud.get_category_by_id(db, category_id)
        if not category:
            raise HTTPException(status_code=404, detail=f"Category with id {category_id} not found")
        
        # Handle image upload
        image_path = None
        if image and image.filename:
            filename = f"item_{uuid.uuid4().hex}_{image.filename}"
            file_path = os.path.join(UPLOAD_DIR, filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            image_path = f"uploads/inventory_items/{filename}".replace("\\", "/")
        
        # Create item
        from app.models.inventory import InventoryItem, InventoryTransaction
        
        created_item = InventoryItem(
            name=name,
            item_code=item_code,
            description=description,
            category_id=category_id,
            sub_category=sub_category,
            hsn_code=hsn_code,
            unit=unit,
            current_stock=initial_stock if initial_stock > 0 else 0.0,
            min_stock_level=min_stock_level,
            max_stock_level=max_stock_level,
            unit_price=unit_price,
            selling_price=selling_price,
            gst_rate=gst_rate,
            location=location,
            barcode=barcode,
            image_path=image_path,
            is_perishable=is_perishable,
            track_serial_number=track_serial_number,
            is_sellable_to_guest=is_sellable_to_guest,
            track_laundry_cycle=track_laundry_cycle,
            is_asset_fixed=is_asset_fixed,
            maintenance_schedule_days=maintenance_schedule_days,
            complimentary_limit=complimentary_limit,
            ingredient_yield_percentage=ingredient_yield_percentage,
            preferred_vendor_id=preferred_vendor_id,
            vendor_item_code=vendor_item_code,
            lead_time_days=lead_time_days,
            is_active=is_active,
        )
        
        db.add(created_item)
        db.flush()  # Get the ID
        
        # Create transaction record for initial stock if provided
        if initial_stock and initial_stock > 0:
            transaction = InventoryTransaction(
                item_id=created_item.id,
                transaction_type="adjustment",
                quantity=initial_stock,
                unit_price=unit_price,
                total_amount=initial_stock * unit_price,
                notes="Initial stock",
                created_by=current_user.id
            )
            db.add(transaction)
        
        db.commit()
        db.refresh(created_item)
        
        # Convert SQLAlchemy model to dict
        item_dict = {
            key: getattr(created_item, key)
            for key in created_item.__table__.columns.keys()
        }
        item_dict["category_name"] = category.name
        item_dict["department"] = category.parent_department  # Add department from category
        item_dict["is_low_stock"] = created_item.current_stock <= created_item.min_stock_level if created_item.min_stock_level else False
        
        return item_dict
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating item: {str(e)}")


@router.get("/items", response_model=List[InventoryItemOut])
def get_items(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Optimized endpoint with eager loading - no N+1 queries"""
    try:
        items = inventory_crud.get_all_items(db, skip=skip, limit=limit, category_id=category_id, active_only=active_only)
        result = []
        for item in items:
            # Category is already loaded via eager loading (when configured), no extra query needed
            category = getattr(item, "category", None)
            result.append({
                **item.__dict__,
                "category_name": category.name if category else None,
                "department": category.parent_department if category else None,  # Add department from category
                "is_low_stock": item.current_stock <= item.min_stock_level if item.min_stock_level else False,
            })
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching items: {str(e)}")


@router.get("/items/{item_id}", response_model=InventoryItemOut)
def get_item(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = inventory_crud.get_item_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    category = inventory_crud.get_category_by_id(db, item.category_id)
    return {
        **item.__dict__,
        "category_name": category.name if category else None,
        "department": category.parent_department if category else None,  # Add department from category
        "is_low_stock": item.current_stock <= item.min_stock_level
    }


@router.put("/items/{item_id}", response_model=InventoryItemOut)
async def update_item(
    item_id: int,
    name: Optional[str] = Form(None),
    item_code: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    sub_category: Optional[str] = Form(None),
    hsn_code: Optional[str] = Form(None),
    unit: Optional[str] = Form(None),
    min_stock_level: Optional[float] = Form(None),
    max_stock_level: Optional[float] = Form(None),
    unit_price: Optional[float] = Form(None),
    selling_price: Optional[float] = Form(None),
    gst_rate: Optional[float] = Form(None),
    location: Optional[str] = Form(None),
    barcode: Optional[str] = Form(None),
    is_perishable: Optional[bool] = Form(None),
    track_serial_number: Optional[bool] = Form(None),
    is_sellable_to_guest: Optional[bool] = Form(None),
    track_laundry_cycle: Optional[bool] = Form(None),
    is_asset_fixed: Optional[bool] = Form(None),
    maintenance_schedule_days: Optional[int] = Form(None),
    complimentary_limit: Optional[int] = Form(None),
    ingredient_yield_percentage: Optional[float] = Form(None),
    preferred_vendor_id: Optional[int] = Form(None),
    vendor_item_code: Optional[str] = Form(None),
    lead_time_days: Optional[int] = Form(None),
    is_active: Optional[bool] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Handle image upload if provided
        image_path = None
        if image and image.filename:
            filename = f"item_{uuid.uuid4().hex}_{image.filename}"
            file_path = os.path.join(UPLOAD_DIR, filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            image_path = f"uploads/inventory_items/{filename}".replace("\\", "/")
        
        # Construct update data
        update_data = InventoryItemUpdate(
            name=name,
            item_code=item_code,
            description=description,
            category_id=category_id,
            sub_category=sub_category,
            hsn_code=hsn_code,
            unit=unit,
            min_stock_level=min_stock_level,
            max_stock_level=max_stock_level,
            unit_price=unit_price,
            selling_price=selling_price,
            gst_rate=gst_rate,
            location=location,
            barcode=barcode,
            image_path=image_path,
            is_perishable=is_perishable,
            track_serial_number=track_serial_number,
            is_sellable_to_guest=is_sellable_to_guest,
            track_laundry_cycle=track_laundry_cycle,
            is_asset_fixed=is_asset_fixed,
            maintenance_schedule_days=maintenance_schedule_days,
            complimentary_limit=complimentary_limit,
            ingredient_yield_percentage=ingredient_yield_percentage,
            preferred_vendor_id=preferred_vendor_id,
            vendor_item_code=vendor_item_code,
            lead_time_days=lead_time_days,
            is_active=is_active
        )
        
        updated = inventory_crud.update_item(db, item_id, update_data)
        if not updated:
            raise HTTPException(status_code=404, detail="Item not found")
            
        # Get category for response
        category = inventory_crud.get_category_by_id(db, updated.category_id)
        
        return {
            **updated.__dict__,
            "category_name": category.name if category else None,
            "department": category.parent_department if category else None,
            "is_low_stock": updated.current_stock <= updated.min_stock_level if updated.min_stock_level else False
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error updating item: {str(e)}")


@router.delete("/items/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item = inventory_crud.get_item_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Always soft delete
    item.is_active = False
    db.commit()
    return {"message": "Item deleted successfully"}


# Vendor Endpoints
@router.post("/vendors", response_model=VendorOut)
def create_vendor(
    vendor: VendorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return inventory_crud.create_vendor(db, vendor)


@router.get("/vendors", response_model=List[VendorOut])
def get_vendors(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return inventory_crud.get_all_vendors(db, skip=skip, limit=limit, active_only=active_only)


@router.get("/vendors/{vendor_id}", response_model=VendorOut)
def get_vendor(vendor_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    vendor = inventory_crud.get_vendor_by_id(db, vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor


@router.put("/vendors/{vendor_id}", response_model=VendorOut)
def update_vendor(
    vendor_id: int,
    vendor_update: VendorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    vendor = inventory_crud.get_vendor_by_id(db, vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    for field, value in vendor_update.dict(exclude_unset=True).items():
        setattr(vendor, field, value)
    
    db.commit()
    db.refresh(vendor)
    return vendor


# Purchase Master Endpoints
@router.post("/purchases", response_model=PurchaseMasterOut)
def create_purchase(
    purchase: PurchaseMasterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Debug logging to file
    import datetime
    with open("purchase_debug.log", "a") as f:
        f.write(f"\n=== {datetime.datetime.now()} ===\n")
        f.write(f"[DEBUG CREATE_PURCHASE] Received purchase data:\n")
        f.write(f"  Status: {purchase.status}\n")
        f.write(f"  Destination Location ID: {purchase.destination_location_id}\n")
        f.write(f"  Details count: {len(purchase.details)}\n")
    
    print(f"[DEBUG CREATE_PURCHASE] Received purchase data:")
    print(f"  Status: {purchase.status}")
    print(f"  Destination Location ID: {purchase.destination_location_id}")
    print(f"  Details count: {len(purchase.details)}")
    
    created = inventory_crud.create_purchase_master(db, purchase, created_by=current_user.id)
    
    # Auto-update item prices from purchase details if purchase is confirmed/received
    if purchase.status in ["confirmed", "received"]:
        try:
            from app.models.inventory import InventoryItem
            for detail in created.details:
                if detail.item_id and detail.unit_price:
                    item = db.query(InventoryItem).filter(InventoryItem.id == detail.item_id).first()
                    if item:
                        # Update item's unit_price to latest purchase price
                        item.unit_price = detail.unit_price
                        print(f"[AUTO-UPDATE] Updated item {item.name} (ID: {item.id}) unit_price to {detail.unit_price}")
            db.commit()
        except Exception as e:
            import traceback
            print(f"Warning: Could not auto-update item prices: {str(e)}\\n{traceback.format_exc()}")
            # Don't fail the purchase creation
    
    # Update stock and location stock if purchase is received
    with open("purchase_debug.log", "a") as f:
        f.write(f"Checking if status is 'received': purchase.status = '{purchase.status}'\n")
    
    if purchase.status == "received":
        with open("purchase_debug.log", "a") as f:
            f.write(f"ENTERING stock update block for received purchase\n")
        
        try:
            from app.models.inventory import InventoryItem, InventoryTransaction, LocationStock
            
            with open("purchase_debug.log", "a") as f:
                f.write(f"Details count in created object: {len(created.details)}\n")
            
            for detail in created.details:
                with open("purchase_debug.log", "a") as f:
                    f.write(f"Processing detail: item_id={detail.item_id}, qty={detail.quantity}\n")
                
                if not detail.item_id:
                    with open("purchase_debug.log", "a") as f:
                        f.write(f"  Skipping - no item_id\n")
                    continue
                
                item = db.query(InventoryItem).filter(InventoryItem.id == detail.item_id).first()
                if not item:
                    continue
                
                # Weighted average cost
                old_stock = item.current_stock or 0
                old_price = item.unit_price or 0
                old_value = old_stock * old_price
                
                new_stock = detail.quantity
                new_price = detail.unit_price
                new_value = new_stock * new_price
                
                total_stock = old_stock + new_stock
                total_value = old_value + new_value
                
                item.current_stock = total_stock
                if total_stock > 0:
                    item.unit_price = round(total_value / total_stock, 2)
                
                print(f"[CREATE-RECEIVED] {item.name}: Stock {old_stock}→{total_stock}, Cost ₹{old_price}→₹{item.unit_price}")
                
                # Location stock
                print(f"[DEBUG] purchase.destination_location_id = {purchase.destination_location_id}")
                if purchase.destination_location_id:
                    print(f"[DEBUG] Creating/updating location stock for location {purchase.destination_location_id}, item {detail.item_id}")
                    location_stock = db.query(LocationStock).filter(
                        LocationStock.location_id == purchase.destination_location_id,
                        LocationStock.item_id == detail.item_id
                    ).first()
                    
                    if location_stock:
                        print(f"[DEBUG] Updating existing location stock, old qty: {location_stock.quantity}")
                        location_stock.quantity += detail.quantity
                    else:
                        print(f"[DEBUG] Creating new location stock with qty: {detail.quantity}")
                        location_stock = LocationStock(
                            location_id=purchase.destination_location_id,
                            item_id=detail.item_id,
                            quantity=detail.quantity
                        )
                        db.add(location_stock)
                else:
                    print(f"[DEBUG] No destination location specified, skipping location stock")
                
                # Transaction
                transaction = InventoryTransaction(
                    item_id=detail.item_id,
                    transaction_type="in",
                    quantity=detail.quantity,
                    unit_price=detail.unit_price,
                    total_amount=detail.unit_price * detail.quantity,
                    reference_number=created.purchase_number,
                    notes=f"Purchase received: {created.purchase_number}",
                    created_by=current_user.id
                )
                db.add(transaction)
            
            db.commit()
        except Exception as e:
            import traceback
            print(f"Warning: Could not update stock for received purchase: {str(e)}\\n{traceback.format_exc()}")
            db.rollback()
    
    # Automatically create journal entry for purchase (Scenario 1)
    # Only create if purchase is confirmed/received (not draft)
    if purchase.status in ["confirmed", "received"]:
        try:
            from app.utils.accounting_helpers import create_purchase_journal_entry
            from app.models.inventory import Vendor
            from app.api.gst_reports import RESORT_STATE_CODE
            
            vendor = inventory_crud.get_vendor_by_id(db, created.vendor_id)
            vendor_name = (vendor.legal_name or vendor.name) if vendor else "Unknown"
            
            # Determine if inter-state purchase
            is_interstate = False
            if vendor and vendor.gst_number and len(vendor.gst_number) >= 2:
                vendor_state_code = vendor.gst_number[:2]
                is_interstate = vendor_state_code != RESORT_STATE_CODE
            
            # Calculate inventory amount (sub_total) and tax amounts
            inventory_amount = float(created.sub_total or 0)
            cgst_amount = float(created.cgst or 0)
            sgst_amount = float(created.sgst or 0)
            igst_amount = float(created.igst or 0)
            
            # Create journal entry
            create_purchase_journal_entry(
                db=db,
                purchase_id=created.id,
                vendor_id=created.vendor_id,
                inventory_amount=inventory_amount,
                cgst_amount=cgst_amount,
                sgst_amount=sgst_amount,
                igst_amount=igst_amount,
                vendor_name=vendor_name,
                is_interstate=is_interstate,
                created_by=current_user.id
            )
        except Exception as e:
            # Log error but don't fail purchase creation
            import traceback
            print(f"Warning: Could not create journal entry for purchase {created.id}: {str(e)}\\n{traceback.format_exc()}")
    
    # Optimized: Batch load items to avoid N+1 queries
    from sqlalchemy.orm import joinedload
    db.refresh(created, ["details"])
    detail_item_ids = [d.item_id for d in created.details if d.item_id]
    items_map = {}
    if detail_item_ids:
        from app.models.inventory import InventoryItem
        items = db.query(InventoryItem).filter(InventoryItem.id.in_(detail_item_ids)).all()
        items_map = {item.id: item for item in items}
    
    # Load vendor
    vendor = inventory_crud.get_vendor_by_id(db, created.vendor_id)
    
    # Build details with item names from map
    details = []
    for detail in created.details:
        item = items_map.get(detail.item_id) if detail.item_id else None
        details.append({
            **detail.__dict__,
            "item_name": item.name if item else None
        })
    
    return {
        **created.__dict__,
        "vendor_name": vendor.name if vendor else None,
        "vendor_gst": vendor.gst_number if vendor else None,
        "created_by_name": current_user.name if current_user else None,
        "details": details
    }


@router.get("/purchases", response_model=List[PurchaseMasterOut])
def get_purchases(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Optimized with eager loading - no N+1 queries"""
    purchases = inventory_crud.get_all_purchases(db, skip=skip, limit=limit, status=status)
    result = []
    for purchase in purchases:
        # Vendor and details.items already loaded via eager loading
        vendor = purchase.vendor
        details = []
        for detail in purchase.details:
            item = detail.item  # Already loaded
            details.append({
                **detail.__dict__,
                "item_name": item.name if item else None
            })
        # Get user separately (not in relationship, but only once per purchase)
        user = db.query(User).filter(User.id == purchase.created_by).first()
        # Get destination location if set
        location_name = None
        if purchase.destination_location_id:
            from app.models.inventory import Location
            location = db.query(Location).filter(Location.id == purchase.destination_location_id).first()
            if location:
                location_name = location.name or f"{location.building} - {location.room_area}"
        result.append({
            **purchase.__dict__,
            "vendor_name": vendor.name if vendor else None,
            "vendor_gst": vendor.gst_number if vendor else None,
            "created_by_name": user.name if user else None,
            "destination_location_name": location_name,
            "details": details
        })
    return result


@router.get("/purchases/{purchase_id}", response_model=PurchaseMasterOut)
def get_purchase(purchase_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    purchase = inventory_crud.get_purchase_by_id(db, purchase_id)
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    
    # Optimized: Batch load to avoid N+1 queries
    vendor = inventory_crud.get_vendor_by_id(db, purchase.vendor_id)
    user = db.query(User).filter(User.id == purchase.created_by).first()
    
    # Batch load items
    detail_item_ids = [d.item_id for d in purchase.details if d.item_id]
    items_map = {}
    if detail_item_ids:
        from app.models.inventory import InventoryItem
        items = db.query(InventoryItem).filter(InventoryItem.id.in_(detail_item_ids)).all()
        items_map = {item.id: item for item in items}
    
    details = []
    for detail in purchase.details:
        item = items_map.get(detail.item_id) if detail.item_id else None
        details.append({
            **detail.__dict__,
            "item_name": item.name if item else None
        })
    
    # Get destination location name
    location_name = None
    if purchase.destination_location_id:
        from app.models.inventory import Location
        location = db.query(Location).filter(Location.id == purchase.destination_location_id).first()
        if location:
            location_name = location.name or f"{location.building} - {location.room_area}"
    
    return {
        **purchase.__dict__,
        "vendor_name": vendor.name if vendor else None,
        "vendor_gst": vendor.gst_number if vendor else None,
        "created_by_name": user.name if user else None,
        "destination_location_name": location_name,
        "details": details
    }


@router.put("/purchases/{purchase_id}", response_model=PurchaseMasterOut)
def update_purchase(
    purchase_id: int,
    purchase_update: PurchaseMasterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models.inventory import InventoryItem, InventoryTransaction, LocationStock
    
    purchase = inventory_crud.get_purchase_by_id(db, purchase_id)
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    
    old_status = purchase.status
    new_status = purchase_update.status if hasattr(purchase_update, 'status') else old_status
    
    updated = inventory_crud.update_purchase_master(db, purchase_id, purchase_update)
    if not updated:
        raise HTTPException(status_code=400, detail="Cannot update purchase")
    
    # CASE 1: Purchase RECEIVED
    if new_status == "received" and old_status != "received":
        for detail in updated.details:
            if not detail.item_id:
                continue
            
            item = db.query(InventoryItem).filter(InventoryItem.id == detail.item_id).first()
            if not item:
                continue
            
            # Weighted average cost
            old_stock = item.current_stock or 0
            old_price = item.unit_price or 0
            old_value = old_stock * old_price
            
            new_stock = detail.quantity
            new_price = detail.unit_price
            new_value = new_stock * new_price
            
            total_stock = old_stock + new_stock
            total_value = old_value + new_value
            
            item.current_stock = total_stock
            if total_stock > 0:
                item.unit_price = round(total_value / total_stock, 2)
            
            print(f"[RECEIVED] {item.name}: Stock {old_stock}→{total_stock}, Cost ₹{old_price}→₹{item.unit_price}")
            
            # Location stock
            if updated.destination_location_id:
                location_stock = db.query(LocationStock).filter(
                    LocationStock.location_id == updated.destination_location_id,
                    LocationStock.item_id == detail.item_id
                ).first()
                
                if location_stock:
                    location_stock.quantity += detail.quantity
                else:
                    location_stock = LocationStock(
                        location_id=updated.destination_location_id,
                        item_id=detail.item_id,
                        quantity=detail.quantity
                    )
                    db.add(location_stock)
            
            # Transaction
            transaction = InventoryTransaction(
                item_id=detail.item_id,
                transaction_type="in",
                quantity=detail.quantity,
                unit_price=detail.unit_price,
                total_amount=detail.unit_price * detail.quantity,
                reference_number=updated.purchase_number,
                notes=f"Purchase received: {updated.purchase_number}",
                created_by=current_user.id
            )
            db.add(transaction)
    
    # CASE 2: Purchase CANCELLED
    elif new_status == "cancelled" and old_status == "received":
        for detail in updated.details:
            if not detail.item_id:
                continue
            
            item = db.query(InventoryItem).filter(InventoryItem.id == detail.item_id).first()
            if not item:
                continue
            
            old_stock = item.current_stock
            new_stock = max(0, old_stock - detail.quantity)
            
            old_value = old_stock * item.unit_price
            cancelled_value = detail.quantity * detail.unit_price
            remaining_value = old_value - cancelled_value
            
            item.current_stock = new_stock
            if new_stock > 0:
                item.unit_price = round(remaining_value / new_stock, 2)
            
            print(f"[CANCELLED] {item.name}: Stock {old_stock}→{new_stock}")
            
            if updated.destination_location_id:
                location_stock = db.query(LocationStock).filter(
                    LocationStock.location_id == updated.destination_location_id,
                    LocationStock.item_id == detail.item_id
                ).first()
                
                if location_stock:
                    location_stock.quantity -= detail.quantity
                    if location_stock.quantity <= 0:
                        db.delete(location_stock)
            
            transaction = InventoryTransaction(
                item_id=detail.item_id,
                transaction_type="out",
                quantity=detail.quantity,
                unit_price=detail.unit_price,
                total_amount=detail.unit_price * detail.quantity,
                reference_number=updated.purchase_number,
                notes=f"Purchase cancelled: {updated.purchase_number}",
                created_by=current_user.id
            )
            db.add(transaction)
    
    db.commit()
    return get_purchase(purchase_id, db, current_user)


@router.delete("/purchases/{purchase_id}")
def delete_purchase(
    purchase_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    purchase = inventory_crud.get_purchase_by_id(db, purchase_id)
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    
    # Only allow deleting draft purchases
    if purchase.status not in ["draft", "cancelled"]:
        raise HTTPException(status_code=400, detail="Cannot delete purchase that is not draft or cancelled")
    
    # Delete details first
    from app.models.inventory import PurchaseDetail
    db.query(PurchaseDetail).filter(PurchaseDetail.purchase_master_id == purchase_id).delete()
    
    db.delete(purchase)
    db.commit()
    return {"message": "Purchase deleted successfully"}


@router.post("/purchases/{purchase_id}/payments")
def create_purchase_payment(
    purchase_id: int,
    payment_data: dict,  # {amount: float, payment_method: str, notes: str}
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record a payment for a purchase (Vendor Payment)"""
    purchase = inventory_crud.get_purchase_by_id(db, purchase_id)
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    
    try:
        amount = float(payment_data.get("amount", 0))
        if amount <= 0:
            raise HTTPException(status_code=400, detail="Invalid amount")
            
        payment_method = payment_data.get("payment_method", "Bank Transfer")
        notes = payment_data.get("notes", "")
        
        # Create Journal Entry
        # Debit: Accounts Payable (Vendor)
        # Credit: Bank/Cash
        
        from app.utils.accounting_helpers import find_ledger_by_name, create_journal_entry
        from app.schemas.account import JournalEntryCreate, JournalEntryLineCreateInEntry
        
        vendor_payable = find_ledger_by_name(db, "Accounts Payable (Vendor)", "Purchase")
        
        # Determine credit ledger
        if payment_method.lower() in ["cash"]:
            credit_ledger = find_ledger_by_name(db, "Cash in Hand", "Asset")
        else:
            credit_ledger = find_ledger_by_name(db, "Bank Account (HDFC)", "Asset") or find_ledger_by_name(db, "Bank Account", "Asset")
            
        if not all([vendor_payable, credit_ledger]):
             raise HTTPException(status_code=400, detail="Required ledgers not found in Chart of Accounts")
             
        lines = [
            JournalEntryLineCreateInEntry(
                debit_ledger_id=vendor_payable.id,
                credit_ledger_id=None,
                amount=amount,
                description=f"Payment for Purchase #{purchase.purchase_number}"
            ),
            JournalEntryLineCreateInEntry(
                debit_ledger_id=None,
                credit_ledger_id=credit_ledger.id,
                amount=amount,
                description=f"Payment to {purchase.vendor.name if purchase.vendor else 'Vendor'}"
            )
        ]
        
        entry = JournalEntryCreate(
            entry_date=datetime.utcnow(),
            reference_type="purchase_payment",
            reference_id=purchase.id,
            description=f"Vendor Payment - {purchase.purchase_number}",
            notes=f"Method: {payment_method}. {notes}",
            lines=lines
        )
        
        journal_entry = create_journal_entry(db, entry, current_user.id)
        
        # Update purchase payment status
        # This is a simplified logic; ideally we sum up all payments
        if amount >= float(purchase.total_amount):
            purchase.payment_status = "paid"
        else:
            purchase.payment_status = "partial"
            
        db.commit()
        
        return {"message": "Payment recorded successfully", "journal_entry_id": journal_entry.id, "payment_status": purchase.payment_status}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error recording payment: {str(e)}")


@router.patch("/purchases/{purchase_id}/status")
def update_purchase_status(
    purchase_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    purchase = inventory_crud.update_purchase_status(db, purchase_id, status)
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
        
    # Auto-update item prices if status is confirmed/received
    if purchase.status in ["confirmed", "received"]:
        try:
            from app.models.inventory import InventoryItem
            for detail in purchase.details:
                if detail.item_id and detail.unit_price:
                    item = db.query(InventoryItem).filter(InventoryItem.id == detail.item_id).first()
                    if item:
                        item.unit_price = detail.unit_price
                        print(f"[AUTO-UPDATE] Updated item {item.name} (ID: {item.id}) unit_price to {detail.unit_price}")
            db.commit()
        except Exception as e:
            print(f"Warning: Could not auto-update item prices: {str(e)}")
            
    return {"message": "Purchase status updated successfully", "status": purchase.status}


@router.patch("/purchases/{purchase_id}/payment-status")
def update_purchase_payment_status(
    purchase_id: int,
    payment_status: str,
    payment_method: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update payment status and payment method for a purchase order"""
    purchase = inventory_crud.get_purchase_by_id(db, purchase_id)
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    
    # Validate payment status
    valid_statuses = ["pending", "partial", "paid"]
    if payment_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid payment status. Must be one of: {', '.join(valid_statuses)}")
    
    # Update payment status
    purchase.payment_status = payment_status
    
    # Update payment method if provided
    if payment_method:
        purchase.payment_method = payment_method
    
    db.commit()
    db.refresh(purchase)
    
    return {
        "message": "Payment status updated successfully",
        "payment_status": purchase.payment_status,
        "payment_method": purchase.payment_method
    }


# Transaction Endpoints
@router.get("/transactions", response_model=List[InventoryTransactionOut])
def get_transactions(
    skip: int = 0,
    limit: int = 100,
    item_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Optimized with eager loading - no N+1 queries"""
    from app.models.inventory import InventoryTransaction, StockIssue
    from sqlalchemy.orm import joinedload
    query = db.query(InventoryTransaction).options(
        joinedload(InventoryTransaction.item),
        joinedload(InventoryTransaction.user)
    )
    if item_id:
        query = query.filter(InventoryTransaction.item_id == item_id)
    transactions = query.order_by(InventoryTransaction.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for trans in transactions:
        # Get destination location if this is a stock issue
        destination_location_name = None
        if trans.reference_number and trans.reference_number.startswith("ISS-"):
            # Try to find the stock issue and get destination location
            issue = db.query(StockIssue).filter(StockIssue.issue_number == trans.reference_number).first()
            if issue and issue.destination_location_id:
                dest_loc = inventory_crud.get_location_by_id(db, issue.destination_location_id)
                if dest_loc:
                    destination_location_name = f"{dest_loc.building} - {dest_loc.room_area}" if (dest_loc.building or dest_loc.room_area) else dest_loc.name or f"Location {dest_loc.id}"
        
        # Relationships already loaded, no extra queries
        result.append({
            **trans.__dict__,
            "item_name": trans.item.name if trans.item else None,
            "created_by_name": trans.user.name if trans.user else None,
            "destination_location_name": destination_location_name
        })
    return result


# Stock Requisition Endpoints
@router.post("/requisitions", response_model=StockRequisitionOut)
def create_requisition(
    requisition: StockRequisitionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        requisition_data = requisition.model_dump()
        created = inventory_crud.create_stock_requisition(db, requisition_data, created_by=current_user.id)
        
        # Load relationships for response
        requester = db.query(User).filter(User.id == created.requested_by).first()
        details = []
        for detail in created.details:
            item = inventory_crud.get_item_by_id(db, detail.item_id)
            details.append({
                **detail.__dict__,
                "item_name": item.name if item else None
            })
        
        return {
            **created.__dict__,
            "requested_by_name": requester.name if requester else None,
            "details": details
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating requisition: {str(e)}")


@router.get("/requisitions", response_model=List[StockRequisitionOut])
def get_requisitions(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Optimized with eager loading - no N+1 queries"""
    requisitions = inventory_crud.get_all_requisitions(db, skip=skip, limit=limit, status=status)
    result = []
    for req in requisitions:
        # Items already loaded via eager loading
        requester = db.query(User).filter(User.id == req.requested_by).first()
        approver = db.query(User).filter(User.id == req.approved_by).first() if req.approved_by else None
        details = []
        for detail in req.details:
            item = detail.item  # Already loaded
            details.append({
                **detail.__dict__,
                "item_name": item.name if item else None,
                "current_stock": item.current_stock if item else None
            })
        result.append({
            **req.__dict__,
            "requested_by_name": requester.name if requester else None,
            "approved_by_name": approver.name if approver else None,
            "details": details
        })
    return result


@router.patch("/requisitions/{requisition_id}/status")
def update_requisition_status(
    requisition_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    requisition = inventory_crud.update_requisition_status(db, requisition_id, status, approved_by=current_user.id)
    if not requisition:
        raise HTTPException(status_code=404, detail="Requisition not found")
    return {"message": "Requisition status updated successfully", "status": requisition.status}


@router.put("/requisitions/{requisition_id}/approve-quantities")
def approve_requisition_quantities(
    requisition_id: int,
    approved_quantities: dict,  # {detail_id: approved_quantity}
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update approved quantities for requisition details"""
    from app.models.inventory import StockRequisitionDetail
    for detail_id, approved_qty in approved_quantities.items():
        detail = db.query(StockRequisitionDetail).filter(StockRequisitionDetail.id == detail_id).first()
        if detail and detail.requisition_id == requisition_id:
            detail.approved_quantity = approved_qty
    db.commit()
    return {"message": "Approved quantities updated successfully"}


# Stock Issue Endpoints
@router.post("/issues", response_model=StockIssueOut)
def create_issue(
    issue: StockIssueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        issue_data = issue.model_dump()
        created = inventory_crud.create_stock_issue(db, issue_data, issued_by=current_user.id)
        
        # Optimized: Batch load to avoid N+1 queries
        issuer = db.query(User).filter(User.id == created.issued_by).first()
        source_loc = inventory_crud.get_location_by_id(db, created.source_location_id) if created.source_location_id else None
        dest_loc = inventory_crud.get_location_by_id(db, created.destination_location_id) if created.destination_location_id else None
        
        # Batch load items
        detail_item_ids = [d.item_id for d in created.details if d.item_id]
        items_map = {}
        if detail_item_ids:
            from app.models.inventory import InventoryItem
            items = db.query(InventoryItem).filter(InventoryItem.id.in_(detail_item_ids)).all()
            items_map = {item.id: item for item in items}
        
        details = []
        for detail in created.details:
            item = items_map.get(detail.item_id) if detail.item_id else None
            details.append({
                **detail.__dict__,
                "item_name": item.name if item else None
            })
        
        return {
            **created.__dict__,
            "issued_by_name": issuer.name if issuer else None,
            "source_location_name": f"{source_loc.building} - {source_loc.room_area}" if source_loc else None,
            "destination_location_name": f"{dest_loc.building} - {dest_loc.room_area}" if dest_loc else None,
            "details": details
        }
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating issue: {str(e)}")


@router.get("/issues", response_model=List[StockIssueOut])
def get_issues(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Optimized with eager loading - no N+1 queries"""
    issues = inventory_crud.get_all_issues(db, skip=skip, limit=limit)
    result = []
    for issue in issues:
        # Locations and items already loaded via eager loading
        issuer = db.query(User).filter(User.id == issue.issued_by).first()
        source_loc = issue.source_location  # Already loaded
        dest_loc = issue.destination_location  # Already loaded
        details = []
        for detail in issue.details:
            item = detail.item  # Already loaded
            # Parse payment status from notes
            is_paid = detail.notes and "PAID" in detail.notes.upper() if detail.notes else False
            details.append({
                **detail.__dict__,
                "item_name": item.name if item else None,
                "is_paid": is_paid
            })
        result.append({
            **issue.__dict__,
            "issued_by_name": issuer.name if issuer else None,
            "source_location_name": f"{source_loc.building} - {source_loc.room_area}" if source_loc else None,
            "destination_location_name": f"{dest_loc.building} - {dest_loc.room_area}" if dest_loc else None,
            "details": details
        })
    return result


@router.patch("/issues/{issue_id}/details/{detail_id}")
def update_issue_detail(
    issue_id: int,
    detail_id: int,
    is_payable: Optional[bool] = None,
    is_paid: Optional[bool] = None,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update issue detail payable/paid status"""
    from app.models.inventory import StockIssueDetail
    
    detail = db.query(StockIssueDetail).filter(
        StockIssueDetail.id == detail_id,
        StockIssueDetail.issue_id == issue_id
    ).first()
    
    if not detail:
        raise HTTPException(status_code=404, detail="Issue detail not found")
    
    # Update notes to reflect payable and paid status
    current_notes = detail.notes or ""
    
    # Parse existing notes to preserve other information
    note_parts = []
    if notes:
        note_parts.append(notes)
    elif current_notes and "PAID" not in current_notes.upper() and "UNPAID" not in current_notes.upper():
        note_parts.append(current_notes)
    
    # Update payable status
    if is_payable is not None:
        if is_payable:
            if "Payable item" not in current_notes:
                note_parts.append("Payable item")
            if "Complimentary item" in current_notes:
                current_notes = current_notes.replace("Complimentary item", "").strip()
        else:
            if "Complimentary item" not in current_notes:
                note_parts.append("Complimentary item")
            if "Payable item" in current_notes:
                current_notes = current_notes.replace("Payable item", "").strip()
    
    # Update paid status
    if is_paid is not None:
        # Remove existing PAID/UNPAID markers
        current_notes = current_notes.replace(" - PAID", "").replace(" - UNPAID", "").replace("PAID", "").replace("UNPAID", "").strip()
        if is_paid:
            note_parts.append("PAID")
        else:
            note_parts.append("UNPAID")
    
    # Combine notes
    detail.notes = " - ".join([p for p in note_parts if p.strip()])
    
    db.commit()
    db.refresh(detail)
    
    return {
        "id": detail.id,
        "item_id": detail.item_id,
        "notes": detail.notes,
        "is_payable": "Payable item" in detail.notes if detail.notes else False,
        "is_paid": "PAID" in detail.notes.upper() if detail.notes else False
    }


# Waste Log Endpoints
@router.post("/waste-logs", response_model=WasteLogOut)
def create_waste_log(
    item_id: Optional[str] = Form(None),
    food_item_id: Optional[str] = Form(None),
    is_food_item: Optional[str] = Form(None),
    location_id: Optional[str] = Form(None),
    batch_number: Optional[str] = Form(None),
    expiry_date: Optional[str] = Form(None),
    quantity: str = Form(...),
    unit: str = Form(...),
    reason_code: str = Form(...),
    action_taken: Optional[str] = Form(None),
    waste_date: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        from datetime import datetime as dt
        
        # Manual conversion
        parsed_item_id = int(item_id) if item_id and item_id.strip() else None
        parsed_food_item_id = int(food_item_id) if food_item_id and food_item_id.strip() else None
        parsed_location_id = int(location_id) if location_id and location_id.strip() else None
        parsed_quantity = float(quantity)
        parsed_is_food = is_food_item in ["true", "True", "1", "on"] if is_food_item else False

        waste_data = {
            "item_id": parsed_item_id,
            "food_item_id": parsed_food_item_id,
            "is_food_item": parsed_is_food,
            "location_id": parsed_location_id,
            "batch_number": batch_number,
            "expiry_date": dt.strptime(expiry_date, "%Y-%m-%d").date() if expiry_date else None,
            "quantity": parsed_quantity,
            "unit": unit,
            "reason_code": reason_code,
            "action_taken": action_taken if action_taken else None,
            "waste_date": dt.strptime(waste_date, "%Y-%m-%d") if waste_date else dt.now(),
            "notes": notes,
        }
        
        # Handle photo upload
        if photo and photo.filename:
            WASTE_UPLOAD_DIR = "uploads/waste_logs"
            os.makedirs(WASTE_UPLOAD_DIR, exist_ok=True)
            filename = f"waste_{uuid.uuid4().hex}_{photo.filename}"
            file_path = os.path.join(WASTE_UPLOAD_DIR, filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(photo.file, buffer)
            waste_data["photo_path"] = f"uploads/waste_logs/{filename}".replace("\\", "/")
        
        created = inventory_crud.create_waste_log(db, waste_data, reported_by=current_user.id)
        
        # Load relationships for response
        reporter = db.query(User).filter(User.id == created.reported_by).first()
        item = inventory_crud.get_item_by_id(db, created.item_id)
        location = inventory_crud.get_location_by_id(db, created.location_id) if created.location_id else None
        
        return {
            **created.__dict__,
            "reported_by_name": reporter.name if reporter else None,
            "item_name": item.name if item else None,
            "location_name": f"{location.building} - {location.room_area}" if location else None
        }
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating waste log: {str(e)}")


@router.get("/waste-logs", response_model=List[WasteLogOut])
def get_waste_logs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Optimized with eager loading"""
    from app.models.inventory import WasteLog
    from sqlalchemy.orm import joinedload
    waste_logs = db.query(WasteLog).options(
        joinedload(WasteLog.item),
        joinedload(WasteLog.location)
    ).order_by(WasteLog.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for log in waste_logs:
        reporter = db.query(User).filter(User.id == log.reported_by).first()
        item = log.item  # Already loaded
        location = log.location  # Already loaded
        result.append({
            **log.__dict__,
            "reported_by_name": reporter.name if reporter else None,
            "item_name": item.name if item else None,
            "location_name": f"{location.building} - {location.room_area}" if location else None
        })
    return result


# Location Endpoints
@router.post("/locations", response_model=LocationOut)
def create_location(
    location: LocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    location_data = location.model_dump()
    created = inventory_crud.create_location(db, location_data)
    return created


@router.get("/locations", response_model=List[LocationOut])
def get_locations(
    skip: int = 0,
    limit: int = 10000,  # Increased limit to show all rooms
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Auto-sync rooms to locations
    from app.models.room import Room
    from app.models.inventory import Location
    from sqlalchemy import or_
    
    # Optimized: Only sync if there are unsynced rooms (performance optimization)
    unsynced_count = db.query(Room).filter(Room.inventory_location_id == None).count()
    
    if unsynced_count > 0:
        # Auto-sync rooms to locations (batch operation for better performance)
        try:
            rooms_to_sync = db.query(Room).filter(Room.inventory_location_id == None).all()
            
            for room in rooms_to_sync:
                try:
                    # Check if location already exists for this room
                    existing_location = db.query(Location).filter(
                        or_(
                            Location.name == f"Room {room.number}",
                            Location.room_area == f"Room {room.number}"
                        ),
                        Location.location_type == "GUEST_ROOM"
                    ).first()
                    
                    if not existing_location:
                        # Create new location for room
                        location_data = {
                            "name": f"Room {room.number}",
                            "building": "Main Building",
                            "floor": None,
                            "room_area": f"Room {room.number}",
                            "location_type": "GUEST_ROOM",
                            "is_inventory_point": False,
                            "description": f"Guest room {room.number} - {room.type or 'Standard'}",
                            "is_active": (room.status != "Deleted" if room.status else True)
                        }
                        location = inventory_crud.create_location(db, location_data)
                        room.inventory_location_id = location.id
                        db.commit()
                    else:
                        # Link room to existing location
                        room.inventory_location_id = existing_location.id
                        db.commit()
                except Exception as e:
                    # Skip this room and continue
                    db.rollback()
                    print(f"Warning: Could not sync room {room.number}: {str(e)}")
                    continue
        except Exception as e:
            # If sync fails completely, just log and continue
            print(f"Warning: Room sync skipped: {str(e)}")
            try:
                db.rollback()
            except:
                pass
    
    # Now fetch all locations (optimized with eager loading)
    from sqlalchemy.orm import joinedload
    locations = db.query(Location).options(
        joinedload(Location.parent_location)
    ).filter(Location.is_active == True).offset(skip).limit(limit).all()
    
    result = []
    for loc in locations:
        parent = loc.parent_location  # Already loaded via eager loading
        result.append({
            **loc.__dict__,
            "parent_location_name": f"{parent.building} - {parent.room_area}" if parent else None
        })
    return result


@router.get("/locations/{location_id}/items")
def get_location_items(
    location_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all inventory items and their stock levels for a specific location"""
    from app.models.inventory import InventoryItem, AssetMapping, AssetRegistry, StockIssueDetail, StockIssue, LocationStock
    from sqlalchemy import func
    
    location = inventory_crud.get_location_by_id(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # 1. Get items from LocationStock (Primary Source for bulk items)
    location_stocks = db.query(LocationStock).filter(
        LocationStock.location_id == location_id
    ).all()
    
    # 2. Get items assigned to this location via asset mappings
    asset_mappings = db.query(AssetMapping).filter(
        AssetMapping.location_id == location_id,
        AssetMapping.is_active == True
    ).all()
    
    # 3. Get items from asset registry
    asset_registry = db.query(AssetRegistry).filter(
        AssetRegistry.current_location_id == location_id
    ).all()
    
    # Combine all items
    items_dict = {}
    
    # Add items from LocationStock
    for stock in location_stocks:
        item = stock.item
        if item:
            key = f"stock_{item.id}"
            category = inventory_crud.get_category_by_id(db, item.category_id)
            items_dict[key] = {
                "item_id": item.id,
                "item_name": item.name,
                "item_code": item.item_code,
                "category_name": category.name if category else None,
                "unit": item.unit,
                "current_stock": stock.quantity, # Location specific stock
                "location_stock": stock.quantity, # Alias for frontend
                "min_stock_level": item.min_stock_level,
                "unit_price": item.unit_price,
                "total_value": stock.quantity * (item.unit_price or 0),
                "source": "Stock",
                "last_updated": stock.last_updated
            }

    # Add items from asset mappings
    for mapping in asset_mappings:
        item = inventory_crud.get_item_by_id(db, mapping.item_id)
        if item:
            key = f"asset_{item.id}"
            if key not in items_dict:
                category = inventory_crud.get_category_by_id(db, item.category_id)
                items_dict[key] = {
                    "item_id": item.id,
                    "item_name": item.name,
                    "item_code": item.item_code,
                    "category_name": category.name if category else None,
                    "unit": item.unit,
                    "current_stock": 1, # Assets are usually 1 per mapping
                    "min_stock_level": item.min_stock_level,
                    "unit_price": item.unit_price,
                    "total_value": item.unit_price or 0,
                    "source": "Asset Mapping",
                    "serial_number": mapping.serial_number,
                    "assigned_date": mapping.assigned_date
                }
            else:
                # If already exists (e.g. multiple assets of same type), increment count
                items_dict[key]["current_stock"] += 1
                items_dict[key]["total_value"] += (item.unit_price or 0)

    # Add items from asset registry
    for asset in asset_registry:
        item = asset.item
        if item:
            key = f"registry_{asset.id}" # Unique per asset instance
            category = inventory_crud.get_category_by_id(db, item.category_id)
            items_dict[key] = {
                "item_id": item.id,
                "item_name": item.name,
                "item_code": item.item_code,
                "category_name": category.name if category else None,
                "unit": item.unit,
                "current_stock": 1,
                "min_stock_level": item.min_stock_level,
                "unit_price": item.unit_price,
                "total_value": item.unit_price or 0,
                "source": "Asset Registry",
                "serial_number": asset.serial_number,
                "asset_tag": asset.asset_tag_id,
                "status": asset.status
            }
    
        
    # Calculate totals
    items_list = list(items_dict.values())
    total_items = sum(item["current_stock"] for item in items_list)
    total_value = sum(item["total_value"] for item in items_list)
    
    return {
        "location": {
            "id": location.id,
            "name": location.name,
            "building": location.building,
            "floor": location.floor,
            "room_area": location.room_area,
            "location_type": location.location_type
        },
        "total_items": total_items,
        "total_stock_value": total_value,
        "items": items_list
    }



@router.get("/stock-by-location")
def get_stock_by_location(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get inventory stock summary grouped by location"""
    from app.models.inventory import Location, AssetMapping, AssetRegistry, StockIssueDetail, StockIssue, LocationStock
    from sqlalchemy import func
    
    try:
        locations = inventory_crud.get_all_locations(db, skip=0, limit=1000)
        result = []
        
        for location in locations:
            try:
                # 1. Count assets in this location
                asset_count = db.query(AssetMapping).filter(
                    AssetMapping.location_id == location.id,
                    AssetMapping.is_active == True
                ).count()
                
                registry_count = db.query(AssetRegistry).filter(
                    AssetRegistry.current_location_id == location.id
                ).count()
                
                # 2. Get items from LocationStock (PRIMARY source for bulk items)
                location_stocks = db.query(LocationStock).filter(
                    LocationStock.location_id == location.id
                ).all()
                
                total_stock_value = 0
                items_count = 0
                
                # Calculate from LocationStock
                for stock in location_stocks:
                    item = stock.item
                    if item and stock.quantity > 0:
                        items_count += 1
                        total_stock_value += stock.quantity * (item.unit_price or 0)
                
                # 3. Get stock issues to this location (legacy/fallback)
                issues = db.query(StockIssueDetail).join(StockIssue).filter(
                    StockIssue.destination_location_id == location.id
                ).all()
                
                items_dict = {}  # Track unique items from issues
                
                for issue_detail in issues:
                    item = inventory_crud.get_item_by_id(db, issue_detail.item_id)
                    if item:
                        qty = getattr(issue_detail, 'issued_quantity', 0) or 0
                        if qty > 0:
                            if issue_detail.item_id not in items_dict:
                                items_dict[issue_detail.item_id] = 0
                            items_dict[issue_detail.item_id] += qty
                            # Only add to value if not already in LocationStock
                            if not any(s.item_id == issue_detail.item_id for s in location_stocks):
                                total_stock_value += qty * (item.unit_price or 0)
                
                # Add unique items from issues that aren't in LocationStock
                for item_id in items_dict:
                    if not any(s.item_id == item_id for s in location_stocks):
                        items_count += 1
                
                result.append({
                    **location.__dict__,
                    "asset_count": asset_count + registry_count,
                    "consumable_items_count": items_count,
                    "total_stock_value": total_stock_value,
                    "total_items": asset_count + registry_count + items_count
                })
            except Exception as e:
                # Skip this location if there's an error
                print(f"Warning: Error processing location {location.id}: {str(e)}")
                continue
        
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching stock by location: {str(e)}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching stock by location: {str(e)}")


@router.post("/locations/sync-rooms")
def sync_rooms_to_locations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Synchronize existing rooms from rooms table to locations table for inventory"""
    from app.models.room import Room
    from app.models.inventory import Location
    from app.curd import inventory as inventory_crud
    
    try:
        rooms = db.query(Room).all()
        synced_count = 0
        created_count = 0
        linked_count = 0
        
        for room in rooms:
            # Check if location already exists for this room
            from sqlalchemy import or_
            existing_location = db.query(Location).filter(
                or_(
                    Location.name == f"Room {room.number}",
                    Location.room_area == f"Room {room.number}"
                ),
                Location.location_type == "GUEST_ROOM"
            ).first()
            
            if existing_location:
                # Link room to existing location
                if not room.inventory_location_id:
                    room.inventory_location_id = existing_location.id
                    linked_count += 1
                synced_count += 1
            else:
                # Create new location for room using CRUD function
                location_data = {
                    "name": f"Room {room.number}",
                    "building": "Main Building",  # Default, can be updated later
                    "floor": None,  # Can be extracted from room number if needed
                    "room_area": f"Room {room.number}",
                    "location_type": "GUEST_ROOM",
                    "is_inventory_point": False,  # Rooms are not inventory points
                    "description": f"Guest room {room.number} - {room.type or 'Standard'}",
                    "is_active": (room.status != "Deleted" if room.status else True)
                }
                try:
                    location = inventory_crud.create_location(db, location_data)
                    
                    # Link room to location
                    room.inventory_location_id = location.id
                    created_count += 1
                    synced_count += 1
                except Exception as e:
                    db.rollback()
                    # Location might already exist, try to find and link
                    existing = db.query(Location).filter(
                        Location.name == f"Room {room.number}"
                    ).first()
                    if existing and not room.inventory_location_id:
                        room.inventory_location_id = existing.id
                        linked_count += 1
                        synced_count += 1
        
        db.commit()
        
        return {
            "message": "Rooms synchronized successfully",
            "total_rooms": len(rooms),
            "synced": synced_count,
            "locations_created": created_count,
            "rooms_linked": linked_count
        }
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error syncing rooms: {str(e)}")


# Asset Mapping Endpoints
@router.post("/asset-mappings", response_model=AssetMappingOut)
def create_asset_mapping(
    mapping: AssetMappingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    mapping_data = mapping.model_dump()
    created = inventory_crud.create_asset_mapping(db, mapping_data, assigned_by=current_user.id)
    
    # Load relationships for response
    assigner = db.query(User).filter(User.id == created.assigned_by).first()
    item = inventory_crud.get_item_by_id(db, created.item_id)
    location = inventory_crud.get_location_by_id(db, created.location_id)
    
    return {
        **created.__dict__,
        "assigned_by_name": assigner.name if assigner else None,
        "item_name": item.name if item else None,
        "location_name": f"{location.building} - {location.room_area}" if location else None
    }


@router.get("/asset-mappings", response_model=List[AssetMappingOut])
def get_asset_mappings(
    skip: int = 0,
    limit: int = 100,
    location_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    mappings = inventory_crud.get_all_asset_mappings(db, skip=skip, limit=limit, location_id=location_id)
    result = []
    for mapping in mappings:
        assigner = db.query(User).filter(User.id == mapping.assigned_by).first() if mapping.assigned_by else None
        item = inventory_crud.get_item_by_id(db, mapping.item_id)
        location = inventory_crud.get_location_by_id(db, mapping.location_id)
        result.append({
            **mapping.__dict__,
            "assigned_by_name": assigner.name if assigner else None,
            "item_name": item.name if item else None,
            "location_name": f"{location.building} - {location.room_area}" if location else None
        })
    return result


@router.delete("/asset-mappings/{mapping_id}")
def unassign_asset(
    mapping_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    mapping = inventory_crud.unassign_asset(db, mapping_id)
    if not mapping:
        raise HTTPException(status_code=404, detail="Asset mapping not found")
    return {"message": "Asset unassigned successfully"}


# Asset Registry Endpoints (The "Profile" - tracks individual instances)
@router.post("/asset-registry", response_model=AssetRegistryOut)
def create_asset_registry(
    asset: AssetRegistryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    asset_data = asset.model_dump()
    created = inventory_crud.create_asset_registry(db, asset_data)
    
    # Load relationships for response
    item = inventory_crud.get_item_by_id(db, created.item_id)
    location = inventory_crud.get_location_by_id(db, created.current_location_id) if created.current_location_id else None
    
    return {
        **created.__dict__,
        "item_name": item.name if item else None,
        "current_location_name": f"{location.building} - {location.room_area}" if location else None
    }


@router.get("/asset-registry", response_model=List[AssetRegistryOut])
def get_asset_registry(
    skip: int = 0,
    limit: int = 100,
    location_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    assets = inventory_crud.get_all_asset_registry(db, skip=skip, limit=limit, location_id=location_id, status=status)
    result = []
    for asset in assets:
        item = inventory_crud.get_item_by_id(db, asset.item_id)
        location = inventory_crud.get_location_by_id(db, asset.current_location_id) if asset.current_location_id else None
        result.append({
            **asset.__dict__,
            "item_name": item.name if item else None,
            "current_location_name": f"{location.building} - {location.room_area}" if location else None
        })
    return result


@router.get("/asset-registry/{asset_id}", response_model=AssetRegistryOut)
def get_asset_registry_by_id(asset_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    asset = inventory_crud.get_asset_registry_by_id(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    item = inventory_crud.get_item_by_id(db, asset.item_id)
    location = inventory_crud.get_location_by_id(db, asset.current_location_id) if asset.current_location_id else None
    
    return {
        **asset.__dict__,
        "item_name": item.name if item else None,
        "current_location_name": f"{location.building} - {location.room_area}" if location else None
    }


@router.put("/asset-registry/{asset_id}", response_model=AssetRegistryOut)
def update_asset_registry(
    asset_id: int,
    asset_update: AssetRegistryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    asset_data = asset_update.model_dump(exclude_unset=True)
    updated = inventory_crud.update_asset_registry(db, asset_id, asset_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    item = inventory_crud.get_item_by_id(db, updated.item_id)
    location = inventory_crud.get_location_by_id(db, updated.current_location_id) if updated.current_location_id else None
    
    return {
        **updated.__dict__,
        "item_name": item.name if item else None,
        "current_location_name": f"{location.building} - {location.room_area}" if location else None
    }


# Stock Requisition Endpoints
@router.post("/requisitions", response_model=StockRequisitionOut)
def create_stock_requisition(
    requisition: StockRequisitionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return inventory_crud.create_stock_requisition(db, requisition, requested_by_id=current_user.id)


@router.get("/requisitions", response_model=List[StockRequisitionOut])
def get_stock_requisitions(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return inventory_crud.get_all_stock_requisitions(db, skip=skip, limit=limit, status=status)


@router.get("/requisitions/{requisition_id}", response_model=StockRequisitionOut)
def get_stock_requisition(
    requisition_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    requisition = inventory_crud.get_stock_requisition_by_id(db, requisition_id)
    if not requisition:
        raise HTTPException(status_code=404, detail="Requisition not found")
    return requisition


@router.patch("/requisitions/{requisition_id}", response_model=StockRequisitionOut)
def update_stock_requisition(
    requisition_id: int,
    update_data: StockRequisitionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # For now, we only support status update via this endpoint or specific fields
    # If status is in update_data, use the status update logic
    if update_data.status:
        return inventory_crud.update_stock_requisition_status(
            db, requisition_id, update_data.status, approved_by_id=current_user.id if update_data.status == "approved" else None
        )
    return inventory_crud.get_stock_requisition_by_id(db, requisition_id)


@router.patch("/requisitions/{requisition_id}/status", response_model=StockRequisitionOut)
def update_stock_requisition_status(
    requisition_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated = inventory_crud.update_stock_requisition_status(
        db, requisition_id, status, approved_by_id=current_user.id if status == "approved" else None
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Requisition not found")
    return updated


# Stock Issue Endpoints
@router.post("/issues", response_model=StockIssueOut)
def create_stock_issue(
    issue: StockIssueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return inventory_crud.create_stock_issue(db, issue, issued_by_id=current_user.id)


@router.get("/issues", response_model=List[StockIssueOut])
def get_stock_issues(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return inventory_crud.get_all_stock_issues(db, skip=skip, limit=limit)
