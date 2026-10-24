#!/bin/bash

set -e

echo "====================================="
echo "Bedrock Agent UI - Deployment Script"
echo "====================================="

ENVIRONMENT=${1:-dev}
AWS_REGION=${AWS_REGION:-us-east-1}

echo "Environment: $ENVIRONMENT"
echo "AWS Region: $AWS_REGION"

# Build frontend
echo ""
echo "Building frontend..."
cd frontend
npm run build

# Deploy to S3
echo ""
echo "Deploying frontend to S3..."
S3_BUCKET=$(cd ../deploy/terraform && terraform output -raw s3_bucket)

aws s3 sync dist/ s3://$S3_BUCKET/ \
  --delete \
  --cache-control "max-age=31536000,public,immutable" \
  --exclude "*.html"

aws s3 sync dist/ s3://$S3_BUCKET/ \
  --exclude "*" \
  --include "*.html" \
  --cache-control "no-cache"

cd ..

# Invalidate CloudFront cache
echo ""
echo "Invalidating CloudFront cache..."
DISTRIBUTION_ID=$(cd deploy/terraform && terraform output -raw cloudfront_distribution_id)
aws cloudfront create-invalidation \
  --distribution-id $DISTRIBUTION_ID \
  --paths "/*"

# Deploy backend (example using ECS, adjust as needed)
echo ""
echo "Building and pushing backend Docker image..."
cd backend

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPOSITORY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/bedrock-agent-backend"

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin $ECR_REPOSITORY

# Build and push
docker build -t bedrock-agent-backend:latest .
docker tag bedrock-agent-backend:latest $ECR_REPOSITORY:latest
docker tag bedrock-agent-backend:latest $ECR_REPOSITORY:$ENVIRONMENT-$(date +%Y%m%d-%H%M%S)
docker push $ECR_REPOSITORY:latest
docker push $ECR_REPOSITORY:$ENVIRONMENT-$(date +%Y%m%d-%H%M%S)

cd ..

echo ""
echo "====================================="
echo "Deployment complete!"
echo "====================================="
