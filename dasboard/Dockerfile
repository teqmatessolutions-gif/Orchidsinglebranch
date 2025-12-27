# Build Stage
FROM node:18-alpine as build

WORKDIR /app

# Copy package.json and lock file
COPY package.json ./
# If you have package-lock.json, uncomment the next line
# COPY package-lock.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build the application
# Use production environment variable usually, but CRA handles build command
RUN npm run build

# Production Stage
FROM nginx:alpine

# Copy built assets from builder stage
COPY --from=build /app/build /usr/share/nginx/html

# Copy custom nginx configuration if needed (optional but recommended for SPA routing)
# We will create a simple nginx conf file inline or COPY it
# For now, let's inject a simple configuration for SPA fallback
RUN echo 'server { \
    listen 80; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html index.htm; \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
