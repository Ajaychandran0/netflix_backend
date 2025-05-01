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

# 🔁 Generate Prisma client after dependencies are installed
RUN npx prisma generate

# Expose development server port
EXPOSE 3001

# Command to run development server
CMD ["npm", "run", "dev"]


# ------------------------------
# 🚀 Production Stage
# ------------------------------
FROM base AS prod

# Install only production dependencies
RUN npm ci --only=production

# Copy all files
COPY . .

# 🔁 Generate Prisma client
RUN npx prisma generate

# Build (for TypeScript projects)
RUN npm run build

# Expose production server port
EXPOSE 3001

CMD ["npm", "run", "start"]

