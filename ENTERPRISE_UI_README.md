# Bedrock Agent Enterprise UI

A production-ready, enterprise-grade React frontend and FastAPI backend for your AWS Bedrock AgentCore deployment. This solution enables multiple users to interact with your AI agent through a modern web interface.

## Features

- **Modern React UI** - Built with React 18, TypeScript, and Tailwind CSS
- **Session Management** - Track and resume conversations
- **Multi-User Support** - DynamoDB-backed user and session storage
- **Memory Support** - Leverages Bedrock AgentCore's memory capabilities
- **Production Ready** - Docker, Docker Compose, and AWS deployment configs
- **Enterprise Architecture** - Scalable, secure, and maintainable

## Architecture

```
┌─────────────────┐
│  React Frontend │ (Port 3000)
│  (Vite + TS)    │
└────────┬────────┘
         │
         │ HTTP/REST
         │
┌────────▼────────┐
│  FastAPI Backend│ (Port 8000)
│                 │
└────────┬────────┘
         │
         ├──────────────┐
         │              │
┌────────▼────────┐ ┌──▼──────────────┐
│  AWS Bedrock    │ │   DynamoDB      │
│  AgentCore      │ │  - Sessions     │
│  - Agent        │ │  - Users        │
│  - Memory       │ │                 │
└─────────────────┘ └─────────────────┘
```

## Quick Start

### Prerequisites

- Node.js 20+
- Python 3.11+
- Docker & Docker Compose (optional)
- AWS Account with Bedrock AgentCore access
- AWS CLI configured

### 1. Clone and Setup

```bash
# Navigate to the project directory
cd C:\Users\manue\Desktop\Amazon_Bedrock_Project\bedrock_repo

# Run setup script (Linux/Mac)
chmod +x scripts/setup.sh
./scripts/setup.sh

# Or setup manually:
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your AWS credentials
```

Update `backend/.env`:
```env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

SESSIONS_TABLE=bedrock-agent-sessions
USERS_TABLE=bedrock-agent-users

CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
```

Update `frontend/.env`:
```env
VITE_API_URL=http://localhost:8000
```

### 4. Create DynamoDB Tables

```bash
# Option 1: Using Terraform
cd deploy/terraform
terraform init
terraform apply

# Option 2: Using AWS CLI
aws dynamodb create-table \
  --table-name bedrock-agent-sessions \
  --attribute-definitions \
    AttributeName=session_id,AttributeType=S \
    AttributeName=user_id,AttributeType=S \
  --key-schema AttributeName=session_id,KeyType=HASH \
  --global-secondary-indexes \
    "IndexName=UserIdIndex,KeySchema=[{AttributeName=user_id,KeyType=HASH}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5}" \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5

aws dynamodb create-table \
  --table-name bedrock-agent-users \
  --attribute-definitions AttributeName=user_id,AttributeType=S \
  --key-schema AttributeName=user_id,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
```

### 5. Run the Application

#### Option A: Using Docker Compose (Recommended)

```bash
# From project root
docker-compose up

# Or run in background
docker-compose up -d
```

#### Option B: Run Separately

Terminal 1 - Backend:
```bash
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

### 6. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Usage

### Starting a Chat

1. Navigate to http://localhost:3000
2. Click on "Chat" in the sidebar
3. Type your message in the input box
4. The agent will respond using the FAQ knowledge base

### Managing Sessions

1. Click "Sessions" in the sidebar
2. View all your conversation history
3. Click on a session to resume it
4. Delete sessions you no longer need

### Session Features

- **Automatic Session Creation** - First message creates a new session
- **Session Persistence** - All conversations are saved
- **Memory Support** - Agent remembers context within sessions
- **Multi-Session** - Switch between different conversations

## API Endpoints

### Chat
- `POST /chat` - Send a message to the agent
  ```json
  {
    "prompt": "How do I activate an eSIM?",
    "session_id": "optional-session-id"
  }
  ```

### Sessions
- `GET /sessions` - Get all sessions for current user
- `DELETE /sessions/{session_id}` - Delete a session

### User
- `GET /user/info` - Get current user information

### Health
- `GET /health` - Health check endpoint

## Deployment

### AWS Production Deployment

#### 1. Deploy Infrastructure

```bash
cd deploy/terraform
terraform init
terraform apply
```

This creates:
- DynamoDB tables for sessions and users
- S3 bucket for frontend hosting
- CloudFront distribution for CDN

#### 2. Build and Deploy

```bash
# Make deploy script executable
chmod +x scripts/deploy.sh

# Deploy to production
./scripts/deploy.sh prod
```

#### 3. Update Backend Configuration

Update `backend/app.py` with your production agent ARN:
```python
AGENT_ARN = "arn:aws:bedrock-agentcore:us-east-1:775690977233:runtime/agent_with_memory_2-aq9shtARJa"
AGENT_ID = "agent_with_memory_2-aq9shtARJa"
```

### Environment Variables for Production

Backend:
- `AWS_REGION` - AWS region (default: us-east-1)
- `AGENT_ARN` - Bedrock AgentCore ARN
- `AGENT_ID` - Bedrock Agent ID
- `SESSIONS_TABLE` - DynamoDB sessions table name
- `USERS_TABLE` - DynamoDB users table name
- `CORS_ORIGINS` - Allowed CORS origins

Frontend:
- `VITE_API_URL` - Backend API URL

## Authentication (Optional Enhancement)

The current implementation uses a simple authorization header. For production, consider:

### AWS Cognito Integration

1. Create Cognito User Pool
2. Update `backend/app.py` to validate JWT tokens
3. Update `frontend/src/lib/api.ts` to include Cognito tokens

Example Cognito validation:
```python
from jose import jwt, JWTError
import requests

def verify_cognito_token(token: str):
    # Get Cognito JWKS
    region = "us-east-1"
    user_pool_id = "your-user-pool-id"
    jwks_url = f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json"

    jwks = requests.get(jwks_url).json()

    # Verify and decode token
    claims = jwt.decode(
        token,
        jwks,
        algorithms=["RS256"],
        audience="your-client-id"
    )

    return claims.get("sub")  # User ID
```

## Monitoring and Observability

### CloudWatch Logs

The Bedrock agent automatically logs to CloudWatch. View logs:

```bash
# Using AWS CLI
aws logs tail /aws/bedrock/agentcore/agent_with_memory_2-aq9shtARJa --follow

# Or use the custom script
python check_logs.py
```

### Metrics

Monitor these key metrics:
- Request latency
- Error rates
- DynamoDB read/write capacity
- Agent invocation count

## Troubleshooting

### Backend Issues

**Error: "Failed to invoke agent"**
- Check AWS credentials are configured correctly
- Verify agent ARN is correct
- Ensure IAM role has necessary permissions

**DynamoDB Errors**
- Verify tables exist: `aws dynamodb list-tables`
- Check table names match environment variables

### Frontend Issues

**API Connection Failed**
- Verify backend is running on port 8000
- Check CORS settings in backend
- Ensure `VITE_API_URL` is set correctly

**Build Errors**
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Clear cache: `npm cache clean --force`

### Docker Issues

**Port Already in Use**
```bash
# Stop existing containers
docker-compose down

# Or use different ports in docker-compose.yml
```

## Project Structure

```
bedrock_repo/
├── backend/
│   ├── app.py              # FastAPI application
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile         # Backend Docker image
│   └── .env.example       # Environment template
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── lib/           # API client
│   │   └── store/         # State management
│   ├── package.json       # Node dependencies
│   ├── Dockerfile         # Frontend Docker image
│   └── vite.config.ts     # Vite configuration
├── deploy/
│   └── terraform/         # Infrastructure as Code
│       └── main.tf        # AWS resources
├── scripts/
│   ├── setup.sh          # Setup script
│   └── deploy.sh         # Deployment script
├── docker-compose.yml    # Local development
└── ENTERPRISE_UI_README.md  # This file
```

## Security Considerations

### Production Checklist

- [ ] Enable HTTPS/TLS for all communications
- [ ] Implement proper authentication (Cognito, Auth0, etc.)
- [ ] Use AWS Secrets Manager for sensitive credentials
- [ ] Enable CloudFront WAF for DDoS protection
- [ ] Implement rate limiting on API endpoints
- [ ] Set up VPC for backend services
- [ ] Enable DynamoDB encryption at rest
- [ ] Regular security audits and dependency updates
- [ ] Implement CORS properly for production domains
- [ ] Use IAM roles instead of access keys when possible

## Performance Optimization

### Frontend
- Code splitting with React lazy loading
- Image optimization
- CDN caching with CloudFront
- Bundle size optimization

### Backend
- Connection pooling for DynamoDB
- Response caching with Redis (optional)
- Async processing for long-running tasks
- API rate limiting

## Cost Optimization

### AWS Resources
- Use DynamoDB on-demand pricing for variable workloads
- Implement S3 lifecycle policies
- Use CloudFront edge caching effectively
- Monitor Bedrock agent invocations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of your AWS Bedrock AgentCore implementation.

## Support

For issues and questions:
- Check the troubleshooting section above
- Review AWS Bedrock AgentCore documentation
- Check CloudWatch logs for detailed error messages

## Next Steps

1. **Add Authentication** - Implement AWS Cognito for user management
2. **Add Admin Dashboard** - Monitor usage, users, and agent performance
3. **Implement Chat History Export** - Allow users to download conversations
4. **Add File Upload** - Enable document uploads for context
5. **Multi-Agent Support** - Switch between different agents
6. **Analytics Dashboard** - Track user engagement and satisfaction

---

Built with AWS Bedrock AgentCore, React, and FastAPI
