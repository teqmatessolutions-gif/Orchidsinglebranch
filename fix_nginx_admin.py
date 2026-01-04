
import os

path = '/etc/nginx/sites-enabled/pomma'
with open(path) as f: lines = f.readlines()

# Check if admin block exists
if any('location /inventory/admin' in l for l in lines):
    print("Admin block already exists")
    exit(0)

# Find insertion point: BEFORE "location /inventoryapi/"
insert_idx = -1
for i, l in enumerate(lines):
    if 'location /inventoryapi/' in l:
        insert_idx = i
        break

if insert_idx == -1:
    print("Could not find location /inventoryapi/")
    # Fallback: find "listen 443" and insert before
    for i, l in enumerate(lines):
         if 'listen 443' in l:
             insert_idx = i
             break

if insert_idx != -1:
    new_block = [
        "    location /inventory/admin {\n",
        "        alias /var/www/html/inventory/admin;\n",
        "        try_files $uri $uri/ /inventory/admin/index.html;\n",
        "    }\n"
    ]
    lines[insert_idx:insert_idx] = new_block

    with open('/tmp/pomma.fixed', 'w') as f:
        f.writelines(lines)
    print("Generated /tmp/pomma.fixed")
else:
    print("Could not find insertion point")
    exit(1)
