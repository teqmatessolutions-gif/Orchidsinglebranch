#!/usr/bin/env python3
"""
Add /inventoryfiles location to Nginx configuration for serving static files
"""

nginx_file = "/etc/nginx/sites-enabled/pomma"

# Read the file
with open(nginx_file, 'r') as f:
    lines = f.readlines()

# Find where to insert (before the /inventoryapi/ block)
insert_idx = -1
for i, line in enumerate(lines):
    if 'location /inventoryapi/' in line:
        insert_idx = i
        break

if insert_idx == -1:
    print("Could not find /inventoryapi/ location block")
    exit(1)

# Check if /inventoryfiles already exists
if any('location /inventoryfiles' in line for line in lines):
    print("/inventoryfiles location already exists")
    exit(0)

# Add the new location block
new_block = [
    "    location /inventoryfiles/ {\n",
    "        alias /var/www/inventory/ResortApp/static/;\n",
    "        try_files $uri $uri/ =404;\n",
    "        add_header Cache-Control \"public, max-age=31536000\";\n",
    "    }\n",
    "\n"
]

lines[insert_idx:insert_idx] = new_block

# Write back
with open(nginx_file, 'w') as f:
    f.writelines(lines)

print("✅ Added /inventoryfiles location to Nginx configuration")
print("Run: sudo nginx -t && sudo systemctl reload nginx")
