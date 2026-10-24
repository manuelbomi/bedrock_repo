#!/bin/bash

set -e

echo "====================================="
echo "Bedrock Agent UI - Setup Script"
echo "====================================="

# Check for required tools
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "Error: $1 is not installed"
        exit 1
    fi
}

echo "Checking prerequisites..."
check_command node
check_command npm
check_command python3
check_command pip
check_command docker
check_command docker-compose

# Setup backend
echo ""
echo "Setting up backend..."
cd backend

if [ ! -f .env ]; then
    echo "Creating backend .env file from example..."
    cp .env.example .env
    echo "Please edit backend/.env with your AWS credentials"
fi

echo "Installing Python dependencies..."
pip install -r requirements.txt

cd ..

# Setup frontend
echo ""
echo "Setting up frontend..."
cd frontend

if [ ! -f .env ]; then
    echo "Creating frontend .env file from example..."
    cp .env.example .env
fi

echo "Installing Node dependencies..."
npm install

cd ..

# Create DynamoDB tables (optional)
echo ""
read -p "Do you want to create DynamoDB tables? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Creating DynamoDB tables..."
    cd deploy/terraform
    terraform init
    terraform apply -auto-approve
    cd ../..
fi

echo ""
echo "====================================="
echo "Setup complete!"
echo "====================================="
echo ""
echo "To start development servers:"
echo "  Option 1 - Using Docker Compose:"
echo "    docker-compose up"
echo ""
echo "  Option 2 - Run separately:"
echo "    Backend:  cd backend && uvicorn app:app --reload"
echo "    Frontend: cd frontend && npm run dev"
echo ""
echo "Access the application at http://localhost:3000"
echo "====================================="
