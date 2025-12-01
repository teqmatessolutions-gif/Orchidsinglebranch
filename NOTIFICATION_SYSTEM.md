# Notification System Implementation

## Overview
A comprehensive notification system has been implemented to provide real-time notifications for all major events in the resort management system.

## Features

### Notification Types
The system supports notifications for:
- **Services**: Creation, assignment, status changes, employee reassignment
- **Bookings**: New bookings, status updates, check-in/check-out
- **Packages**: New packages, package bookings
- **Inventory**: Item updates, low stock alerts
- **Expenses**: New expense entries
- **Food Orders**: New orders, status changes

### User Interface
- **Notification Bell**: Located in the dashboard header with unread count badge
- **Notification Panel**: Slide-out panel showing all notifications
- **Features**:
  - Mark individual notifications as read
  - Mark all as read
  - Delete individual notifications
  - Clear all notifications
  - Auto-refresh every 30 seconds
  - Color-coded by notification type
  - Time-based display (e.g., "5m ago", "2h ago")

## Implementation Details

### Backend Components

#### 1. Database Model (`app/models/notification.py`)
```python
class Notification(Base):
    id: int
    type: NotificationType (enum)
    title: str
    message: str
    is_read: bool
    created_at: datetime
    read_at: datetime (optional)
    entity_type: str (optional)
    entity_id: int (optional)
```

#### 2. API Endpoints (`app/api/notification.py`)
- `GET /api/notifications` - Get all notifications
- `GET /api/notifications/unread-count` - Get unread count
- `GET /api/notifications/{id}` - Get specific notification
- `POST /api/notifications` - Create notification
- `PUT /api/notifications/{id}/read` - Mark as read
- `PUT /api/notifications/mark-all-read` - Mark all as read
- `DELETE /api/notifications/{id}` - Delete notification
- `DELETE /api/notifications/clear-all` - Clear all

#### 3. CRUD Functions (`app/curd/notification.py`)
Helper functions for creating notifications:
- `notify_service_created()`
- `notify_service_assigned()`
- `notify_service_status_changed()`
- `notify_booking_created()`
- `notify_booking_status_changed()`
- `notify_package_created()`
- `notify_package_booked()`
- `notify_inventory_updated()`
- `notify_inventory_low_stock()`
- `notify_expense_added()`
- `notify_food_order_created()`
- `notify_food_order_status_changed()`

### Frontend Components

#### 1. Notification Context (`src/contexts/NotificationContext.jsx`)
Provides global notification state management:
- `notifications` - Array of all notifications
- `unreadCount` - Number of unread notifications
- `showPanel` - Panel visibility state
- `addNotification()` - Add new notification
- `markAsRead()` - Mark notification as read
- `markAllAsRead()` - Mark all as read
- `deleteNotification()` - Delete notification
- `clearAll()` - Clear all notifications

#### 2. Notification Bell (`NotificationBell` component)
- Shows bell icon with unread count badge
- Opens notification panel on click
- Located in dashboard header

#### 3. Notification Panel (`NotificationPanel` component)
- Slide-out panel from right side
- Lists all notifications with icons and colors
- Actions: mark as read, delete
- Bulk actions: mark all read, clear all

## Usage

### Creating Notifications from Backend

Example: When a new service is created
```python
from app.curd import notification as notification_crud

# After creating a service
notification_crud.notify_service_created(
    db=db,
    service_name=service.name,
    service_id=service.id
)
```

Example: When a food order status changes
```python
notification_crud.notify_food_order_status_changed(
    db=db,
    room_number=order.room.number,
    status=new_status,
    order_id=order.id
)
```

### Integration Points

To add notifications to existing features, add notification creation calls in:

1. **Services** (`app/api/service.py`):
   - After creating service → `notify_service_created()`
   - After assigning service → `notify_service_assigned()`
   - After status update → `notify_service_status_changed()`

2. **Bookings** (`app/api/booking.py`):
   - After creating booking → `notify_booking_created()`
   - After status update → `notify_booking_status_changed()`

3. **Packages** (`app/api/packages.py`):
   - After creating package → `notify_package_created()`
   - After package booking → `notify_package_booked()`

4. **Inventory** (`app/api/inventory.py`):
   - After item update → `notify_inventory_updated()`
   - When stock is low → `notify_inventory_low_stock()`

5. **Expenses** (`app/api/expenses.py`):
   - After adding expense → `notify_expense_added()`

6. **Food Orders** (`app/api/food_orders.py`):
   - After creating order → `notify_food_order_created()`
   - After status change → `notify_food_order_status_changed()`

## Database Migration

Run the migration to create the notifications table:
```bash
cd ResortApp
python migrations/add_notifications_table.py
```

Or the table will be created automatically when the server starts (via `Base.metadata.create_all()`).

## Configuration

### Polling Interval
Notifications are fetched every 30 seconds. To change this, edit `NotificationContext.jsx`:
```javascript
const interval = setInterval(fetchNotifications, 30000); // 30 seconds
```

### Auto-dismiss
Toast-style notifications auto-dismiss after 5 seconds. To change:
```javascript
setTimeout(() => {
  removeNotification(notification.id);
}, 5000); // 5 seconds
```

## Styling

Notification colors are defined in `NotificationContext.jsx`:
```javascript
const colorMap = {
  service: 'bg-blue-500',
  booking: 'bg-purple-500',
  package: 'bg-indigo-500',
  inventory: 'bg-orange-500',
  expense: 'bg-red-500',
  food_order: 'bg-green-500',
};
```

## Future Enhancements

Potential improvements:
1. **WebSocket Support**: Real-time notifications without polling
2. **Push Notifications**: Browser push notifications
3. **Email Notifications**: Send important notifications via email
4. **Notification Preferences**: Allow users to customize which notifications they receive
5. **Notification History**: Archive old notifications
6. **Sound Alerts**: Audio notification for important events
7. **Desktop Notifications**: System-level notifications
8. **Notification Categories**: Filter notifications by type
9. **Priority Levels**: High/Medium/Low priority notifications
10. **Action Buttons**: Quick actions from notifications (e.g., "View Order", "Approve Request")

## Troubleshooting

### Notifications not appearing
1. Check if backend server is running
2. Verify notification API endpoints are accessible
3. Check browser console for errors
4. Ensure NotificationProvider wraps the app in App.js

### Unread count not updating
1. Check if `fetchNotifications()` is being called
2. Verify API response includes `is_read` field
3. Check network tab for API calls

### Panel not opening
1. Verify NotificationBell is rendered
2. Check if `setShowPanel` is being called
3. Inspect z-index conflicts with other UI elements
