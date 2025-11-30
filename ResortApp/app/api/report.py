"""
Comprehensive Reporting Module for Resort Management Application
Organized by Department: Front Office, Restaurant, Inventory, Housekeeping, Accounts, Security/HR, Management Dashboard
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func, and_, or_, case, cast, Date, extract
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from decimal import Decimal

from app.database import get_db
from app.models import (
    Booking, BookingRoom, PackageBooking, PackageBookingRoom,
    Checkout,
    FoodOrder, FoodOrderItem, FoodItem,
    InventoryItem, InventoryCategory, InventoryTransaction, PurchaseMaster, PurchaseDetail, WasteLog,
    Expense, Employee, Attendance,
    Room, Service, AssignedService, Vendor
)
from app.models.checkout import CheckoutPayment, CheckoutVerification
from app.models.employee import WorkingLog, Leave
from app.utils.api_optimization import apply_api_optimizations
from pydantic import BaseModel

router = APIRouter(prefix="/reports", tags=["Reports"])


# ============================================
# 1. 🏨 FRONT OFFICE REPORTS
# ============================================

class DailyArrivalReportItem(BaseModel):
    guest_name: str
    guest_mobile: Optional[str]
    guest_email: Optional[str]
    room_number: str
    room_type: Optional[str]
    adults: int
    children: int
    advance_paid: float
    total_amount: float
    special_requests: Optional[str]
    booking_type: str

class DailyArrivalReport(BaseModel):
    date: date
    arrivals: List[DailyArrivalReportItem]
    total: int

@router.get("/front-office/daily-arrival", response_model=DailyArrivalReport)
@apply_api_optimizations
def get_daily_arrival_report(
    report_date: Optional[date] = Query(None, description="Date for arrival report (default: today)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Daily Arrival Report: List of guests checking in today"""
    try:
        if not report_date:
            report_date = date.today()
        
        # Query regular bookings
        bookings = db.query(Booking).filter(
            Booking.check_in == report_date
        ).options(
            joinedload(Booking.booking_rooms).joinedload(BookingRoom.room),
            joinedload(Booking.user)
        ).all()
        
        # Query package bookings
        package_bookings = db.query(PackageBooking).filter(
            PackageBooking.check_in == report_date
        ).options(
            joinedload(PackageBooking.rooms).joinedload(PackageBookingRoom.room),
            joinedload(PackageBooking.package),
            joinedload(PackageBooking.user)
        ).all()
        
        result = []
        
        # Process regular bookings
        for booking in bookings:
            if booking.booking_rooms:
                for br in booking.booking_rooms:
                    result.append({
                        "guest_name": booking.guest_name or "N/A",
                        "guest_mobile": booking.guest_mobile or "-",
                        "guest_email": booking.guest_email or "-",
                        "room_number": br.room.number if br.room and br.room.number else "N/A",
                        "room_type": br.room.type if br.room and br.room.type else "N/A",
                        "adults": booking.adults or 0,
                        "children": booking.children or 0,
                        "advance_paid": float(booking.advance_deposit or 0),
                        "total_amount": float(booking.total_amount or 0),
                        "special_requests": booking.guest_email or "-",
                        "booking_type": "Regular"
                    })
            else:
                # Booking without rooms
                result.append({
                    "guest_name": booking.guest_name or "N/A",
                    "guest_mobile": booking.guest_mobile or "-",
                    "guest_email": booking.guest_email or "-",
                    "room_number": "N/A",
                    "room_type": "N/A",
                    "adults": booking.adults or 0,
                    "children": booking.children or 0,
                    "advance_paid": float(booking.advance_deposit or 0),
                    "total_amount": float(booking.total_amount or 0),
                    "special_requests": booking.guest_email or "-",
                    "booking_type": "Regular"
                })
        
        # Process package bookings
        for pkg_booking in package_bookings:
            if pkg_booking.rooms:
                for pbr in pkg_booking.rooms:
                    result.append({
                        "guest_name": pkg_booking.guest_name or "N/A",
                        "guest_mobile": pkg_booking.guest_mobile or "-",
                        "guest_email": pkg_booking.guest_email or "-",
                        "room_number": pbr.room.number if pbr.room and pbr.room.number else "N/A",
                        "room_type": pbr.room.type if pbr.room and pbr.room.type else "N/A",
                        "adults": pkg_booking.adults or 0,
                        "children": pkg_booking.children or 0,
                        "advance_paid": float(pkg_booking.advance_deposit or 0),
                        "total_amount": float(pkg_booking.package.price if pkg_booking.package and pkg_booking.package.price else 0),
                        "special_requests": f"Package: {pkg_booking.package.title if pkg_booking.package and pkg_booking.package.title else 'N/A'}",
                        "booking_type": "Package"
                    })
            else:
                # Package booking without rooms
                result.append({
                    "guest_name": pkg_booking.guest_name or "N/A",
                    "guest_mobile": pkg_booking.guest_mobile or "-",
                    "guest_email": pkg_booking.guest_email or "-",
                    "room_number": "N/A",
                    "room_type": "N/A",
                    "adults": pkg_booking.adults or 0,
                    "children": pkg_booking.children or 0,
                    "advance_paid": float(pkg_booking.advance_deposit or 0),
                    "total_amount": float(pkg_booking.package.price if pkg_booking.package and pkg_booking.package.price else 0),
                    "special_requests": f"Package: {pkg_booking.package.title if pkg_booking.package and pkg_booking.package.title else 'N/A'}",
                    "booking_type": "Package"
                })
        
        return {"date": report_date.isoformat(), "arrivals": result, "total": len(result)}
    except Exception as e:
        import traceback
        print(f"Error in daily-arrival report: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error generating daily arrival report: {str(e)}")


@router.get("/front-office/daily-departure")
@apply_api_optimizations
def get_daily_departure_report(
    report_date: Optional[date] = Query(None, description="Date for departure report (default: today)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Daily Departure Report: List of guests checking out"""
    from app.models.checkout import Checkout
    if not report_date:
        report_date = date.today()
    
    checkouts = db.query(Checkout).filter(
        func.date(Checkout.checkout_date) == report_date
    ).options(
        joinedload(Checkout.booking),
        joinedload(Checkout.package_booking),
        joinedload(Checkout.payments)
    ).offset(skip).limit(limit).all()
    
    result = []
    for checkout in checkouts:
        balance_pending = checkout.grand_total - sum(p.amount for p in checkout.payments)
        result.append({
            "room_number": checkout.room_number,
            "guest_name": checkout.guest_name,
            "checkout_time": checkout.checkout_date.isoformat() if checkout.checkout_date else None,
            "room_total": checkout.room_total,
            "food_total": checkout.food_total,
            "service_total": checkout.service_total,
            "grand_total": checkout.grand_total,
            "advance_deposit": checkout.advance_deposit,
            "balance_pending": balance_pending,
            "payment_method": checkout.payment_method,
            "invoice_number": checkout.invoice_number,
            "billing_instructions": "Standard checkout"  # Can be enhanced
        })
    
    return {"date": report_date.isoformat(), "departures": result, "total": len(result)}

@router.get("/front-office/occupancy")
@apply_api_optimizations
def get_occupancy_report(
    report_date: Optional[date] = Query(None, description="Date for occupancy report (default: today)"),
    db: Session = Depends(get_db)
):
    """Occupancy Report: % of rooms occupied vs vacant"""
    if not report_date:
        report_date = date.today()
    
    total_rooms = db.query(Room).count()
    
    # Occupied rooms (checked in but not checked out)
    occupied_bookings = db.query(Booking).filter(
        and_(
            Booking.check_in <= report_date,
            Booking.check_out > report_date,
            Booking.status.in_(["checked-in", "booked"])
        )
    ).count()
    
    occupied_packages = db.query(PackageBooking).filter(
        and_(
            PackageBooking.check_in <= report_date,
            PackageBooking.check_out > report_date,
            PackageBooking.status.in_(["checked-in", "booked"])
        )
    ).count()
    
    occupied_rooms = occupied_bookings + occupied_packages
    vacant_rooms = total_rooms - occupied_rooms
    occupancy_percentage = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
    
    return {
        "date": report_date.isoformat(),
        "total_rooms": total_rooms,
        "occupied_rooms": occupied_rooms,
        "vacant_rooms": vacant_rooms,
        "occupancy_percentage": round(occupancy_percentage, 2)
    }

@router.get("/front-office/police-c-form")
@apply_api_optimizations
def get_police_c_form_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=10000),
    db: Session = Depends(get_db)
):
    """Police / C-Form Report: List of foreign nationals (Legal Requirement) - Currently checked-in guests"""
    try:
        today = date.today()
        result = []
        
        # Query currently checked-in regular bookings
        booking_query = db.query(Booking).filter(
            and_(
                Booking.check_in <= today,
                Booking.check_out > today,
                Booking.status == "checked-in"
            )
        )
        
        if start_date:
            booking_query = booking_query.filter(Booking.check_in >= start_date)
        if end_date:
            booking_query = booking_query.filter(Booking.check_in <= end_date)
        
        bookings = booking_query.options(
            joinedload(Booking.booking_rooms).joinedload(BookingRoom.room)
        ).all()
        
        # Query currently checked-in package bookings
        package_query = db.query(PackageBooking).filter(
            and_(
                PackageBooking.check_in <= today,
                PackageBooking.check_out > today,
                PackageBooking.status == "checked-in"
            )
        )
        
        if start_date:
            package_query = package_query.filter(PackageBooking.check_in >= start_date)
        if end_date:
            package_query = package_query.filter(PackageBooking.check_in <= end_date)
        
        package_bookings = package_query.options(
            joinedload(PackageBooking.rooms).joinedload(PackageBookingRoom.room),
            joinedload(PackageBooking.package)
        ).all()
        
        # Process regular bookings
        for booking in bookings:
            room_numbers = []
            if booking.booking_rooms:
                for br in booking.booking_rooms:
                    if br.room:
                        room_numbers.append(br.room.number)
            
            # Extract passport/visa info from id_card_image_url if available, or use placeholder
            # In a real system, these would be separate fields
            passport_number = "N/A"
            visa_number = "N/A"
            nationality = "N/A"
            
            # If id_card_image_url exists, it might contain passport info
            # For now, we'll use placeholder values until proper fields are added
            if booking.id_card_image_url:
                passport_number = "See ID Card"
            
            result.append({
                "guest_name": booking.guest_name or "N/A",
                "guest_mobile": booking.guest_mobile or "-",
                "guest_email": booking.guest_email or "-",
                "check_in": booking.check_in.isoformat() if booking.check_in else None,
                "check_out": booking.check_out.isoformat() if booking.check_out else None,
                "passport_number": passport_number,
                "visa_number": visa_number,
                "nationality": nationality,
                "room_numbers": room_numbers if room_numbers else ["N/A"],
                "adults": booking.adults or 0,
                "children": booking.children or 0,
                "booking_type": "Regular",
                "booking_id": booking.id
            })
        
        # Process package bookings
        for pkg_booking in package_bookings:
            room_numbers = []
            if pkg_booking.rooms:
                for pbr in pkg_booking.rooms:
                    if pbr.room:
                        room_numbers.append(pbr.room.number)
            
            passport_number = "N/A"
            visa_number = "N/A"
            nationality = "N/A"
            
            if pkg_booking.id_card_image_url:
                passport_number = "See ID Card"
            
            result.append({
                "guest_name": pkg_booking.guest_name or "N/A",
                "guest_mobile": pkg_booking.guest_mobile or "-",
                "guest_email": pkg_booking.guest_email or "-",
                "check_in": pkg_booking.check_in.isoformat() if pkg_booking.check_in else None,
                "check_out": pkg_booking.check_out.isoformat() if pkg_booking.check_out else None,
                "passport_number": passport_number,
                "visa_number": visa_number,
                "nationality": nationality,
                "room_numbers": room_numbers if room_numbers else ["N/A"],
                "adults": pkg_booking.adults or 0,
                "children": pkg_booking.children or 0,
                "booking_type": "Package",
                "booking_id": pkg_booking.id
            })
        
        # Apply skip and limit
        total = len(result)
        result = result[skip:skip+limit]
        
        return {
            "foreign_nationals": result,
            "total": total,
            "showing": len(result),
            "date_range": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            }
        }
    except Exception as e:
        import traceback
        print(f"Error in police-c-form report: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error generating police C-form report: {str(e)}")


@router.get("/front-office/night-audit")
@apply_api_optimizations
def get_night_audit_report(
    audit_date: Optional[date] = Query(None, description="Date for night audit (default: yesterday)"),
    db: Session = Depends(get_db)
):
    """Night Audit Report: Summary of day's total business closed at midnight"""
    if not audit_date:
        audit_date = date.today() - timedelta(days=1)
    
    # Room revenue
    room_revenue = db.query(func.sum(Checkout.room_total)).filter(
        func.date(Checkout.checkout_date) == audit_date
    ).scalar() or 0
    
    # Food & Beverage revenue
    food_revenue = db.query(func.sum(Checkout.food_total)).filter(
        func.date(Checkout.checkout_date) == audit_date
    ).scalar() or 0
    
    # Service revenue
    service_revenue = db.query(func.sum(Checkout.service_total)).filter(
        func.date(Checkout.checkout_date) == audit_date
    ).scalar() or 0
    
    # Tax collected
    tax_collected = db.query(func.sum(Checkout.tax_amount)).filter(
        func.date(Checkout.checkout_date) == audit_date
    ).scalar() or 0
    
    # Total revenue
    total_revenue = room_revenue + food_revenue + service_revenue + tax_collected
    
    # Checkouts count
    checkouts_count = db.query(Checkout).filter(
        func.date(Checkout.checkout_date) == audit_date
    ).count()
    
    return {
        "audit_date": audit_date.isoformat(),
        "room_revenue": float(room_revenue),
        "food_beverage_revenue": float(food_revenue),
        "service_revenue": float(service_revenue),
        "tax_collected": float(tax_collected),
        "total_revenue": float(total_revenue),
        "checkouts_count": checkouts_count
    }


@router.get("/front-office/no-show-cancellation")
@apply_api_optimizations
def get_no_show_cancellation_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """No-Show & Cancellation Report: Revenue loss tracking"""
    query = db.query(Booking).filter(
        Booking.status.in_(["cancelled", "no-show"])
    )
    
    if start_date:
        query = query.filter(Booking.check_in >= start_date)
    if end_date:
        query = query.filter(Booking.check_in <= end_date)
    
    bookings = query.options(
        joinedload(Booking.booking_rooms).joinedload(BookingRoom.room)
    ).offset(skip).limit(limit).all()
    
    result = []
    total_revenue_loss = 0
    for booking in bookings:
        revenue_loss = booking.total_amount - booking.advance_deposit
        total_revenue_loss += revenue_loss
        result.append({
            "guest_name": booking.guest_name,
            "check_in": booking.check_in.isoformat(),
            "check_out": booking.check_out.isoformat(),
            "status": booking.status,
            "total_amount": booking.total_amount,
            "advance_deposit": booking.advance_deposit,
            "revenue_loss": revenue_loss,
            "rooms": [br.room.number if br.room else "N/A" for br in booking.booking_rooms]
        })
    
    return {
        "no_shows_cancellations": result,
        "total_revenue_loss": float(total_revenue_loss),
        "total_count": len(result)
    }


@router.get("/front-office/in-house-guests")
@apply_api_optimizations
def get_in_house_guest_list(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=10000),
    db: Session = Depends(get_db)
):
    """In-House Guest List: Currently checked-in guests (Emergency evacuation list)"""
    try:
        today = date.today()
        result = []
        
        # Query regular bookings that are currently checked in
        # Include bookings where check_in <= today and check_out > today
        # Exclude only cancelled and checked-out bookings
        booking_query = db.query(Booking).filter(
            and_(
                Booking.check_in <= today,
                Booking.check_out > today,
                ~func.lower(func.coalesce(Booking.status, '')).in_(["cancelled", "checked-out", "checked_out", "checkedout"])
            )
        )
        
        if start_date:
            booking_query = booking_query.filter(Booking.check_in >= start_date)
        if end_date:
            booking_query = booking_query.filter(Booking.check_in <= end_date)
        
        bookings = booking_query.options(
            joinedload(Booking.booking_rooms).joinedload(BookingRoom.room)
        ).all()
        
        # Query package bookings that are currently checked in
        package_query = db.query(PackageBooking).filter(
            and_(
                PackageBooking.check_in <= today,
                PackageBooking.check_out > today,
                ~func.lower(func.coalesce(PackageBooking.status, '')).in_(["cancelled", "checked-out", "checked_out", "checkedout"])
            )
        )
        
        if start_date:
            package_query = package_query.filter(PackageBooking.check_in >= start_date)
        if end_date:
            package_query = package_query.filter(PackageBooking.check_in <= end_date)
        
        package_bookings = package_query.options(
            joinedload(PackageBooking.rooms).joinedload(PackageBookingRoom.room),
            joinedload(PackageBooking.package)
        ).all()
        
        # Process regular bookings
        for booking in bookings:
            if booking.booking_rooms:
                for br in booking.booking_rooms:
                    if br.room:
                        result.append({
                            "guest_name": booking.guest_name or "N/A",
                            "guest_mobile": booking.guest_mobile or "-",
                            "guest_email": booking.guest_email or "-",
                            "room_number": br.room.number if br.room else "N/A",
                            "check_in": booking.check_in.isoformat() if booking.check_in else None,
                            "check_out": booking.check_out.isoformat() if booking.check_out else None,
                            "adults": booking.adults or 0,
                            "children": booking.children or 0,
                            "booking_type": "Regular",
                            "booking_id": booking.id,
                            "status": booking.status
                        })
            else:
                # Booking without rooms
                result.append({
                    "guest_name": booking.guest_name or "N/A",
                    "guest_mobile": booking.guest_mobile or "-",
                    "guest_email": booking.guest_email or "-",
                    "room_number": "N/A",
                    "check_in": booking.check_in.isoformat() if booking.check_in else None,
                    "check_out": booking.check_out.isoformat() if booking.check_out else None,
                    "adults": booking.adults or 0,
                    "children": booking.children or 0,
                    "booking_type": "Regular",
                    "booking_id": booking.id,
                    "status": booking.status
                })
        
        # Process package bookings
        for pkg_booking in package_bookings:
            if pkg_booking.rooms:
                for pbr in pkg_booking.rooms:
                    if pbr.room:
                        result.append({
                            "guest_name": pkg_booking.guest_name or "N/A",
                            "guest_mobile": pkg_booking.guest_mobile or "-",
                            "guest_email": pkg_booking.guest_email or "-",
                            "room_number": pbr.room.number if pbr.room else "N/A",
                            "check_in": pkg_booking.check_in.isoformat() if pkg_booking.check_in else None,
                            "check_out": pkg_booking.check_out.isoformat() if pkg_booking.check_out else None,
                            "adults": pkg_booking.adults or 0,
                            "children": pkg_booking.children or 0,
                            "booking_type": "Package",
                            "booking_id": pkg_booking.id,
                            "status": pkg_booking.status
                        })
            else:
                # Package booking without rooms
                result.append({
                    "guest_name": pkg_booking.guest_name or "N/A",
                    "guest_mobile": pkg_booking.guest_mobile or "-",
                    "guest_email": pkg_booking.guest_email or "-",
                    "room_number": "N/A",
                    "check_in": pkg_booking.check_in.isoformat() if pkg_booking.check_in else None,
                    "check_out": pkg_booking.check_out.isoformat() if pkg_booking.check_out else None,
                    "adults": pkg_booking.adults or 0,
                    "children": pkg_booking.children or 0,
                    "booking_type": "Package",
                    "booking_id": pkg_booking.id,
                    "status": pkg_booking.status
                })
        
        # Apply skip and limit
        total = len(result)
        result = result[skip:skip+limit]
        
        return {
            "in_house_guests": result,
            "total": total,
            "showing": len(result),
            "date_range": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            }
        }
    except Exception as e:
        import traceback
        print(f"Error in in-house-guests report: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error generating in-house guest list: {str(e)}")


# ============================================
# 2. 🥘 RESTAURANT (F&B) REPORTS
# ============================================

@router.get("/restaurant/daily-sales-summary")
@apply_api_optimizations
def get_daily_sales_summary(
    report_date: Optional[date] = Query(None, description="Date for sales summary (default: today)"),
    db: Session = Depends(get_db)
):
    """Daily Sales Summary: Food vs Beverage vs Alcohol sales by meal period"""
    if not report_date:
        report_date = date.today()
    
    # Get all food orders for the date
    orders = db.query(FoodOrder).filter(
        func.date(FoodOrder.created_at) == report_date
    ).options(
        joinedload(FoodOrder.items).joinedload(FoodOrderItem.food_item)
    ).all()
    
    food_sales = 0
    beverage_sales = 0
    alcohol_sales = 0
    
    breakfast_total = 0
    lunch_total = 0
    dinner_total = 0
    
    for order in orders:
        order_total = order.amount or 0
        hour = order.created_at.hour if order.created_at else 12
        
        # Categorize by meal period
        if 6 <= hour < 11:
            breakfast_total += order_total
        elif 11 <= hour < 16:
            lunch_total += order_total
        elif 16 <= hour < 23:
            dinner_total += order_total
        
        # Categorize by item type (requires FoodItem.category field)
        for item in order.items:
            if item.food_item:
                # Assuming category field exists - adjust based on actual model
                category = getattr(item.food_item, 'category', None)
                item_total = (item.food_item.price or 0) * (item.quantity or 0)
                
                if category == "Beverage" or "drink" in (item.food_item.name or "").lower():
                    beverage_sales += item_total
                elif category == "Alcohol" or "alcohol" in (item.food_item.name or "").lower():
                    alcohol_sales += item_total
                else:
                    food_sales += item_total
    
    return {
        "date": report_date.isoformat(),
        "food_sales": float(food_sales),
        "beverage_sales": float(beverage_sales),
        "alcohol_sales": float(alcohol_sales),
        "breakfast_sales": float(breakfast_total),
        "lunch_sales": float(lunch_total),
        "dinner_sales": float(dinner_total),
        "total_sales": float(food_sales + beverage_sales + alcohol_sales)
    }


@router.get("/restaurant/item-wise-sales")
@apply_api_optimizations
def get_item_wise_sales_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Item-wise Sales Report: Which dish is selling the most?"""
    query = db.query(
        FoodItem.id,
        FoodItem.name,
        func.sum(FoodOrderItem.quantity).label("total_quantity"),
        func.sum(FoodOrderItem.quantity * FoodItem.price).label("total_revenue")
    ).join(
        FoodOrderItem, FoodOrderItem.food_item_id == FoodItem.id
    ).join(
        FoodOrder, FoodOrderItem.order_id == FoodOrder.id
    )
    
    if start_date:
        query = query.filter(func.date(FoodOrder.created_at) >= start_date)
    if end_date:
        query = query.filter(func.date(FoodOrder.created_at) <= end_date)
    
    query = query.group_by(FoodItem.id, FoodItem.name).order_by(
        func.sum(FoodOrderItem.quantity * FoodItem.price).desc()
    )
    
    results = query.offset(skip).limit(limit).all()
    
    return {
        "items": [
            {
                "item_name": r.name,
                "total_quantity": int(r.total_quantity or 0),
                "total_revenue": float(r.total_revenue or 0)
            }
            for r in results
        ],
        "total_items": len(results)
    }


@router.get("/restaurant/kot-analysis")
@apply_api_optimizations
def get_kot_analysis(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """KOT Analysis: Time between Order (KOT) and Service (Kitchen Efficiency)"""
    # Note: Requires order_time and service_time fields in FoodOrder
    # For now, using created_at as order_time
    query = db.query(FoodOrder).filter(FoodOrder.status == "completed")
    
    if start_date:
        query = query.filter(func.date(FoodOrder.created_at) >= start_date)
    if end_date:
        query = query.filter(func.date(FoodOrder.created_at) <= end_date)
    
    orders = query.options(
        joinedload(FoodOrder.room),
        joinedload(FoodOrder.items)
    ).offset(skip).limit(limit).all()
    
    result = []
    for order in orders:
        # Assuming service_time field exists - adjust based on actual model
        order_time = order.created_at
        service_time = getattr(order, 'service_time', None) or order.created_at
        
        if service_time and order_time:
            time_taken = (service_time - order_time).total_seconds() / 60  # minutes
        else:
            time_taken = 0
        
        result.append({
            "kot_number": f"KOT-{order.id}",
            "room_number": order.room.number if order.room else "Dine-in",
            "order_time": order_time.isoformat() if order_time else None,
            "service_time": service_time.isoformat() if service_time else None,
            "time_taken_minutes": round(time_taken, 2),
            "items_count": len(order.items),
            "status": order.status
        })
    
    return {"kot_analysis": result, "total": len(result)}


@router.get("/restaurant/void-cancellation")
@apply_api_optimizations
def get_void_cancellation_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=10000),
    db: Session = Depends(get_db)
):
    """Void / Cancellation Report: Tracks orders cancelled or voided after being created (Security)"""
    try:
        # Query orders with cancelled, voided, or similar statuses
        # Handle different status formats
        query = db.query(FoodOrder).filter(
            func.lower(func.coalesce(FoodOrder.status, '')).in_([
                'cancelled', 'canceled', 'voided', 'void', 'deleted'
            ])
        )
        
        if start_date:
            query = query.filter(func.date(FoodOrder.created_at) >= start_date)
        if end_date:
            query = query.filter(func.date(FoodOrder.created_at) <= end_date)
        
        orders = query.options(
            joinedload(FoodOrder.room),
            joinedload(FoodOrder.employee),
            joinedload(FoodOrder.items).joinedload(FoodOrderItem.food_item)
        ).order_by(FoodOrder.created_at.desc()).all()
        
        result = []
        total_amount = 0.0
        
        for order in orders:
            # Get item details
            items_detail = []
            for item in order.items:
                item_name = item.food_item.name if item.food_item else f"Item #{item.food_item_id}"
                items_detail.append(f"{item_name} (x{item.quantity})")
            
            order_amount = float(order.amount or 0)
            total_amount += order_amount
            
            result.append({
                "order_id": order.id,
                "room_number": order.room.number if order.room and order.room.number else "Dine-in",
                "guest_name": getattr(order, 'guest_name', None) or "N/A",
                "order_time": order.created_at.isoformat() if order.created_at else None,
                "order_date": order.created_at.date().isoformat() if order.created_at else None,
                "amount": order_amount,
                "status": order.status or "N/A",
                "employee_name": order.employee.name if order.employee and order.employee.name else "N/A",
                "employee_id": order.assigned_employee_id,
                "items_count": len(order.items) if order.items else 0,
                "items_detail": ", ".join(items_detail) if items_detail else "N/A",
                "order_type": order.order_type or "dine_in",
                "billing_status": order.billing_status or "unbilled",
                "void_reason": "N/A"  # Can be added as a field later
            })
        
        # Apply skip and limit
        total = len(result)
        result = result[skip:skip+limit]
        
        return {
            "voided_orders": result,
            "total": total,
            "showing": len(result),
            "total_amount": float(total_amount),
            "date_range": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            }
        }
    except Exception as e:
        import traceback
        print(f"Error in void-cancellation report: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error generating void/cancellation report: {str(e)}")


@router.get("/restaurant/discount-complimentary")
@apply_api_optimizations
def get_discount_complimentary_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=10000),
    db: Session = Depends(get_db)
):
    """Discount & Complimentary Report: Free meals given (Manager approval tracking)"""
    try:
        # Get all orders and calculate original amount from items
        query = db.query(FoodOrder)
        
        if start_date:
            query = query.filter(func.date(FoodOrder.created_at) >= start_date)
        if end_date:
            query = query.filter(func.date(FoodOrder.created_at) <= end_date)
        
        orders = query.options(
            joinedload(FoodOrder.room),
            joinedload(FoodOrder.employee),
            joinedload(FoodOrder.items).joinedload(FoodOrderItem.food_item)
        ).order_by(FoodOrder.created_at.desc()).all()
        
        result = []
        total_complimentary = 0.0
        total_discount = 0.0
        
        for order in orders:
            # Calculate original amount from items
            original_amount = 0.0
            items_detail = []
            
            if order.items:
                for item in order.items:
                    if item.food_item and item.food_item.price:
                        item_total = float(item.food_item.price) * (item.quantity or 0)
                        original_amount += item_total
                        item_name = item.food_item.name or f"Item #{item.food_item_id}"
                        items_detail.append(f"{item_name} (x{item.quantity})")
            
            final_amount = float(order.amount or 0)
            discount_amount = original_amount - final_amount if original_amount > final_amount else 0.0
            is_complimentary = final_amount == 0 and original_amount > 0
            
            # Only include orders with discounts or complimentary
            if discount_amount > 0 or is_complimentary:
                # Get guest name from room booking
                guest_name = "N/A"
                if order.room:
                    # Try to find active booking for this room
                    today = date.today()
                    booking = db.query(Booking).join(BookingRoom).filter(
                        and_(
                            BookingRoom.room_id == order.room.id,
                            Booking.check_in <= today,
                            Booking.check_out > today,
                            ~func.lower(func.coalesce(Booking.status, '')).in_(["cancelled", "checked-out", "checked_out", "checkedout"])
                        )
                    ).first()
                    
                    if booking:
                        guest_name = booking.guest_name or "N/A"
                    else:
                        # Try package booking
                        pkg_booking = db.query(PackageBooking).join(PackageBookingRoom).filter(
                            and_(
                                PackageBookingRoom.room_id == order.room.id,
                                PackageBooking.check_in <= today,
                                PackageBooking.check_out > today,
                                ~func.lower(func.coalesce(PackageBooking.status, '')).in_(["cancelled", "checked-out", "checked_out", "checkedout"])
                            )
                        ).first()
                        
                        if pkg_booking:
                            guest_name = pkg_booking.guest_name or "N/A"
                
                if is_complimentary:
                    total_complimentary += original_amount
                else:
                    total_discount += discount_amount
                
                result.append({
                    "order_id": order.id,
                    "room_number": order.room.number if order.room and order.room.number else "Dine-in",
                    "guest_name": guest_name,
                    "order_time": order.created_at.isoformat() if order.created_at else None,
                    "order_date": order.created_at.date().isoformat() if order.created_at else None,
                    "original_amount": float(original_amount),
                    "discount_amount": float(discount_amount),
                    "final_amount": final_amount,
                    "is_complimentary": is_complimentary,
                    "employee_name": order.employee.name if order.employee and order.employee.name else "N/A",
                    "employee_id": order.assigned_employee_id,
                    "items_count": len(order.items) if order.items else 0,
                    "items_detail": ", ".join(items_detail) if items_detail else "N/A",
                    "order_type": order.order_type or "dine_in",
                    "billing_status": order.billing_status or "unbilled",
                    "approved_by": "N/A",  # Can be added as a field later
                    "reason": "Complimentary" if is_complimentary else f"Discount: {discount_amount:.2f}"
                })
        
        # Apply skip and limit
        total = len(result)
        result = result[skip:skip+limit]
        
        return {
            "discounts_complimentary": result,
            "total": total,
            "showing": len(result),
            "total_complimentary_amount": float(total_complimentary),
            "total_discount_amount": float(total_discount),
            "complimentary_count": len([r for r in result if r.get("is_complimentary", False)]),
            "discount_count": len([r for r in result if not r.get("is_complimentary", False)]),
            "date_range": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            }
        }
    except Exception as e:
        import traceback
        print(f"Error in discount-complimentary report: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error generating discount/complimentary report: {str(e)}")


@router.get("/restaurant/nc-report")
@apply_api_optimizations
def get_nc_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=10000),
    db: Session = Depends(get_db)
):
    """NC (Non-Chargeable) Report: Food given to Staff or Owners (No revenue, but inventory reduced)"""
    try:
        # Get orders with amount = 0 (complimentary) or billing_status indicating non-chargeable
        # Also check if order has no room (staff meal) or specific indicators
        query = db.query(FoodOrder).filter(
            or_(
                FoodOrder.amount == 0,
                FoodOrder.billing_status.in_(["non_chargeable", "non-chargeable", "nc", "staff_meal"]),
                FoodOrder.room_id.is_(None)  # Orders without room assignment (likely staff meals)
            )
        )
        
        if start_date:
            query = query.filter(func.date(FoodOrder.created_at) >= start_date)
        if end_date:
            query = query.filter(func.date(FoodOrder.created_at) <= end_date)
        
        orders = query.options(
            joinedload(FoodOrder.room),
            joinedload(FoodOrder.employee),
            joinedload(FoodOrder.items).joinedload(FoodOrderItem.food_item)
        ).order_by(FoodOrder.created_at.desc()).all()
        
        result = []
        total_value = 0.0
        
        for order in orders:
            # Calculate total value from items
            items_detail = []
            order_value = 0.0
            
            if order.items:
                for item in order.items:
                    if item.food_item:
                        item_price = float(item.food_item.price or 0)
                        item_qty = item.quantity or 0
                        item_total = item_price * item_qty
                        order_value += item_total
                        item_name = item.food_item.name or f"Item #{item.food_item_id}"
                        items_detail.append({
                            "item_name": item_name,
                            "quantity": item_qty,
                            "unit_price": item_price,
                            "total": item_total
                        })
            
            total_value += order_value
            
            # Determine recipient type
            recipient_type = "Staff"
            recipient_name = "N/A"
            
            if order.employee:
                recipient_name = order.employee.name or "Staff Member"
                recipient_type = "Staff"
            elif not order.room:
                recipient_type = "Staff/Owner"
                recipient_name = "Staff/Owner"
            elif order.room:
                # If order has room but amount is 0, might be guest complimentary
                recipient_type = "Guest (Complimentary)"
                # Try to get guest name
                today = date.today()
                booking = db.query(Booking).join(BookingRoom).filter(
                    and_(
                        BookingRoom.room_id == order.room.id,
                        Booking.check_in <= today,
                        Booking.check_out > today
                    )
                ).first()
                if booking:
                    recipient_name = booking.guest_name or "Guest"
                else:
                    recipient_name = "Guest"
            
            result.append({
                "order_id": order.id,
                "recipient_name": recipient_name,
                "recipient_type": recipient_type,
                "employee_name": order.employee.name if order.employee and order.employee.name else "N/A",
                "employee_id": order.assigned_employee_id,
                "room_number": order.room.number if order.room and order.room.number else "N/A",
                "order_time": order.created_at.isoformat() if order.created_at else None,
                "order_date": order.created_at.date().isoformat() if order.created_at else None,
                "items": items_detail,
                "items_count": len(items_detail),
                "total_value": float(order_value),
                "billing_status": order.billing_status or "unbilled",
                "order_type": order.order_type or "dine_in"
            })
        
        # Apply skip and limit
        total = len(result)
        result = result[skip:skip+limit]
        
        return {
            "nc_orders": result,
            "total": total,
            "showing": len(result),
            "total_value": float(total_value),
            "date_range": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            }
        }
    except Exception as e:
        import traceback
        print(f"Error in nc-report: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error generating NC report: {str(e)}")


# ============================================
# 3. 📦 INVENTORY & PURCHASE REPORTS
# ============================================

@router.get("/inventory/stock-status")
@apply_api_optimizations
def get_stock_status_report(
    category_id: Optional[int] = Query(None),
    location: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Stock Status Report: Current quantity and value of every item"""
    query = db.query(InventoryItem).options(
        joinedload(InventoryItem.category),
        joinedload(InventoryItem.preferred_vendor)
    )
    
    if category_id:
        query = query.filter(InventoryItem.category_id == category_id)
    if location:
        query = query.filter(InventoryItem.location == location)
    
    items = query.offset(skip).limit(limit).all()
    
    result = []
    for item in items:
        stock_value = item.current_stock * item.unit_price
        result.append({
            "item_name": item.name,
            "item_code": item.item_code,
            "category": item.category.name if item.category else "N/A",
            "unit": item.unit,
            "current_stock": float(item.current_stock),
            "unit_price": float(item.unit_price),
            "stock_value": float(stock_value),
            "location": item.location,
            "min_stock_level": float(item.min_stock_level),
            "status": "Low Stock" if item.current_stock < item.min_stock_level else "OK"
        })
    
    return {"stock_status": result, "total": len(result)}


@router.get("/inventory/low-stock-alert")
@apply_api_optimizations
def get_low_stock_alert(
    db: Session = Depends(get_db)
):
    """Low Stock Alert Report: Items below minimum level"""
    items = db.query(InventoryItem).filter(
        InventoryItem.current_stock < InventoryItem.min_stock_level
    ).options(
        joinedload(InventoryItem.category),
        joinedload(InventoryItem.preferred_vendor)
    ).all()
    
    result = []
    for item in items:
        shortage = item.min_stock_level - item.current_stock
        result.append({
            "item_name": item.name,
            "item_code": item.item_code,
            "category": item.category.name if item.category else "N/A",
            "current_stock": float(item.current_stock),
            "min_stock_level": float(item.min_stock_level),
            "shortage": float(shortage),
            "unit": item.unit,
            "preferred_vendor": item.preferred_vendor.name if item.preferred_vendor else "N/A",
            "urgency": "Critical" if item.current_stock == 0 else "High"
        })
    
    return {"low_stock_items": result, "total": len(result)}


@router.get("/inventory/expiry-aging")
@apply_api_optimizations
def get_expiry_aging_report(
    days_ahead: int = Query(3, ge=1, le=30, description="Days ahead to check for expiry"),
    db: Session = Depends(get_db)
):
    """Expiry / Aging Report: Perishable items expiring in next N days"""
    # Note: Requires expiry_date field in InventoryTransaction or InventoryItem
    # For now, checking perishable items
    cutoff_date = date.today() + timedelta(days=days_ahead)
    
    # Get perishable items with transactions
    items = db.query(InventoryItem).filter(
        InventoryItem.is_perishable == True
    ).options(
        joinedload(InventoryItem.category),
        joinedload(InventoryItem.transactions)
    ).all()
    
    result = []
    for item in items:
        # Check transactions for expiry dates
        for transaction in item.transactions:
            expiry_date = getattr(transaction, 'expiry_date', None)
            if expiry_date and expiry_date <= cutoff_date:
                days_until_expiry = (expiry_date - date.today()).days
                result.append({
                    "item_name": item.name,
                    "item_code": item.item_code,
                    "batch_number": getattr(transaction, 'batch_number', 'N/A'),
                    "quantity": float(transaction.quantity) if hasattr(transaction, 'quantity') else 0,
                    "expiry_date": expiry_date.isoformat() if expiry_date else None,
                    "days_until_expiry": days_until_expiry,
                    "location": item.location,
                    "urgency": "Expired" if days_until_expiry < 0 else ("Critical" if days_until_expiry <= 1 else "High")
                })
    
    return {"expiring_items": result, "total": len(result), "days_ahead": days_ahead}


@router.get("/inventory/stock-movement")
@apply_api_optimizations
def get_stock_movement_register(
    item_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Stock Movement Register: History of item (In -> Move -> Out)"""
    from app.models.inventory import StockIssue, StockIssueDetail, Location
    
    query = db.query(InventoryTransaction).options(
        joinedload(InventoryTransaction.item),
        joinedload(InventoryTransaction.user),
        joinedload(InventoryTransaction.purchase_master)
    )
    
    if item_id:
        query = query.filter(InventoryTransaction.item_id == item_id)
    if start_date:
        query = query.filter(func.date(InventoryTransaction.created_at) >= start_date)
    if end_date:
        query = query.filter(func.date(InventoryTransaction.created_at) <= end_date)
    
    transactions = query.order_by(InventoryTransaction.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for trans in transactions:
        # Try to get location info from related StockIssue records
        from_location = "-"
        to_location = "-"
        
        # Check if transaction notes reference a stock issue
        if trans.notes:
            # Try to find related stock issue by matching item and date
            stock_issue = db.query(StockIssue).join(StockIssueDetail).filter(
                StockIssueDetail.item_id == trans.item_id,
                func.date(StockIssue.issue_date) == func.date(trans.created_at)
            ).options(
                joinedload(StockIssue.source_location),
                joinedload(StockIssue.destination_location)
            ).first()
            
            if stock_issue:
                if stock_issue.source_location:
                    from_location = stock_issue.source_location.name or f"{stock_issue.source_location.building} - {stock_issue.source_location.room_area}" if stock_issue.source_location.building else "-"
                if stock_issue.destination_location:
                    to_location = stock_issue.destination_location.name or f"{stock_issue.destination_location.building} - {stock_issue.destination_location.room_area}" if stock_issue.destination_location.building else "-"
        
        # If still no location, try to extract from notes
        if from_location == "-" and to_location == "-" and trans.notes:
            notes_lower = trans.notes.lower()
            if "location:" in notes_lower or "to" in notes_lower:
                # Try to extract location from notes
                if "location:" in notes_lower:
                    parts = trans.notes.split("Location:")
                    if len(parts) > 1:
                        location_info = parts[1].strip()
                        if "to" in location_info.lower():
                            loc_parts = location_info.split("to")
                            if len(loc_parts) >= 2:
                                from_location = loc_parts[0].strip() or "-"
                                to_location = loc_parts[1].strip() or "-"
                            else:
                                to_location = location_info.strip() or "-"
                        else:
                            to_location = location_info.strip() or "-"
        
        # Fallback to item's default location
        if from_location == "-" and trans.item and trans.item.location:
            from_location = trans.item.location
        
        # Get reference from purchase_master or reference_number
        reference = "-"
        if trans.reference_number:
            reference = trans.reference_number
        elif trans.purchase_master:
            reference = f"PO-{trans.purchase_master.purchase_number}" if hasattr(trans.purchase_master, 'purchase_number') else f"Purchase-{trans.purchase_master.id}"
        elif trans.id:
            reference = f"TXN-{trans.id}"
        
        # Get user name
        created_by_name = "-"
        if trans.user:
            created_by_name = trans.user.name or trans.user.email or f"User-{trans.created_by}"
        elif trans.created_by:
            created_by_name = f"User-{trans.created_by}"
        
        result.append({
            "transaction_id": trans.id,
            "item_name": trans.item.name if trans.item else "-",
            "transaction_type": trans.transaction_type or "-",
            "quantity": float(trans.quantity) if trans.quantity else 0,
            "unit": trans.item.unit if trans.item else "-",
            "from_location": from_location,
            "to_location": to_location,
            "reference": reference,
            "created_at": trans.created_at.isoformat() if trans.created_at else None,
            "created_by": created_by_name
        })
    
    return {"stock_movements": result, "total": len(result)}


@router.get("/inventory/waste-spoilage")
@apply_api_optimizations
def get_waste_spoilage_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Waste & Spoilage Report: Value of items thrown away"""
    try:
        query = db.query(WasteLog).options(
            joinedload(WasteLog.item),
            joinedload(WasteLog.location),
            joinedload(WasteLog.reporter)
        )
        
        if start_date:
            query = query.filter(func.date(WasteLog.waste_date) >= start_date)
        if end_date:
            query = query.filter(func.date(WasteLog.waste_date) <= end_date)
        
        waste_logs = query.order_by(WasteLog.waste_date.desc()).offset(skip).limit(limit).all()
        
        result = []
        total_waste_value = 0
        for waste in waste_logs:
            # Calculate value lost
            unit_price = waste.item.unit_price if waste.item and waste.item.unit_price else 0
            waste_value = float(waste.quantity) * unit_price
            total_waste_value += waste_value
            
            # Get location name
            location_name = "-"
            if waste.location:
                if hasattr(waste.location, 'name') and waste.location.name:
                    location_name = waste.location.name
                elif hasattr(waste.location, 'building') and waste.location.building:
                    room_area = getattr(waste.location, 'room_area', '') or ''
                    location_name = f"{waste.location.building} - {room_area}".strip() if room_area else waste.location.building
            
            # Get reporter name
            reported_by_name = "-"
            if waste.reporter:
                reported_by_name = waste.reporter.name or waste.reporter.email or f"User-{waste.reported_by}"
            elif waste.reported_by:
                reported_by_name = f"User-{waste.reported_by}"
            
            result.append({
                "item_name": waste.item.name if waste.item else "-",
                "quantity": float(waste.quantity) if waste.quantity else 0,
                "unit": waste.item.unit if waste.item else "-",
                "waste_value": round(waste_value, 2),
                "reason_code": waste.reason_code if waste.reason_code else "-",
                "action_taken": waste.action_taken if waste.action_taken else "-",
                "location": location_name,
                "batch_number": waste.batch_number if waste.batch_number else "-",
                "expiry_date": waste.expiry_date.isoformat() if waste.expiry_date else None,
                "waste_date": waste.waste_date.isoformat() if waste.waste_date else None,
                "reported_by": reported_by_name,
                "notes": waste.notes if waste.notes else "-"
            })
        
        return {
            "waste_logs": result,
            "total_waste_value": round(total_waste_value, 2),
            "total": len(result)
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating waste & spoilage report: {str(e)}")


@router.get("/inventory/purchase-register")
@apply_api_optimizations
def get_purchase_register(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    vendor_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Purchase Register: List of all Vendor Bills entered"""
    try:
        query = db.query(PurchaseMaster).options(
            joinedload(PurchaseMaster.vendor),
            joinedload(PurchaseMaster.details).joinedload(PurchaseDetail.item),
            joinedload(PurchaseMaster.user)
        )
        
        if start_date:
            query = query.filter(PurchaseMaster.purchase_date >= start_date)
        if end_date:
            query = query.filter(PurchaseMaster.purchase_date <= end_date)
        if vendor_id:
            query = query.filter(PurchaseMaster.vendor_id == vendor_id)
        
        purchases = query.order_by(PurchaseMaster.purchase_date.desc()).offset(skip).limit(limit).all()
        
        result = []
        for purchase in purchases:
            # Calculate total tax amount
            tax_amount = float(purchase.cgst or 0) + float(purchase.sgst or 0) + float(purchase.igst or 0)
            
            result.append({
                "purchase_id": purchase.id,
                "purchase_number": purchase.purchase_number if purchase.purchase_number else "-",
                "invoice_number": purchase.invoice_number if purchase.invoice_number else "-",
                "vendor_name": purchase.vendor.name if purchase.vendor else "-",
                "purchase_date": purchase.purchase_date.isoformat() if purchase.purchase_date else None,
                "invoice_date": purchase.invoice_date.isoformat() if purchase.invoice_date else None,
                "sub_total": float(purchase.sub_total or 0),
                "cgst": float(purchase.cgst or 0),
                "sgst": float(purchase.sgst or 0),
                "igst": float(purchase.igst or 0),
                "tax_amount": round(tax_amount, 2),
                "discount": float(purchase.discount or 0),
                "total_amount": float(purchase.total_amount or 0),
                "payment_status": purchase.payment_status if purchase.payment_status else "-",
                "status": purchase.status if purchase.status else "-",
                "items_count": len(purchase.details) if purchase.details else 0,
                "created_by": purchase.user.name if purchase.user else (f"User-{purchase.created_by}" if purchase.created_by else "-")
            })
        
        return {"purchases": result, "total": len(result)}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating purchase register: {str(e)}")


@router.get("/inventory/variance")
@apply_api_optimizations
def get_variance_report(
    location: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Variance Report: Difference between System Stock and Physical Audit Stock"""
    # Note: Requires physical_count field from audit
    # For now, returning items that may need audit
    query = db.query(InventoryItem).options(
        joinedload(InventoryItem.category)
    )
    
    if location:
        query = query.filter(InventoryItem.location == location)
    
    items = query.offset(skip).limit(limit).all()
    
    result = []
    for item in items:
        physical_count = getattr(item, 'physical_count', None)  # Add physical_count field
        system_stock = item.current_stock
        variance = (physical_count - system_stock) if physical_count is not None else 0
        variance_value = variance * item.unit_price
        
        result.append({
            "item_name": item.name,
            "item_code": item.item_code,
            "system_stock": float(system_stock),
            "physical_count": float(physical_count) if physical_count is not None else None,
            "variance": float(variance),
            "variance_value": float(variance_value),
            "unit": item.unit,
            "location": item.location,
            "status": "Match" if variance == 0 else ("Shortage" if variance < 0 else "Excess")
        })
    
    return {"variance_report": result, "total": len(result)}


# ============================================
# 4. 🧹 HOUSEKEEPING & FACILITY REPORTS
# ============================================

@router.get("/housekeeping/room-discrepancy")
@apply_api_optimizations
def get_room_discrepancy_report(
    db: Session = Depends(get_db)
):
    """Room Discrepancy Report: Front Desk vs Housekeeping status mismatch"""
    # Get all rooms
    rooms = db.query(Room).all()
    
    result = []
    for room in rooms:
        # Check booking status
        booking = db.query(Booking).join(BookingRoom).filter(
            and_(
                BookingRoom.room_id == room.id,
                Booking.check_in <= date.today(),
                Booking.check_out > date.today(),
                Booking.status == "checked-in"
            )
        ).first()
        
        # Front desk status
        front_desk_status = "Occupied" if booking else "Vacant"
        
        # Housekeeping status (requires housekeeping_status field in Room)
        housekeeping_status = getattr(room, 'housekeeping_status', room.status)
        
        if front_desk_status != housekeeping_status:
            result.append({
                "room_number": room.number,
                "front_desk_status": front_desk_status,
                "housekeeping_status": housekeeping_status,
                "discrepancy": f"{front_desk_status} vs {housekeeping_status}",
                "guest_name": booking.guest_name if booking else "N/A",
                "severity": "Critical" if front_desk_status == "Vacant" and housekeeping_status == "Occupied" else "Warning"
            })
    
    return {"discrepancies": result, "total": len(result)}


@router.get("/housekeeping/laundry-cost")
@apply_api_optimizations
def get_laundry_cost_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Laundry Cost Report: Linen sent vs returned, torn/damaged tracking"""
    # Note: Requires laundry tracking in InventoryTransaction
    # Filter by items with track_laundry_cycle = True
    query = db.query(InventoryTransaction).join(InventoryItem).filter(
        InventoryItem.track_laundry_cycle == True
    )
    
    if start_date:
        query = query.filter(func.date(InventoryTransaction.created_at) >= start_date)
    if end_date:
        query = query.filter(func.date(InventoryTransaction.created_at) <= end_date)
    
    transactions = query.options(
        joinedload(InventoryTransaction.item)
    ).all()
    
    sent_count = 0
    returned_count = 0
    damaged_count = 0
    
    for trans in transactions:
        if trans.transaction_type == "laundry_sent":
            sent_count += trans.quantity
        elif trans.transaction_type == "laundry_returned":
            returned_count += trans.quantity
        elif trans.transaction_type == "laundry_damaged":
            damaged_count += trans.quantity
    
    return {
        "period": {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None
        },
        "linen_sent": float(sent_count),
        "linen_returned": float(returned_count),
        "linen_damaged": float(damaged_count),
        "linen_pending": float(sent_count - returned_count - damaged_count)
    }


@router.get("/housekeeping/minibar-consumption")
@apply_api_optimizations
def get_minibar_consumption_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Minibar Consumption: Items consumed from room minibars"""
    # Get checkout verifications with consumables audit
    query = db.query(CheckoutVerification).join(Checkout).filter(
        CheckoutVerification.consumables_audit_data.isnot(None)
    )
    
    if start_date:
        query = query.filter(func.date(Checkout.checkout_date) >= start_date)
    if end_date:
        query = query.filter(func.date(Checkout.checkout_date) <= end_date)
    
    verifications = query.options(
        joinedload(CheckoutVerification.checkout)
    ).offset(skip).limit(limit).all()
    
    result = []
    for verification in verifications:
        consumables = verification.consumables_audit_data or {}
        for item_id, data in consumables.items():
            if isinstance(data, dict):
                actual = data.get('actual', 0)
                limit = data.get('limit', 0)
                charge = data.get('charge', 0)
                
                if actual > limit:
                    result.append({
                        "room_number": verification.room_number,
                        "checkout_date": verification.checkout.checkout_date.isoformat() if verification.checkout and verification.checkout.checkout_date else None,
                        "item_id": item_id,
                        "consumed": actual - limit,
                        "chargeable": charge > 0,
                        "charge_amount": float(charge)
                    })
    
    return {"minibar_consumption": result, "total": len(result)}


@router.get("/housekeeping/lost-found")
@apply_api_optimizations
def get_lost_found_register(
    status: Optional[str] = Query(None, description="Filter by status: found, claimed, disposed"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Lost & Found Register: Items left behind by guests"""
    try:
        from app.models.lost_found import LostFound
        
        query = db.query(LostFound).options(
            joinedload(LostFound.employee)
        )
        
        if status:
            query = query.filter(LostFound.status == status)
        
        if start_date:
            query = query.filter(LostFound.found_date >= start_date)
        if end_date:
            query = query.filter(LostFound.found_date <= end_date)
        
        total = query.count()
        items = query.order_by(LostFound.found_date.desc(), LostFound.created_at.desc()).offset(skip).limit(limit).all()
        
        result = []
        for item in items:
            result.append({
                "id": item.id,
                "item_description": item.item_description,
                "found_date": item.found_date.isoformat() if item.found_date else None,
                "found_by": item.found_by,
                "found_by_employee": item.employee.name if item.employee else None,
                "room_number": item.room_number,
                "location": item.location,
                "status": item.status,
                "claimed_by": item.claimed_by,
                "claimed_date": item.claimed_date.isoformat() if item.claimed_date else None,
                "claimed_contact": item.claimed_contact,
                "notes": item.notes,
                "image_url": item.image_url,
                "created_at": item.created_at.isoformat() if item.created_at else None
            })
        
        return {
            "lost_found_items": result,
            "total": total
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating lost & found report: {str(e)}")


@router.get("/housekeeping/maintenance-tickets")
@apply_api_optimizations
def get_maintenance_ticket_log(
    status: Optional[str] = Query(None, description="Filter by status: pending, in_progress, completed"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Maintenance Ticket Log: Status of repairs"""
    # Note: Requires MaintenanceTicket model - creating placeholder response
    # This would need a new model: MaintenanceTicket(id, room_number, issue_description, reported_date, status, assigned_to, completed_date)
    
    return {
        "message": "Maintenance Ticket model not yet implemented",
        "tickets": [],
        "total": 0
    }


@router.get("/housekeeping/asset-audit")
@apply_api_optimizations
def get_asset_audit_report(
    location: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Asset Audit Report: Fixed Assets mapped to locations vs actually found"""
    # Get fixed assets
    query = db.query(InventoryItem).filter(
        InventoryItem.is_asset_fixed == True
    ).options(
        joinedload(InventoryItem.category)
    )
    
    if location:
        query = query.filter(InventoryItem.location == location)
    
    assets = query.offset(skip).limit(limit).all()
    
    result = []
    for asset in assets:
        # Check AssetMapping for location
        mapped_location = getattr(asset, 'mapped_location', asset.location)
        actual_location = getattr(asset, 'actual_location', None)  # From audit
        
        # Get location_id if location exists
        location_id = None
        if asset.location:
            from app.models.inventory import Location
            location_obj = db.query(Location).filter(Location.name == asset.location).first()
            if location_obj:
                location_id = location_obj.id
        
        result.append({
            "asset_id": asset.id,
            "asset_name": asset.name,
            "asset_code": asset.item_code,
            "mapped_location": mapped_location,
            "actual_location": actual_location,
            "location": asset.location,
            "location_id": location_id,
            "status": "Match" if mapped_location == actual_location else "Mismatch",
            "category": asset.category.name if asset.category else "N/A"
        })
    
    return {"asset_audit": result, "total": len(result)}


# ============================================
# 5. 💰 ACCOUNTS & GST REPORTS (Already exists in gst_reports.py)
# ============================================
# These are already implemented in app/api/gst_reports.py
# Just adding reference endpoints here


# ============================================
# 6. 🛡️ SECURITY & HR REPORTS
# ============================================

@router.get("/security/visitor-log")
@apply_api_optimizations
def get_visitor_log(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=10000),
    db: Session = Depends(get_db)
):
    """Visitor Log: Non-resident guests entering premises (Based on check-in/checkout data)"""
    try:
        result = []
        
        # Get all checkouts (guests who visited and left)
        checkout_query = db.query(Checkout).options(
            joinedload(Checkout.booking).joinedload(Booking.booking_rooms).joinedload(BookingRoom.room),
            joinedload(Checkout.package_booking).joinedload(PackageBooking.rooms).joinedload(PackageBookingRoom.room)
        )
        
        if start_date:
            checkout_query = checkout_query.filter(func.date(Checkout.checkout_date) >= start_date)
        if end_date:
            checkout_query = checkout_query.filter(func.date(Checkout.checkout_date) <= end_date)
        
        checkouts = checkout_query.order_by(Checkout.checkout_date.desc()).all()
        
        for checkout in checkouts:
            # Get booking details
            booking = None
            pkg_booking = None
            room_numbers = []
            check_in_date = None
            check_out_date = None
            
            if checkout.booking_id:
                booking = db.query(Booking).options(
                    joinedload(Booking.booking_rooms).joinedload(BookingRoom.room)
                ).filter(Booking.id == checkout.booking_id).first()
                if booking:
                    room_numbers = [br.room.number for br in booking.booking_rooms if br.room and br.room.number]
                    check_in_date = booking.check_in
                    check_out_date = booking.check_out
            
            if checkout.package_booking_id:
                pkg_booking = db.query(PackageBooking).options(
                    joinedload(PackageBooking.rooms).joinedload(PackageBookingRoom.room)
                ).filter(PackageBooking.id == checkout.package_booking_id).first()
                if pkg_booking:
                    room_numbers = [pbr.room.number for pbr in pkg_booking.rooms if pbr.room and pbr.room.number]
                    check_in_date = pkg_booking.check_in
                    check_out_date = pkg_booking.check_out
            
            # Get guest details
            guest_name = checkout.guest_name or "N/A"
            guest_mobile = None
            guest_email = None
            
            if booking:
                guest_mobile = booking.guest_mobile
                guest_email = booking.guest_email
            elif pkg_booking:
                guest_mobile = pkg_booking.guest_mobile
                guest_email = pkg_booking.guest_email
            
            result.append({
                "visitor_name": guest_name,
                "visitor_mobile": guest_mobile or "-",
                "visitor_email": guest_email or "-",
                "purpose": "Guest Stay",
                "time_in": check_in_date.isoformat() if check_in_date else None,
                "time_out": checkout.checkout_date.isoformat() if checkout.checkout_date else None,
                "room_visited": ", ".join(room_numbers) if room_numbers else checkout.room_number or "N/A",
                "host_name": "Resort Guest",
                "checkout_id": checkout.id,
                "booking_type": "Regular" if booking else ("Package" if pkg_booking else "N/A"),
                "duration_days": (check_out_date - check_in_date).days if check_in_date and check_out_date else None
            })
        
        # Also include service requests (visitors for services)
        service_query = db.query(AssignedService).options(
            joinedload(AssignedService.room),
            joinedload(AssignedService.employee),
            joinedload(AssignedService.service)
        )
        
        if start_date:
            service_query = service_query.filter(func.date(AssignedService.assigned_at) >= start_date)
        if end_date:
            service_query = service_query.filter(func.date(AssignedService.assigned_at) <= end_date)
        
        services = service_query.all()
        
        for service in services:
            if service.room:
                # Get guest from room booking
                today = date.today()
                booking = db.query(Booking).join(BookingRoom).filter(
                    and_(
                        BookingRoom.room_id == service.room.id,
                        Booking.check_in <= today,
                        Booking.check_out > today
                    )
                ).first()
                
                if booking:
                    result.append({
                        "visitor_name": booking.guest_name or "Service Visitor",
                        "visitor_mobile": booking.guest_mobile or "-",
                        "visitor_email": booking.guest_email or "-",
                        "purpose": f"Service: {service.service.name if service.service else 'N/A'}",
                        "time_in": service.assigned_at.isoformat() if service.assigned_at else None,
                        "time_out": None,
                        "room_visited": service.room.number if service.room else "N/A",
                        "host_name": booking.guest_name or "Guest",
                        "checkout_id": None,
                        "booking_type": "Service Request",
                        "duration_days": None
                    })
        
        # Apply skip and limit
        total = len(result)
        result = result[skip:skip+limit]
        
        return {
            "visitors": result,
            "total": total,
            "showing": len(result),
            "date_range": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            }
        }
    except Exception as e:
        import traceback
        print(f"Error in visitor-log report: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error generating visitor log: {str(e)}")


@router.get("/security/key-card-audit")
@apply_api_optimizations
def get_key_card_audit(
    room_number: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=10000),
    db: Session = Depends(get_db)
):
    """Key Card Audit: Who opened which room? (Based on check-in/checkout and service assignments)"""
    try:
        result = []
        
        # Get check-ins (room access events)
        booking_query = db.query(Booking).options(
            joinedload(Booking.booking_rooms).joinedload(BookingRoom.room),
            joinedload(Booking.user)
        )
        
        if room_number:
            booking_query = booking_query.join(BookingRoom).join(Room).filter(Room.number == room_number)
        
        if start_date:
            booking_query = booking_query.filter(Booking.check_in >= start_date)
        if end_date:
            booking_query = booking_query.filter(Booking.check_in <= end_date)
        
        bookings = booking_query.filter(
            func.lower(func.coalesce(Booking.status, '')).in_(['checked-in', 'checked_in', 'checked in', 'checked-out', 'checked_out', 'checkedout'])
        ).order_by(Booking.check_in.desc()).all()
        
        for booking in bookings:
            for br in booking.booking_rooms:
                if br.room:
                    # Get employee who checked in (from user if available)
                    staff_name = "Front Desk"
                    if booking.user:
                        staff_name = booking.user.name or booking.user.email or "Front Desk"
                    
                    result.append({
                        "room_number": br.room.number,
                        "staff_name": staff_name,
                        "access_time": booking.check_in.isoformat() if booking.check_in else None,
                        "access_type": "Check-in",
                        "guest_name": booking.guest_name,
                        "card_number": f"BK-{str(booking.id).zfill(6)}",
                        "booking_id": booking.id,
                        "status": booking.status
                    })
        
        # Get package bookings
        pkg_query = db.query(PackageBooking).options(
            joinedload(PackageBooking.rooms).joinedload(PackageBookingRoom.room),
            joinedload(PackageBooking.user)
        )
        
        if room_number:
            pkg_query = pkg_query.join(PackageBookingRoom).join(Room).filter(Room.number == room_number)
        
        if start_date:
            pkg_query = pkg_query.filter(PackageBooking.check_in >= start_date)
        if end_date:
            pkg_query = pkg_query.filter(PackageBooking.check_in <= end_date)
        
        pkg_bookings = pkg_query.filter(
            func.lower(func.coalesce(PackageBooking.status, '')).in_(['checked-in', 'checked_in', 'checked in', 'checked-out', 'checked_out', 'checkedout'])
        ).order_by(PackageBooking.check_in.desc()).all()
        
        for pkg_booking in pkg_bookings:
            for pbr in pkg_booking.rooms:
                if pbr.room:
                    staff_name = "Front Desk"
                    if pkg_booking.user:
                        staff_name = pkg_booking.user.name or pkg_booking.user.email or "Front Desk"
                    
                    result.append({
                        "room_number": pbr.room.number,
                        "staff_name": staff_name,
                        "access_time": pkg_booking.check_in.isoformat() if pkg_booking.check_in else None,
                        "access_type": "Check-in",
                        "guest_name": pkg_booking.guest_name,
                        "card_number": f"PK-{str(pkg_booking.id).zfill(6)}",
                        "booking_id": pkg_booking.id,
                        "status": pkg_booking.status
                    })
        
        # Get service assignments (staff accessing rooms for services)
        service_query = db.query(AssignedService).options(
            joinedload(AssignedService.room),
            joinedload(AssignedService.employee),
            joinedload(AssignedService.service)
        )
        
        if room_number:
            service_query = service_query.join(Room).filter(Room.number == room_number)
        
        if start_date:
            service_query = service_query.filter(func.date(AssignedService.assigned_at) >= start_date)
        if end_date:
            service_query = service_query.filter(func.date(AssignedService.assigned_at) <= end_date)
        
        services = service_query.order_by(AssignedService.assigned_at.desc()).all()
        
        for service in services:
            if service.room and service.employee:
                result.append({
                    "room_number": service.room.number,
                    "staff_name": service.employee.name if service.employee else "Staff",
                    "access_time": service.assigned_at.isoformat() if service.assigned_at else None,
                    "access_type": f"Service: {service.service.name if service.service else 'N/A'}",
                    "guest_name": "Service Access",
                    "card_number": f"SRV-{service.id}",
                    "booking_id": None,
                    "status": service.status or "N/A"
                })
        
        # Get checkouts (room access end)
        checkout_query = db.query(Checkout).options(
            joinedload(Checkout.booking),
            joinedload(Checkout.package_booking)
        )
        
        if room_number:
            checkout_query = checkout_query.filter(Checkout.room_number == room_number)
        
        if start_date:
            checkout_query = checkout_query.filter(func.date(Checkout.checkout_date) >= start_date)
        if end_date:
            checkout_query = checkout_query.filter(func.date(Checkout.checkout_date) <= end_date)
        
        checkouts = checkout_query.order_by(Checkout.checkout_date.desc()).all()
        
        for checkout in checkouts:
            booking = checkout.booking
            pkg_booking = checkout.package_booking
            
            if booking:
                for br in booking.booking_rooms:
                    if br.room:
                        result.append({
                            "room_number": br.room.number,
                            "staff_name": "Front Desk",
                            "access_time": checkout.checkout_date.isoformat() if checkout.checkout_date else None,
                            "access_type": "Check-out",
                            "guest_name": checkout.guest_name or booking.guest_name,
                            "card_number": f"BK-{str(booking.id).zfill(6)}",
                            "booking_id": booking.id,
                            "status": "Checked Out"
                        })
            
            if pkg_booking:
                for pbr in pkg_booking.rooms:
                    if pbr.room:
                        result.append({
                            "room_number": pbr.room.number,
                            "staff_name": "Front Desk",
                            "access_time": checkout.checkout_date.isoformat() if checkout.checkout_date else None,
                            "access_type": "Check-out",
                            "guest_name": checkout.guest_name or pkg_booking.guest_name,
                            "card_number": f"PK-{str(pkg_booking.id).zfill(6)}",
                            "booking_id": pkg_booking.id,
                            "status": "Checked Out"
                        })
        
        # Sort by access time
        result.sort(key=lambda x: x.get("access_time") or "", reverse=True)
        
        # Apply skip and limit
        total = len(result)
        result = result[skip:skip+limit]
        
        return {
            "access_logs": result,
            "total": total,
            "showing": len(result),
            "date_range": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            }
        }
    except Exception as e:
        import traceback
        print(f"Error in key-card-audit report: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error generating key card audit: {str(e)}")


@router.get("/hr/staff-attendance")
@apply_api_optimizations
def get_staff_attendance_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    employee_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=10000),
    db: Session = Depends(get_db)
):
    """Staff Attendance: Shift In/Out times (Based on WorkingLog and service assignments)"""
    try:
        result = []
        
        # Get working logs
        query = db.query(WorkingLog).options(
            joinedload(WorkingLog.employee)
        )
        
        if employee_id:
            query = query.filter(WorkingLog.employee_id == employee_id)
        if start_date:
            query = query.filter(WorkingLog.date >= start_date)
        if end_date:
            query = query.filter(WorkingLog.date <= end_date)
        
        logs = query.order_by(WorkingLog.date.desc(), WorkingLog.check_in_time.desc()).all()
        
        for log in logs:
            hours_worked = 0.0
            check_in_datetime = None
            check_out_datetime = None
            
            if log.check_in_time and log.check_out_time:
                # Calculate hours
                check_in = datetime.combine(log.date, log.check_in_time)
                check_out = datetime.combine(log.date, log.check_out_time)
                if check_out > check_in:
                    hours_worked = (check_out - check_in).total_seconds() / 3600
                check_in_datetime = check_in
                check_out_datetime = check_out
            elif log.check_in_time:
                check_in_datetime = datetime.combine(log.date, log.check_in_time)
            elif log.check_out_time:
                check_out_datetime = datetime.combine(log.date, log.check_out_time)
            
            # Get additional activity from service assignments
            service_count = db.query(AssignedService).filter(
                and_(
                    AssignedService.employee_id == log.employee_id,
                    func.date(AssignedService.assigned_at) == log.date
                )
            ).count()
            
            result.append({
                "employee_name": log.employee.name if log.employee else "-",
                "employee_id": log.employee_id,
                "employee_code": f"EMP-{log.employee.id}" if log.employee else None,
                "date": log.date.isoformat() if log.date else None,
                "check_in_time": check_in_datetime.isoformat() if check_in_datetime else None,
                "check_out_time": check_out_datetime.isoformat() if check_out_datetime else None,
                "hours_worked": round(hours_worked, 2) if hours_worked > 0 else None,
                "location": log.location or "Office",
                "services_assigned": service_count,
                "status": "Present" if log.check_in_time else "Absent"
            })
        
        # Apply skip and limit
        total = len(result)
        result = result[skip:skip+limit]
        
        return {
            "attendance_logs": result,
            "total": total,
            "showing": len(result),
            "date_range": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            }
        }
    except Exception as e:
        import traceback
        print(f"Error in staff-attendance report: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error generating staff attendance report: {str(e)}")


@router.get("/hr/payroll-register")
@apply_api_optimizations
def get_payroll_register(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Payroll Register: Salary calculation (Basic + OT - Deductions)"""
    try:
        if not year:
            year = date.today().year
        if not month:
            month = date.today().month
        
        # Calculate month boundaries
        from calendar import monthrange
        _, days_in_month = monthrange(year, month)
        month_start = date(year, month, 1)
        month_end = date(year, month, days_in_month)
        
        # Get all employees (process all, then apply skip/limit to results)
        employees = db.query(Employee).all()
        
        result = []
        for employee in employees:
            # Get attendance for the month
            attendance_count = db.query(Attendance).filter(
                and_(
                    Attendance.employee_id == employee.id,
                    Attendance.date >= month_start,
                    Attendance.date <= month_end,
                    Attendance.status == "Present"
                )
            ).count()
            
            # Get working logs for OT calculation
            working_logs = db.query(WorkingLog).filter(
                and_(
                    WorkingLog.employee_id == employee.id,
                    WorkingLog.date >= month_start,
                    WorkingLog.date <= month_end
                )
            ).all()
            
            total_hours = 0.0
            for log in working_logs:
                if log.check_in_time and log.check_out_time:
                    try:
                        check_in_dt = datetime.combine(log.date, log.check_in_time)
                        check_out_dt = datetime.combine(log.date, log.check_out_time)
                        if check_out_dt > check_in_dt:
                            hours = (check_out_dt - check_in_dt).total_seconds() / 3600
                            total_hours += hours
                    except:
                        pass
            
            # Calculate salary components
            basic_salary = float(employee.salary or 0)
            # Assuming 8 hours per day standard
            standard_hours = attendance_count * 8
            ot_hours = max(0, total_hours - standard_hours)
            hourly_rate = (basic_salary / (30 * 8)) if (30 * 8) > 0 else 0
            ot_amount = (ot_hours * hourly_rate) * 1.5  # 1.5x for OT
            
            # Deductions from Leave model (handle date ranges)
            leaves = db.query(Leave).filter(
                and_(
                    Leave.employee_id == employee.id,
                    Leave.from_date <= month_end,
                    Leave.to_date >= month_start,
                    Leave.status == "approved",
                    Leave.leave_type == "Unpaid"
                )
            ).all()
            
            # Calculate leave days in this month
            leave_days = 0
            for leave in leaves:
                overlap_start = max(leave.from_date, month_start)
                overlap_end = min(leave.to_date, month_end)
                if overlap_end >= overlap_start:
                    leave_days += (overlap_end - overlap_start).days + 1
            
            leave_deduction = (leave_days * (basic_salary / 30)) if basic_salary > 0 else 0
            other_deductions = 0.0
            net_salary = max(0, basic_salary + ot_amount - leave_deduction - other_deductions)
            
            result.append({
                "employee_name": employee.name or "N/A",
                "employee_id": employee.id,
                "employee_code": f"EMP-{employee.id}",
                "role": employee.role.name if hasattr(employee.role, 'name') else (employee.role if isinstance(employee.role, str) else "N/A"),
                "basic_salary": basic_salary,
                "attendance_days": attendance_count,
                "total_hours": round(total_hours, 2),
                "ot_hours": round(ot_hours, 2),
                "ot_amount": round(ot_amount, 2),
                "leave_days": leave_days,
                "leave_deduction": round(leave_deduction, 2),
                "other_deductions": other_deductions,
                "net_salary": round(net_salary, 2),
                "month": month,
                "year": year
            })
        
        # Sort by employee name
        result.sort(key=lambda x: x.get("employee_name", ""))
        
        total_payroll = sum(r["net_salary"] for r in result)
        
        # Apply skip and limit
        total = len(result)
        result = result[skip:skip+limit]
        
        return {
            "payroll": result,
            "total": total,
            "showing": len(result),
            "total_payroll": round(total_payroll, 2),
            "month": month,
            "year": year,
            "month_name": date(year, month, 1).strftime("%B %Y")
        }
    except Exception as e:
        import traceback
        print(f"Error in payroll-register report: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error generating payroll register: {str(e)}")


# ============================================
# 7. 📊 MANAGEMENT DASHBOARD
# ============================================

@router.get("/management/dashboard")
@apply_api_optimizations
def get_management_dashboard(
    report_date: Optional[date] = Query(None, description="Date for dashboard (default: today)"),
    db: Session = Depends(get_db)
):
    """Management Dashboard: ADR, RevPAR, Food Cost %, Occupancy %"""
    if not report_date:
        report_date = date.today()
    
    # Total rooms
    total_rooms = db.query(Room).count()
    
    # Occupied rooms
    occupied_bookings = db.query(Booking).filter(
        and_(
            Booking.check_in <= report_date,
            Booking.check_out > report_date,
            Booking.status.in_(["checked-in", "booked"])
        )
    ).count()
    
    occupied_packages = db.query(PackageBooking).filter(
        and_(
            PackageBooking.check_in <= report_date,
            PackageBooking.check_out > report_date,
            PackageBooking.status.in_(["checked-in", "booked"])
        )
    ).count()
    
    occupied_rooms = occupied_bookings + occupied_packages
    occupancy_percentage = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
    
    # Room revenue for the date
    room_revenue = db.query(func.sum(Checkout.room_total)).filter(
        func.date(Checkout.checkout_date) == report_date
    ).scalar() or 0
    
    # ADR (Average Daily Rate)
    checkouts_count = db.query(Checkout).filter(
        func.date(Checkout.checkout_date) == report_date
    ).count()
    
    adr = (room_revenue / checkouts_count) if checkouts_count > 0 else 0
    
    # RevPAR (Revenue Per Available Room)
    revpar = (room_revenue / total_rooms) if total_rooms > 0 else 0
    
    # Food revenue
    food_revenue = db.query(func.sum(Checkout.food_total)).filter(
        func.date(Checkout.checkout_date) == report_date
    ).scalar() or 0
    
    # Food cost (from inventory consumption)
    # This would require tracking food cost separately
    # For now, using a placeholder
    food_cost = 0  # Calculate from inventory consumption for food items
    
    food_cost_percentage = (food_cost / food_revenue * 100) if food_revenue > 0 else 0
    
    return {
        "date": report_date.isoformat(),
        "kpis": {
            "adr": round(float(adr), 2),
            "revpar": round(float(revpar), 2),
            "occupancy_percentage": round(occupancy_percentage, 2),
            "food_cost_percentage": round(food_cost_percentage, 2)
        },
        "details": {
            "total_rooms": total_rooms,
            "occupied_rooms": occupied_rooms,
            "room_revenue": float(room_revenue),
            "food_revenue": float(food_revenue),
            "checkouts_count": checkouts_count
        }
    }
