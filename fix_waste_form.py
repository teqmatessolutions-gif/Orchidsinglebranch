"""
Fix waste form to include food items
This script will update the WasteLogFormModal to support food items
"""

file_path = "dasboard/src/pages/Inventory.jsx"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Update component props to include foodItems
old_props = '''const WasteLogFormModal = ({
  form,
  setForm,
  items = [],
  locations = [],
  onSubmit,
  onClose,
}) => {'''

new_props = '''const WasteLogFormModal = ({
  form,
  setForm,
  items = [],
  foodItems = [],
  locations = [],
  onSubmit,
  onClose,
}) => {'''

content = content.replace(old_props, new_props)

# Fix 2: Update item dropdown to include food items with optgroups
old_dropdown = '''            <select
              value={form.item_id}
              onChange={(e) => {
                const item = items.find(
                  (i) => i.id === parseInt(e.target.value),
                );
                setForm({
                  ...form,
                  item_id: e.target.value,
                  unit: item?.unit || "pcs",
                });
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              required
            >
              <option value="">Select Item</option>
              {items.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
            </select>'''

new_dropdown = '''            <select
              value={form.item_id || form.food_item_id || ""}
              onChange={(e) => {
                const value = e.target.value;
                const type = e.target.selectedOptions[0]?.dataset.type;
                
                if (type === 'food') {
                  const foodItem = foodItems.find(i => i.id === parseInt(value));
                  setForm({
                    ...form,
                    food_item_id: value,
                    item_id: "",
                    is_food_item: true,
                    unit: foodItem?.unit || "pcs",
                  });
                } else {
                  const item = items.find(i => i.id === parseInt(value));
                  setForm({
                    ...form,
                    item_id: value,
                    food_item_id: "",
                    is_food_item: false,
                    unit: item?.unit || "pcs",
                  });
                }
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              required
            >
              <option value="">Select Item</option>
              <optgroup label="Inventory Items (Raw Materials)">
                {items.map((item) => (
                  <option key={`inv-${item.id}`} value={item.id} data-type="inventory">
                    {item.name}
                  </option>
                ))}
              </optgroup>
              <optgroup label="Food Items (Prepared Dishes)">
                {foodItems.map((item) => (
                  <option key={`food-${item.id}`} value={item.id} data-type="food">
                    {item.name}
                  </option>
                ))}
              </optgroup>
            </select>'''

content = content.replace(old_dropdown, new_dropdown)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Waste form updated to include food items!")
