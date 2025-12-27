#!/bin/bash

# ==========================================
# TeqMates Server Provisioning Script
# ==========================================
# Run this on a fresh Ubuntu 22.04 / 20.04 Server
# Usage: sudo ./provision_server.sh

set -e # Exit on error

echo "🚀 Starting Server Provisioning..."

# 1. Update System
echo "📦 Updating system packages..."
apt-get update && apt-get upgrade -y
apt-get install -y python3-pip python3-venv python3-dev libpq-dev postgresql postgresql-contrib nginx git curl build-essential acl

# 2. Install Node.js 18.x
if ! command -v node &> /dev/null; then
    echo "📦 Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt-get install -y nodejs
fi

# 3. Create Project Directories
echo "📂 Creating Directory Structure..."
mkdir -p /var/www/resort/Resort_first
mkdir -p /var/www/resort/orchid_production
mkdir -p /var/www/resort/resort_production
mkdir -p /var/www/landingpage

# Set Permissions (assuming 'ubuntu' user, change if using root or another user)
# We grant 'www-data' ownership and allow the current user to write
chown -R www-data:www-data /var/www/resort /var/www/landingpage
chmod -R 775 /var/www/resort /var/www/landingpage
# Add current user to www-data group
usermod -aG www-data $SUDO_USER

# 4. Database Setup
echo "🗄️ Setting up PostgreSQL Databases..."
# We use sudo -u postgres psql to execute commands
sudo -u postgres psql <<EOF
-- Pomma
CREATE DATABASE pommadb;
CREATE USER resort_user WITH PASSWORD 'ResortDB2024';
ALTER DATABASE pommadb OWNER TO resort_user;
GRANT ALL PRIVILEGES ON DATABASE pommadb TO resort_user;

-- Orchid
CREATE DATABASE orchiddb;
CREATE USER orchiduser WITH PASSWORD 'orchid123';
ALTER DATABASE orchiddb OWNER TO orchiduser;
GRANT ALL PRIVILEGES ON DATABASE orchiddb TO orchiduser;

-- Resort Demo
CREATE DATABASE rdb;
CREATE USER resortuser WITH PASSWORD 'resort123';
ALTER DATABASE rdb OWNER TO resortuser;
GRANT ALL PRIVILEGES ON DATABASE rdb TO resortuser;
EOF
echo "✅ Databases created."

# 5. Nginx Configuration
echo "🌐 Configuring Nginx..."
cat > /etc/nginx/sites-available/teqmates <<'EOF'
upstream pomma_backend {
    server 127.0.0.1:8010;
    keepalive 32;
}

upstream orchid_backend {
    server 127.0.0.1:8011;
    keepalive 32;
}

upstream resort_backend {
    server 127.0.0.1:8012;
    keepalive 32;
}

server {
    listen 80;
    server_name teqmates.com www.teqmates.com;

    # 🏠 MAIN LANDING PAGE
    location / {
        root /var/www/landingpage;
        index index.html;
        try_files $uri $uri/ =404;
    }

    # 🌸 ORCHID RESORT
    location /orchid {
        alias /var/www/resort/orchid_production/userend/userend/build;
        try_files $uri $uri/ /orchid/index.html;
    }
    location /orchidadmin {
        alias /var/www/resort/orchid_production/dasboard/build;
        try_files $uri $uri/ /orchidadmin/index.html;
    }
    location /orchidapi/ {
        proxy_pass http://orchid_backend/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
    location /orchidfiles/ {
        alias /var/www/resort/orchid_production/ResortApp/;
    }

    # 📦 POMMA HOLIDAYS
    location /pommaholidays {
        alias /var/www/resort/Resort_first/userend/userend/build;
        try_files $uri $uri/ /pommaholidays/index.html;
    }
    location /pommaadmin {
        alias /var/www/resort/Resort_first/dasboard/build;
        try_files $uri $uri/ /pommaadmin/index.html;
    }
    location /pommaapi/ {
        proxy_pass http://pomma_backend/;
        proxy_set_header Host $host;
    }
    location /pomma/ {
        alias /var/www/resort/pomma_production/ResortApp/;
    }

    # 🏨 RESORT DEMO
    location /resort {
        alias /var/www/resort/resort_production/userend/userend/build;
        try_files $uri $uri/ /resort/index.html;
    }
    location /admin {
        alias /var/www/resort/resort_production/dasboard/build;
        try_files $uri $uri/ /admin/index.html;
    }
    location /resoapi/ {
        proxy_pass http://resort_backend/;
        proxy_set_header Host $host;
    }
    location /resortfiles/ {
        alias /var/www/resort/resort_production/ResortApp/;
    }
}
EOF

# Enable Site
ln -sf /etc/nginx/sites-available/teqmates /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

echo "🎉 Server Provisioning Complete!"
echo "Next steps:"
echo "1. Run deployment scripts for each project."
echo "2. Upload Landing Page to /var/www/landingpage"
echo "3. Update DNS to point to this server."
