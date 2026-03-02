#!/bin/bash

# Deployment script for Disease Prediction Platform

echo "🚀 Starting deployment..."

# Load environment variables
source .env

# Pull latest changes
echo "📦 Pulling latest code..."
git pull origin main

# Build and deploy with Docker Compose
echo "🐳 Building Docker images..."
docker-compose -f docker/docker-compose.yml build

# Run database migrations
echo "🗄️ Running database migrations..."
docker-compose -f docker/docker-compose.yml run --rm backend flask db upgrade

# Start services
echo "▶️ Starting services..."
docker-compose -f docker/docker-compose.yml up -d

# Check service health
echo "🏥 Checking service health..."
sleep 10
curl -f http://localhost:5000/api/health || exit 1

echo "✅ Deployment completed successfully!"