# ------------------------------
# 🏗 Base Stage: Common setup for both dev and prod
# ------------------------------
    FROM node:20-alpine AS base

    # Set working directory
    WORKDIR /app
    
    # Copy package.json and package-lock.json separately to leverage Docker cache
    COPY package*.json ./
    
    # ------------------------------
    # 🛠 Development Stage
    # ------------------------------
    FROM base AS dev
    
    # Install all dependencies including devDependencies
    RUN npm install
    
    # Copy all source code
    COPY . .
    
    # Expose development server port
    EXPOSE 3001
    
    # Command to run development server (delegated to package.json)
    CMD ["npm", "run", "dev"]
    
    # ------------------------------
    # 🚀 Production Stage
    # ------------------------------
    FROM base AS prod
    
    # Only install production dependencies
    RUN npm ci --only=production

    # Copy only necessary files (optional: you can create .dockerignore to avoid copying unnecessary stuff)
    COPY . .
    
    # (Optional) Build if you are transpiling TypeScript (assuming dist/ will be generated)
    RUN npm run build
    
    # Expose production server port
    EXPOSE 3001
    
    # Command to run production server
    CMD ["npm", "run", "start"]
    