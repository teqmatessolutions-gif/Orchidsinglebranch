# User Frontend API Configuration

## ✅ Configuration Complete!

The user frontend has been successfully configured to work with your current backend APIs.

### API Endpoints Configuration

**Backend API Base URL**: `http://localhost:8011/api`
**Media Files Base URL**: `http://localhost:8011`

### Changes Made

1. **Updated `src/utils/env.js`**:
   - Changed API base URL from `localhost:8012` to `localhost:8011`
   - Changed media base URL from `localhost:8012` to `localhost:8011`

### Running Services

| Service | URL | Port | Status |
|---------|-----|------|--------|
| Backend API | http://localhost:8011/api | 8011 | ✅ Running |
| Admin Dashboard | http://localhost:3000 | 3000 | ✅ Running |
| User Frontend | http://localhost:3002/resort | 3002 | ✅ Running |

### API Integration

The user frontend now connects to your backend for:

- **Rooms API**: `/api/rooms/` - Get available rooms
- **Packages API**: `/api/packages/` - Get packages
- **Bookings API**: `/api/bookings` - Create and manage bookings
- **Food API**: `/api/food/` - Food menu and orders
- **Services API**: `/api/services/` - Service requests
- **Media Files**: Room images, package images, etc.

### Testing the Integration

1. **Open the user frontend**: http://localhost:3002/resort
2. **Check browser console** for any API errors
3. **Test booking flow**:
   - Browse rooms
   - Select dates
   - Create a booking
   - Verify data appears in admin dashboard

### CORS Configuration

Your backend is already configured to allow requests from `localhost:3002` through the CORS middleware in `main.py`.

### Next Steps

1. **Test the booking flow** end-to-end
2. **Verify room images** are loading correctly
3. **Check package details** display properly
4. **Test form submissions** (bookings, contact forms, etc.)

### Troubleshooting

If you encounter any API errors:

1. **Check browser console** (F12) for error messages
2. **Verify backend is running** on port 8011
3. **Check CORS headers** in network tab
4. **Ensure database** is accessible

### Development Mode

The user frontend is running in development mode with:
- Hot reload enabled
- Source maps for debugging
- React DevTools support
- Detailed error messages

---

**Last Updated**: 2025-12-27
**Configuration**: Local Development
