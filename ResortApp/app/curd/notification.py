from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from typing import List, Optional
from app.models.notification import Notification, NotificationType
from app.schemas.notification import NotificationCreate

def create_notification(
    db: Session,
    notification: NotificationCreate
) -> Notification:
    """Create a new notification"""
    db_notification = Notification(
        type=notification.type,
        title=notification.title,
        message=notification.message,
        entity_type=notification.entity_type,
        entity_id=notification.entity_id
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

def get_notifications(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    unread_only: bool = False
) -> List[Notification]:
    """Get all notifications, optionally filtered by read status"""
    query = db.query(Notification)
    if unread_only:
        query = query.filter(Notification.is_read == False)
    return query.order_by(desc(Notification.created_at)).offset(skip).limit(limit).all()

def get_notification(db: Session, notification_id: int) -> Optional[Notification]:
    """Get a specific notification by ID"""
    return db.query(Notification).filter(Notification.id == notification_id).first()

def mark_notification_as_read(db: Session, notification_id: int) -> Optional[Notification]:
    """Mark a notification as read"""
    notification = get_notification(db, notification_id)
    if notification:
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        db.commit()
        db.refresh(notification)
    return notification

def mark_all_as_read(db: Session) -> int:
    """Mark all notifications as read"""
    count = db.query(Notification).filter(Notification.is_read == False).update({
        "is_read": True,
        "read_at": datetime.utcnow()
    })
    db.commit()
    return count

def delete_notification(db: Session, notification_id: int) -> bool:
    """Delete a specific notification"""
    notification = get_notification(db, notification_id)
    if notification:
        db.delete(notification)
        db.commit()
        return True
    return False

def clear_all_notifications(db: Session) -> int:
    """Delete all notifications"""
    count = db.query(Notification).delete()
    db.commit()
    return count

def get_unread_count(db: Session) -> int:
    """Get count of unread notifications"""
    return db.query(Notification).filter(Notification.is_read == False).count()

# Helper function to create notifications for different events
def notify_service_created(db: Session, service_name: str, service_id: int):
    """Create notification for new service"""
    return create_notification(db, NotificationCreate(
        type=NotificationType.SERVICE,
        title="New Service Created",
        message=f"Service '{service_name}' has been created successfully.",
        entity_type="service",
        entity_id=service_id
    ))

def notify_service_assigned(db: Session, service_name: str, employee_name: str, room_number: str, assigned_id: int):
    """Create notification for service assignment"""
    return create_notification(db, NotificationCreate(
        type=NotificationType.SERVICE,
        title="Service Assigned",
        message=f"Service '{service_name}' assigned to {employee_name} for Room {room_number}.",
        entity_type="assigned_service",
        entity_id=assigned_id
    ))

def notify_service_status_changed(db: Session, service_name: str, status: str, assigned_id: int):
    """Create notification for service status change"""
    return create_notification(db, NotificationCreate(
        type=NotificationType.SERVICE,
        title="Service Status Updated",
        message=f"Service '{service_name}' status changed to {status}.",
        entity_type="assigned_service",
        entity_id=assigned_id
    ))

def notify_booking_created(db: Session, guest_name: str, booking_id: int):
    """Create notification for new booking"""
    return create_notification(db, NotificationCreate(
        type=NotificationType.BOOKING,
        title="New Booking Created",
        message=f"New booking created for {guest_name}.",
        entity_type="booking",
        entity_id=booking_id
    ))

def notify_booking_status_changed(db: Session, guest_name: str, status: str, booking_id: int):
    """Create notification for booking status change"""
    return create_notification(db, NotificationCreate(
        type=NotificationType.BOOKING,
        title="Booking Status Updated",
        message=f"Booking for {guest_name} status changed to {status}.",
        entity_type="booking",
        entity_id=booking_id
    ))

def notify_package_created(db: Session, package_name: str, package_id: int):
    """Create notification for new package"""
    return create_notification(db, NotificationCreate(
        type=NotificationType.PACKAGE,
        title="New Package Created",
        message=f"Package '{package_name}' has been created successfully.",
        entity_type="package",
        entity_id=package_id
    ))

def notify_package_booked(db: Session, package_name: str, guest_name: str, booking_id: int):
    """Create notification for package booking"""
    return create_notification(db, NotificationCreate(
        type=NotificationType.PACKAGE,
        title="Package Booked",
        message=f"Package '{package_name}' booked by {guest_name}.",
        entity_type="package_booking",
        entity_id=booking_id
    ))

def notify_inventory_updated(db: Session, item_name: str, action: str, item_id: int):
    """Create notification for inventory changes"""
    return create_notification(db, NotificationCreate(
        type=NotificationType.INVENTORY,
        title="Inventory Updated",
        message=f"Inventory item '{item_name}' has been {action}.",
        entity_type="inventory_item",
        entity_id=item_id
    ))

def notify_inventory_low_stock(db: Session, item_name: str, current_stock: float, item_id: int):
    """Create notification for low stock"""
    return create_notification(db, NotificationCreate(
        type=NotificationType.INVENTORY,
        title="Low Stock Alert",
        message=f"Inventory item '{item_name}' is running low (Current: {current_stock}).",
        entity_type="inventory_item",
        entity_id=item_id
    ))

def notify_expense_added(db: Session, expense_name: str, amount: float, expense_id: int):
    """Create notification for new expense"""
    return create_notification(db, NotificationCreate(
        type=NotificationType.EXPENSE,
        title="New Expense Added",
        message=f"Expense '{expense_name}' of ₹{amount:,.2f} has been recorded.",
        entity_type="expense",
        entity_id=expense_id
    ))

def notify_food_order_created(db: Session, room_number: str, order_id: int):
    """Create notification for new food order"""
    return create_notification(db, NotificationCreate(
        type=NotificationType.FOOD_ORDER,
        title="New Food Order",
        message=f"New food order received for Room {room_number}.",
        entity_type="food_order",
        entity_id=order_id
    ))

def notify_food_order_status_changed(db: Session, room_number: str, status: str, order_id: int):
    """Create notification for food order status change"""
    return create_notification(db, NotificationCreate(
        type=NotificationType.FOOD_ORDER,
        title="Food Order Status Updated",
        message=f"Food order for Room {room_number} is now {status}.",
        entity_type="food_order",
        entity_id=order_id
    ))

def notify_service_request_created(db: Session, request_type: str, room_number: str, request_id: int):
    """Create notification for new service request"""
    type_label = request_type.replace("_", " ").title()
    return create_notification(db, NotificationCreate(
        type=NotificationType.SERVICE,
        title=f"New {type_label} Request",
        message=f"{type_label} request created for Room {room_number}.",
        entity_type="service_request",
        entity_id=request_id
    ))

def notify_service_request_status_changed(db: Session, request_type: str, room_number: str, status: str, request_id: int):
    """Create notification for service request status change"""
    type_label = request_type.replace("_", " ").title()
    return create_notification(db, NotificationCreate(
        type=NotificationType.SERVICE,
        title=f"{type_label} Request Updated",
        message=f"{type_label} request for Room {room_number} is now {status}.",
        entity_type="service_request",
        entity_id=request_id
    ))
