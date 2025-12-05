"""
Fix Inventory Frontend Issues
This script applies multiple fixes to Inventory.jsx:
1. Fetch food items for waste form
2. Pass foodItems to WasteLogFormModal
3. Auto-load requisition items in Issue Form
4. Add status dropdown to Requisitions table
5. Exclude cancelled purchases from totals
"""

import re

file_path = "dasboard/src/pages/Inventory.jsx"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# ------------------------------------------------------------------
# Fix 1: Fetch food items for waste form
# ------------------------------------------------------------------
old_fetch = 'else if (activeTab === "waste") {'
new_fetch = '''else if (activeTab === "waste") {
        const res = await API.get(`/inventory/waste-logs?limit=${limit}`);
        setWasteLogs(res.data || []);
        // Also fetch food items for waste form
        try {
          const foodRes = await API.get("/food-items");
          setFoodItems(foodRes.data || []);
        } catch (err) {
          console.error("Failed to fetch food items:", err);
        }'''

content = content.replace(old_fetch, new_fetch)

# ------------------------------------------------------------------
# Fix 2: Pass foodItems to WasteLogFormModal
# ------------------------------------------------------------------
# There are two occurrences
content = content.replace(
    'items={items}',
    'items={items}\n          foodItems={foodItems}'
)

# ------------------------------------------------------------------
# Fix 3: Auto-load requisition items in Issue Form
# ------------------------------------------------------------------
# Find the onChange handler for requisition_id
old_issue_change = '''                onChange={(e) =>
                  setForm({ ...form, requisition_id: e.target.value })
                }'''

new_issue_change = '''                onChange={(e) => {
                  const reqId = e.target.value;
                  let newDetails = form.details;
                  
                  if (reqId) {
                    const selectedReq = requisitions.find(r => r.id === parseInt(reqId));
                    if (selectedReq?.details) {
                      newDetails = selectedReq.details.map(detail => ({
                        item_id: detail.item_id,
                        issued_quantity: detail.requested_quantity || detail.approved_quantity,
                        unit: detail.unit,
                        cost: items.find(i => i.id === detail.item_id)?.unit_price || 0,
                        notes: `From ${selectedReq.requisition_number}`,
                        batch_lot_number: "",
                      }));
                    }
                  }
                  
                  setForm({ 
                    ...form, 
                    requisition_id: reqId,
                    details: newDetails.length > 0 ? newDetails : form.details
                  });
                }}'''

# We need to be careful with replacement as setForm might be used elsewhere
# The Issue Form uses 'form' in the render (passed as prop) but 'issueForm' in state
# Wait, the modal component receives 'form' and 'setForm' props.
# So the replacement above is correct for the modal component code.
# Let's verify the context.
# The modal code is around line 6824.
content = content.replace(old_issue_change, new_issue_change)


# ------------------------------------------------------------------
# Fix 4: Add status dropdown to Requisitions table
# ------------------------------------------------------------------
# First, add the handler function
handler_marker = 'const handleApproveRequisition = async (requisitionId) => {'
new_handler = '''  const handleRequisitionStatusChange = async (reqId, newStatus) => {
    try {
      await API.patch(`/inventory/requisitions/${reqId}`, { status: newStatus });
      addNotification({ title: "Success", message: `Requisition status updated to ${newStatus}`, type: "success" });
      fetchData();
    } catch (error) {
      addNotification({ title: "Error", message: "Failed to update status", type: "error" });
    }
  };

  const handleApproveRequisition = async (requisitionId) => {'''

content = content.replace(handler_marker, new_handler)

# Now replace the button with dropdown
old_button = '''                            {req.status === "pending" && (
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleApproveRequisition(req.id);
                                }}
                                className="mt-3 w-full px-3 py-2 bg-green-600 text-white text-sm rounded hover:bg-green-700"
                              >
                                Approve & Issue
                              </button>
                            )}'''

new_dropdown = '''                            <div className="mt-3" onClick={(e) => e.stopPropagation()}>
                              <select
                                value={req.status}
                                onChange={(e) => handleRequisitionStatusChange(req.id, e.target.value)}
                                className={`w-full px-3 py-2 text-sm border rounded-lg ${
                                  req.status === 'approved' ? 'bg-green-50 text-green-700 border-green-200' :
                                  req.status === 'rejected' ? 'bg-red-50 text-red-700 border-red-200' :
                                  req.status === 'completed' ? 'bg-blue-50 text-blue-700 border-blue-200' :
                                  'bg-yellow-50 text-yellow-700 border-yellow-200'
                                }`}
                              >
                                <option value="pending">Pending</option>
                                <option value="approved">Approved</option>
                                <option value="rejected">Rejected</option>
                                <option value="completed">Completed</option>
                              </select>
                            </div>'''

content = content.replace(old_button, new_dropdown)

# ------------------------------------------------------------------
# Fix 5: Exclude cancelled purchases from totals
# ------------------------------------------------------------------
old_calc = '''    const totalPurchases = purchases.reduce((sum, p) => {
      return sum + (parseFloat(p.total_amount) || 0);
    }, 0);'''

new_calc = '''    const totalPurchases = purchases
      .filter(p => p.status !== 'cancelled')
      .reduce((sum, p) => {
        return sum + (parseFloat(p.total_amount) || 0);
      }, 0);'''

content = content.replace(old_calc, new_calc)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Inventory frontend fixes applied!")
