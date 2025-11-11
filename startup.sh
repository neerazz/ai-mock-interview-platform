#!/bin/bash

# Startup script for AI Mock Interview Platform

set -e

echo "Starting AI Mock Interview Platform..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please create .env file with required environment variables."
    echo "You can use .env.template as a starting point:"
    echo "  cp .env.template .env"
    echo "Then edit .env with your actual values."
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Validate required environment variables
required_vars=("DB_PASSWORD" "OPENAI_API_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: $var is not set in .env file"
        exit 1
    fi
done

# Create necessary directories
mkdir -p data/sessions logs

# Start Docker services
echo "Starting Docker services..."
docker-compose up -d

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
max_attempts=30
attempt=0
until docker exec interview_platform_db pg_isready -U interview_user > /dev/null 2>&1; do
    attempt=$((attempt + 1))
    if [ $attempt -eq $max_attempts ]; then
        echo "Error: PostgreSQL failed to start after $max_attempts attempts"
        docker-compose logs postgres
        exit 1
    fi
    echo "Waiting for PostgreSQL... (attempt $attempt/$max_attempts)"
    sleep 2
done

echo "PostgreSQL is ready!"

# Check database connection
echo "Verifying database connection..."
docker exec interview_platform_db psql -U interview_user -d interview_platform -c "SELECT 1;" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "Database connection successful!"
else
    echo "Error: Could not connect to database"
    docker-compose logs postgres
    exit 1
fi

# Verify tables were created
echo "Verifying database schema..."
table_count=$(docker exec interview_platform_db psql -U interview_user -d interview_platform -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
if [ "$table_count" -ge 7 ]; then
    echo "Database schema initialized successfully! ($table_count tables created)"
else
    echo "Warning: Expected at least 7 tables, found $table_count"
fi

# Display service status
echo ""
echo "================================"
echo "Services started successfully!"
echo "================================"
echo "PostgreSQL: localhost:5432"
echo "  Database: interview_platform"
echo "  User: interview_user"
echo ""
echo "Streamlit App: http://localhost:8501"
echo "================================"
echo ""
echo "Useful commands:"
echo "  View logs:        docker-compose logs -f"
echo "  View app logs:    docker-compose logs -f app"
echo "  View DB logs:     docker-compose logs -f postgres"
echo "  Stop services:    docker-compose down"
echo "  Restart services: docker-compose restart"
echo ""
echo "Data directories:"
echo "  Sessions: ./data/sessions/"
echo "  Logs:     ./logs/"
echo ""
