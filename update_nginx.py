
import os

config_path = '/etc/nginx/sites-enabled/pomma'
with open(config_path, 'r') as f:
    lines = f.readlines()

insert_idx = -1
for i, line in enumerate(lines):
    if 'listen 443 ssl;' in line:
        insert_idx = i
        break

if insert_idx != -1:
    new_conf = [
        "\n    # --- INVENTORY SYSTEM CONFIGURATION ---\n",
        "    location /inventory {\n",
        "        alias /var/www/html/inventory;\n",
        "        try_files $uri $uri/ /inventory/index.html;\n",
        "    }\n\n",
        "    location /inventory/admin {\n",
        "        alias /var/www/html/inventory/admin;\n",
        "        try_files $uri $uri/ /inventory/admin/index.html;\n",
        "    }\n\n",
        "    location /inventoryapi/ {\n",
        "        rewrite ^/inventoryapi/(.*) /$1 break;\n",
        "        proxy_pass http://127.0.0.1:8011;\n",
        "        proxy_set_header Host $host;\n",
        "        proxy_set_header X-Real-IP $remote_addr;\n",
        "        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n",
        "        proxy_set_header X-Forwarded-Proto $scheme;\n",
        "    }\n",
        "    # --------------------------------------\n"
    ]
    lines[insert_idx:insert_idx] = new_conf
    
    with open('/tmp/pomma.new', 'w') as f:
        f.writelines(lines)
    print("Configuration generated at /tmp/pomma.new")
else:
    print("Could not find insertion point 'listen 443 ssl;'")
