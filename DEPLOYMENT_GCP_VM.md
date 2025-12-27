# ☁️ Deploying TeqMates Projects to Google Cloud Platform (Compute Engine)

 This guide outlines how to migrate your existing multi-tenant setup (Pomma, Orchid, Resort) to a **GCP Compute Engine Virtual Machine**. This approach replicates your current server architecture (Ubuntu + Nginx + Postgres) for maximum compatibility.

 ## 🏗️ 1. GCP Infrastructure Setup

 ### Step 1: Create VM Instance
 1. Go to **Google Cloud Console** > **Compute Engine** > **VM Instances**.
 2. Click **Create Instance**.
    *   **Name:** `teqmates-prod-server`
    *   **Region:** `asia-south1` (or your preferred region)
    *   **Machine Type:** `e2-medium` (2 vCPU, 4GB RAM) for moderate traffic, or `e2-standard-4` for higher performance.
    *   **Boot Disk:** Ubuntu 22.04 LTS (x86/64), 50GB SSD.
    *   **Firewall:** Check "Allow HTTP traffic" and "Allow HTTPS traffic".
 3. Click **Create**.

 ### Step 2: Reserve Static IP
 1. Go to **VPC Network** > **IP addresses**.
 2. Click **Reserve External Static IP**.
 3. Attach it to your `teqmates-prod-server`.
 4. **Note this IP** (e.g., `34.xxx.xxx.xxx`). You will update GoDaddy/DNS to point `teqmates.com` to this IP.

 ---

 ## 🛠️ 2. Server Environment Configuration

 SSH into your new VM (via Console "SSH" button or local terminal).

 ### Update System & Install Dependencies
 ```bash
 sudo apt update && sudo apt upgrade -y
 sudo apt install -y python3-pip python3-venv python3-dev libpq-dev postgresql postgresql-contrib nginx git curl build-essential
 ```

 ### Install Node.js (for React builds)
 ```bash
 curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
 sudo apt install -y nodejs
 ```

 ### Setup Postgres Database
 ```bash
 sudo systemctl start postgresql
 sudo -u postgres psql
 ```

 Inside the SQL shell, create the Databases and Users matching your configuration:

 ```sql
 -- 1. Pomma
 CREATE DATABASE pommadb;
 CREATE USER resort_user WITH PASSWORD 'ResortDB2024';
 GRANT ALL PRIVILEGES ON DATABASE pommadb TO resort_user;

 -- 2. Orchid
 CREATE DATABASE orchiddb;
 CREATE USER orchiduser WITH PASSWORD 'orchid123';
 GRANT ALL PRIVILEGES ON DATABASE orchiddb TO orchiduser;

 -- 3. Resort Demo
 CREATE DATABASE rdb;
 CREATE USER resortuser WITH PASSWORD 'resort123';
 GRANT ALL PRIVILEGES ON DATABASE rdb TO resortuser;
 
 -- Exit
 \q
 ```

 ---

 ## 📂 3. Project Deployment (Code Transfer)

 Create the directory structure:
 ```bash
 sudo mkdir -p /var/www/resort/Resort_first
 sudo mkdir -p /var/www/resort/orchid_production
 sudo mkdir -p /var/www/resort/resort_production
 sudo mkdir -p /var/www/landingpage  # For your landing page
 sudo chown -R $USER:www-data /var/www/resort
 sudo chown -R $USER:www-data /var/www/landingpage
 ```

 ### App 1: Orchid Resort (Currently working on)
 1. **Clone Repo:**
    ```bash
    git clone https://github.com/teqmatessolutions-gif/orchidresort.git /var/www/resort/orchid_production
    ```
 2. **Backend Setup:**
    ```bash
    cd /var/www/resort/orchid_production/ResortApp
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    
    # Create .env file
    nano .env
    # Paste the content: DATABASE_URL=postgresql+psycopg2://orchiduser:orchid123@localhost:5432/orchiddb
    ```
 3. **Run Migrations:**
    ```bash
    alembic upgrade head
    # OR if using simple create_tables script
    python init_db.py 
    ```
 4. **Frontend Build:**
    ```bash
    cd /var/www/resort/orchid_production/dasboard
    npm install --legacy-peer-deps
    npm run build
    
    cd /var/www/resort/orchid_production/userend/userend
    npm install --legacy-peer-deps
    npm run build
    ```

 *(Repeat similar steps for Pomma and Resort Demo repos).*

 ### Setup Landing Page
 You specifically requested the landing page at `teqmates.com`.
 1. Upload your local folder `C:\releasing\Resort\landingpage` to the server at `/var/www/landingpage`.
    *   *(Use SCP or SFTP like FileZilla connected to the VM IP).*

 ---

 ## ⚙️ 4. Application Services (Systemd)

 Create `systemd` files for each backend API to keep them running.

 ### Orchid Service
 `sudo nano /etc/systemd/system/orchid.service`
 ```ini
 [Unit]
 Description=Orchid Resort API
 After=network.target

 [Service]
 User=root
 Group=www-data
 WorkingDirectory=/var/www/resort/orchid_production/ResortApp
 Environment="PATH=/var/www/resort/orchid_production/ResortApp/venv/bin"
 EnvironmentFile=/var/www/resort/orchid_production/ResortApp/.env
 ExecStart=/var/www/resort/orchid_production/ResortApp/venv/bin/gunicorn main:app --workers 3 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8011
 Restart=always

 [Install]
 WantedBy=multi-user.target
 ```

 *(Create `pomma.service` on port 8010 and `resort.service` on port 8012 similarly).*

 **Start Services:**
 ```bash
 sudo systemctl daemon-reload
 sudo systemctl start orchid
 sudo systemctl enable orchid
 # ... repeat for others
 ```

 ---

 ## 🌐 5. Nginx Configuration (Reverse Proxy)

 Configure Nginx to route traffic based on your requirements.

 `sudo nano /etc/nginx/sites-available/teqmates`

 ```nginx
 upstream pomma_backend { server 127.0.0.1:8010; }
 upstream orchid_backend { server 127.0.0.1:8011; }
 upstream resort_backend { server 127.0.0.1:8012; }

 server {
     listen 80;
     server_name teqmates.com www.teqmates.com;

     # 🏠 MAIN LANDING PAGE (Root)
     location / {
         root /var/www/landingpage;
         index index.html;
         try_files $uri $uri/ =404;
     }

     # 🌸 ORCHID RESORT
     # User Frontend
     location /orchid {
         alias /var/www/resort/orchid_production/userend/userend/build;
         try_files $uri $uri/ /orchid/index.html;
     }
     # Admin Dashboard
     location /orchidadmin {
         alias /var/www/resort/orchid_production/dasboard/build;
         try_files $uri $uri/ /orchidadmin/index.html;
     }
     # Backend API
     location /orchidapi/ {
         proxy_pass http://orchid_backend/;
         proxy_http_version 1.1;
         proxy_set_header Upgrade $http_upgrade;
         proxy_set_header Connection 'upgrade';
         proxy_set_header Host $host;
         proxy_cache_bypass $http_upgrade;
     }
     # Static Files
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
 }
 ```

 **Activate Nginx Config:**
 ```bash
 sudo ln -s /etc/nginx/sites-available/teqmates /etc/nginx/sites-enabled/
 sudo rm /etc/nginx/sites-enabled/default
 sudo nginx -t
 sudo systemctl restart nginx
 ```

 ## 🔒 6. SSL Configuration (HTTPS)
 Use Certbot to get free SSL certificates.

 ```bash
 sudo apt install certbot python3-certbot-nginx
 sudo certbot --nginx -d teqmates.com -d www.teqmates.com
 ```

 ---

 ## ✅ Final Checklist
 1. **DNS**: Update A Record for `teqmates.com` to point to the new GCP VM IP.
 2. **Uploads**: Ensure `uploads` directories (e.g., `/var/www/resort/orchid_production/ResortApp/uploads`) are writable (`chmod 775`).
 3. **Landing Page**: Verify `C:\releasing\Resort\landingpage` contents are visible at `https://teqmates.com/`.

 This setup mirrors your previous server exactly, ensuring all paths and API endpoints work without code changes.
