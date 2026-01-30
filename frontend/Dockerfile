# syntax=docker/dockerfile:1
FROM node:20-alpine as build

WORKDIR /app

# Ensure latest npm is installed if not present
RUN if ! command -v npm >/dev/null 2>&1; then npm install -g npm@latest; else npm install -g npm@latest || true; fi

# Install dependencies
COPY package.json ./
RUN npm install

# Copy source
COPY . .


# Run tests (will not fail build if no tests are defined)
RUN npm run test

# Build the app
RUN npm run build

# --- Production image ---
FROM nginx:1.29-alpine
COPY --from=build /app/dist /usr/share/nginx/html
# For Next.js, use /app/.next instead of /app/dist and adjust as needed
COPY ./nginx.conf /etc/nginx/nginx.conf
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
