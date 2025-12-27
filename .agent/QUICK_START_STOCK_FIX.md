# Quick Start: Fix Stock Discrepancies

## Immediate Actions

### 1. Check Current Discrepancies (Safe - Read Only)
```bash
curl -X POST "http://localhost:8000/api/inventory/reconcile-stock?fix_discrepancies=false" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**What it does**: Shows all items where global stock ≠ sum of location stocks

**Example Output**:
```json
{
  "discrepancies_found": 5,
  "items_with_issues": [
    {
      "item_name": "Towel",
      "global_stock": 100,
      "total_location_stock": 95,
      "discrepancy": 5
    }
  ]
}
```

---

### 2. Fix All Discrepancies (Automatic)
```bash
curl -X POST "http://localhost:8000/api/inventory/reconcile-stock?fix_discrepancies=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**What it does**: 
- Adjusts global stock to match sum of location stocks
- Creates adjustment transactions for audit trail
- Returns report of all fixes made

**Safe to run**: Yes - uses location stocks as source of truth

---

### 3. Audit Specific Item
```bash
curl -X GET "http://localhost:8000/api/inventory/stock-audit?item_id=45" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**What it does**:
- Shows transaction history
- Calculates expected stock from transactions
- Compares global vs location vs calculated stock
- Lists all locations with this item

---

### 4. Validate Room Before Checkout
```bash
curl -X POST "http://localhost:8000/api/inventory/validate-checkout-stock?room_number=101" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**What it does**:
- Checks for negative stock
- Validates current stock vs issued stock
- Warns of any issues before checkout

---

## Common Scenarios

### Scenario 1: "Stock shows wrong quantity"
```bash
# Step 1: Audit the item
GET /api/inventory/stock-audit?item_id=<ITEM_ID>

# Step 2: Check transaction history in response
# Look for unexpected transactions or missing entries

# Step 3: Run reconciliation
POST /api/inventory/reconcile-stock?fix_discrepancies=true
```

---

### Scenario 2: "Checkout shows negative stock"
```bash
# Step 1: Validate the room first
POST /api/inventory/validate-checkout-stock?room_number=<ROOM>

# Step 2: Check response for issues
# Fix any negative stock or over-issued items

# Step 3: If issues found, run reconciliation
POST /api/inventory/reconcile-stock?fix_discrepancies=true

# Step 4: Validate again
POST /api/inventory/validate-checkout-stock?room_number=<ROOM>
```

---

### Scenario 3: "Global stock doesn't match locations"
```bash
# This is the main fix - just run reconciliation
POST /api/inventory/reconcile-stock?fix_discrepancies=true

# Verify specific items if needed
GET /api/inventory/stock-audit?item_id=<ITEM_ID>
```

---

## Understanding the Response

### Reconciliation Report
```json
{
  "total_items_checked": 150,      // Total inventory items
  "discrepancies_found": 12,       // Items with issues
  "discrepancies_fixed": 12,       // Items corrected (if fix=true)
  "items_with_issues": [           // Details of each issue
    {
      "item_name": "Soap",
      "global_stock": 50,            // Current global stock
      "total_location_stock": 48,    // Sum of all locations
      "discrepancy": 2,              // Difference
      "locations": [                 // Where the stock is
        {
          "location_name": "Warehouse",
          "quantity": 30
        },
        {
          "location_name": "Room 101",
          "quantity": 18
        }
      ],
      "action_taken": "Adjusted global stock from 50 to 48"
    }
  ]
}
```

### Stock Audit Report
```json
{
  "item_name": "Towel",
  "global_stock": 95,                    // Current global stock
  "calculated_from_transactions": 95,    // What it should be based on history
  "total_location_stock": 95,            // Sum of all locations
  "discrepancies": {
    "global_vs_calculated": 0,           // Should be 0
    "global_vs_locations": 0,            // Should be 0
    "calculated_vs_locations": 0         // Should be 0
  },
  "recent_transactions": [               // Last 10 transactions
    {
      "type": "return",
      "quantity": 6,
      "reference": "RETURN-CHK-123",
      "notes": "Unused items returned from Room 101"
    }
  ]
}
```

---

## Troubleshooting

### Issue: "Discrepancies keep appearing"
**Cause**: Old checkout logic creating new discrepancies
**Solution**: 
1. Restart server to load new code
2. Run reconciliation to fix existing data
3. Test new checkout flow

### Issue: "Negative stock in room"
**Cause**: Stock was consumed but not properly recorded
**Solution**:
1. Validate room: `POST /api/inventory/validate-checkout-stock?room_number=<ROOM>`
2. Check issues in response
3. Run reconciliation: `POST /api/inventory/reconcile-stock?fix_discrepancies=true`

### Issue: "Can't find source location for return"
**Cause**: Stock was issued before tracking was implemented
**Solution**: System will find warehouse automatically as fallback

---

## Best Practices

### Daily
- Run reconciliation report (fix=false) to monitor
- Check for any new discrepancies

### Weekly  
- Run full reconciliation (fix=true)
- Audit high-value items

### Before Month-End
- Run full reconciliation
- Generate stock audit report
- Review transaction logs

### Before Checkout
- Always validate room stock first
- Fix any issues before processing checkout
- Verify global stock after checkout

---

## API Endpoints Summary

| Endpoint | Method | Purpose | Safe? |
|----------|--------|---------|-------|
| `/api/inventory/reconcile-stock?fix_discrepancies=false` | POST | Report discrepancies | ✅ Yes |
| `/api/inventory/reconcile-stock?fix_discrepancies=true` | POST | Fix discrepancies | ✅ Yes* |
| `/api/inventory/stock-audit` | GET | Audit all items | ✅ Yes |
| `/api/inventory/stock-audit?item_id=X` | GET | Audit specific item | ✅ Yes |
| `/api/inventory/validate-checkout-stock?room_number=X` | POST | Validate room | ✅ Yes |

*Safe because it uses location stocks as source of truth and creates audit trail

---

## Need Help?

1. Check server logs for detailed messages
2. Run stock audit on affected item
3. Review transaction history
4. Use reconciliation tool to fix

All operations are logged and reversible through transaction records.
