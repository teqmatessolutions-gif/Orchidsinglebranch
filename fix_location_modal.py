import re

# Read the file
with open('dasboard/src/pages/Inventory.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the class name - find the LocationFormModal div
old_pattern = r'(const LocationFormModal.*?return \(\s*<div className="fixed inset-0.*?>\s*)<div className="bg-white rounded-xl shadow-xl max-w-2xl w-full mx-4 max-h-\\?\[90vh\\?\] overflow-y-auto">'
new_replacement = r'\1<div className="bg-white rounded-xl shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">'

# Try the replacement
content_new = re.sub(old_pattern, new_replacement, content, flags=re.DOTALL)

# If that didn't work, try a simpler pattern
if content_new == content:
    # Just replace the specific line
    content_new = content.replace(
        '<div className="bg-white rounded-xl shadow-xl max-w-2xl w-full mx-4 max-h-\\[90vh\\] overflow-y-auto">',
        '<div className="bg-white rounded-xl shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">'
    )

# Write back
with open('dasboard/src/pages/Inventory.jsx', 'w', encoding='utf-8') as f:
    f.write(content_new)

print("Fixed the LocationFormModal to be scrollable!")
