"""
Enterprise Backend API for Bedrock Agent
FastAPI server that interfaces with AWS Bedrock AgentCore
"""
import os
import sys
import json
import uuid
import subprocess
from datetime import datetime
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

import boto3
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# AWS Configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AGENT_ARN = "arn:aws:bedrock-agentcore:us-east-1:775690977233:runtime/agent_with_memory_2-aq9shtARJa"
AGENT_ID = "agent_with_memory_2-aq9shtARJa"
AGENT_NAME = "agent_with_memory_2"

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)

# DynamoDB tables for session and user management
SESSIONS_TABLE = os.getenv("SESSIONS_TABLE", "bedrock-agent-sessions")
USERS_TABLE = os.getenv("USERS_TABLE", "bedrock-agent-users")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup"""
    print(f"Starting Bedrock Agent API")
    print(f"Agent ARN: {AGENT_ARN}")
    print(f"AWS Region: {AWS_REGION}")

    # Create DynamoDB tables if they don't exist
    try:
        create_dynamodb_tables()
    except Exception as e:
        print(f"Warning: Could not create DynamoDB tables: {e}")

    yield

    print("Shutting down Bedrock Agent API")


app = FastAPI(
    title="Bedrock Agent Enterprise API",
    description="Production-ready API for AWS Bedrock AgentCore with multi-user support",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class ChatRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str


class SessionInfo(BaseModel):
    session_id: str
    user_id: str
    created_at: str
    last_message_at: str
    message_count: int


class UserInfo(BaseModel):
    user_id: str
    email: str
    created_at: str
    session_count: int


# Helper functions
def create_dynamodb_tables():
    """Create DynamoDB tables for sessions and users if they don't exist"""
    dynamodb_client = boto3.client('dynamodb', region_name=AWS_REGION)

    # Check and create sessions table
    try:
        dynamodb_client.describe_table(TableName=SESSIONS_TABLE)
        print(f"Sessions table {SESSIONS_TABLE} already exists")
    except dynamodb_client.exceptions.ResourceNotFoundException:
        print(f"Creating sessions table {SESSIONS_TABLE}")
        dynamodb_client.create_table(
            TableName=SESSIONS_TABLE,
            KeySchema=[
                {'AttributeName': 'session_id', 'KeyType': 'HASH'},
            ],
            AttributeDefinitions=[
                {'AttributeName': 'session_id', 'AttributeType': 'S'},
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'UserIdIndex',
                    'KeySchema': [
                        {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )

    # Check and create users table
    try:
        dynamodb_client.describe_table(TableName=USERS_TABLE)
        print(f"Users table {USERS_TABLE} already exists")
    except dynamodb_client.exceptions.ResourceNotFoundException:
        print(f"Creating users table {USERS_TABLE}")
        dynamodb_client.create_table(
            TableName=USERS_TABLE,
            KeySchema=[
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
            ],
            AttributeDefinitions=[
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )


def get_user_id(authorization: Optional[str] = Header(None)) -> str:
    """Extract user ID from authorization header or use default"""
    if authorization and authorization.startswith("Bearer "):
        # In production, validate JWT token and extract user_id
        # For now, we'll use a simple approach
        try:
            # This is a placeholder - implement proper JWT validation
            token = authorization.replace("Bearer ", "")
            return token.split("-")[0] if "-" in token else "default-user"
        except:
            return "default-user"
    return "default-user"


def save_session(session_id: str, user_id: str, message_count: int = 0):
    """Save or update session in DynamoDB"""
    try:
        table = dynamodb.Table(SESSIONS_TABLE)
        table.put_item(
            Item={
                'session_id': session_id,
                'user_id': user_id,
                'created_at': datetime.utcnow().isoformat(),
                'last_message_at': datetime.utcnow().isoformat(),
                'message_count': message_count
            }
        )
    except Exception as e:
        print(f"Warning: Could not save session to DynamoDB: {e}")


def update_session(session_id: str):
    """Update session last message timestamp"""
    try:
        table = dynamodb.Table(SESSIONS_TABLE)
        table.update_item(
            Key={'session_id': session_id},
            UpdateExpression='SET last_message_at = :timestamp ADD message_count :inc',
            ExpressionAttributeValues={
                ':timestamp': datetime.utcnow().isoformat(),
                ':inc': 1
            }
        )
    except Exception as e:
        print(f"Warning: Could not update session: {e}")


def invoke_bedrock_agent(prompt: str, session_id: str) -> str:
    """Invoke the Bedrock AgentCore agent with the given prompt and session"""
    try:
        # Prepare the payload for AgentCore
        payload = {
            "prompt": prompt,
            "session_id": session_id
        }

        # Set up environment to suppress warnings and handle encoding
        env = os.environ.copy()
        env["AGENTCORE_SUPPRESS_RECOMMENDATION"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"

        # Use the agentcore CLI to invoke the agent
        # The agentcore CLI expects: python -m bedrock_agentcore_starter_toolkit.cli.cli invoke --agent <agent_name> '<json_payload>'
        result = subprocess.run(
            [sys.executable, "-m", "bedrock_agentcore_starter_toolkit.cli.cli", "invoke", "--agent", AGENT_NAME, json.dumps(payload)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),  # Run from project root
            env=env,
            encoding='utf-8',
            errors='replace'  # Replace encoding errors with placeholders
        )

        # The CLI may have encoding issues but still succeed - check for response content
        output = result.stdout.strip()

        # Look for "Response:" section in the output
        if "Response:" in output:
            # Extract everything after "Response:"
            response_start = output.find("Response:") + len("Response:")
            response_content = output[response_start:].strip()
            return response_content if response_content else "No response content from agent"

        # If no explicit Response section, try to parse as JSON
        try:
            response_data = json.loads(output)
            return response_data.get("response", output)
        except json.JSONDecodeError:
            pass

        # Check if there's an error even if returncode is 0
        if result.returncode != 0 or "error" in output.lower() or "traceback" in output.lower():
            error_msg = result.stderr or output or "Unknown error"
            print(f"AgentCore invocation failed: {error_msg}")
            raise HTTPException(status_code=500, detail=f"Agent invocation failed: Check agent logs")

        # Return any output we got
        return output if output else "No response from agent"

    except subprocess.TimeoutExpired:
        print(f"Agent invocation timed out after 60 seconds")
        raise HTTPException(status_code=504, detail="Agent invocation timed out")
    except Exception as e:
        print(f"Error invoking Bedrock AgentCore agent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to invoke agent: {str(e)}")


# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Bedrock Agent Enterprise API",
        "agent_id": AGENT_ID,
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "agent": {
            "id": AGENT_ID,
            "arn": AGENT_ARN,
            "region": AWS_REGION
        }
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_user_id)
):
    """
    Send a message to the Bedrock agent and get a response

    - Maintains session continuity for conversation memory
    - Tracks user sessions in DynamoDB
    """
    # Generate or use existing session ID
    session_id = request.session_id or str(uuid.uuid4())

    # Save session info
    if not request.session_id:
        save_session(session_id, user_id, message_count=0)
    else:
        update_session(session_id)

    # Invoke the agent
    response_text = invoke_bedrock_agent(request.prompt, session_id)

    return ChatResponse(
        response=response_text,
        session_id=session_id,
        timestamp=datetime.utcnow().isoformat()
    )


@app.get("/sessions", response_model=List[SessionInfo])
async def get_sessions(user_id: str = Depends(get_user_id)):
    """Get all sessions for the current user"""
    try:
        table = dynamodb.Table(SESSIONS_TABLE)
        response = table.query(
            IndexName='UserIdIndex',
            KeyConditionExpression='user_id = :uid',
            ExpressionAttributeValues={':uid': user_id}
        )

        return [
            SessionInfo(
                session_id=item['session_id'],
                user_id=item['user_id'],
                created_at=item['created_at'],
                last_message_at=item.get('last_message_at', item['created_at']),
                message_count=item.get('message_count', 0)
            )
            for item in response.get('Items', [])
        ]
    except Exception as e:
        print(f"Error fetching sessions: {e}")
        return []


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str, user_id: str = Depends(get_user_id)):
    """Delete a session"""
    try:
        table = dynamodb.Table(SESSIONS_TABLE)
        table.delete_item(Key={'session_id': session_id})
        return {"status": "deleted", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")


@app.get("/user/info", response_model=UserInfo)
async def get_user_info(user_id: str = Depends(get_user_id)):
    """Get current user information"""
    try:
        # Count sessions for this user
        table = dynamodb.Table(SESSIONS_TABLE)
        response = table.query(
            IndexName='UserIdIndex',
            KeyConditionExpression='user_id = :uid',
            ExpressionAttributeValues={':uid': user_id},
            Select='COUNT'
        )

        return UserInfo(
            user_id=user_id,
            email=f"{user_id}@example.com",  # Replace with actual email from Cognito
            created_at=datetime.utcnow().isoformat(),
            session_count=response.get('Count', 0)
        )
    except Exception as e:
        print(f"Error fetching user info: {e}")
        return UserInfo(
            user_id=user_id,
            email=f"{user_id}@example.com",
            created_at=datetime.utcnow().isoformat(),
            session_count=0
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
