# Quick Start Guide

Get your Bedrock Agent Enterprise UI running in 5 minutes!

## Prerequisites Check

- [ ] Node.js 20+ installed (`node --version`)
- [ ] Python 3.11+ installed (`python --version`)
- [ ] AWS credentials configured
- [ ] Your Bedrock agent is deployed and working

## 30-Second Start (Windows)

1. **Open terminal in project root**:
   ```cmd
   cd C:\Users\manue\Desktop\Amazon_Bedrock_Project\bedrock_repo
   ```

2. **Install backend dependencies**:
   ```cmd
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

3. **Install frontend dependencies**:
   ```cmd
   cd frontend
   npm install
   cd ..
   ```

4. **Start both servers** (easy mode):
   ```cmd
   scripts\start-dev.bat
   ```

5. **Open browser**: http://localhost:3000

That's it! You should see the chat interface.

## Manual Start (More Control)

### Terminal 1 - Backend:
```cmd
cd backend
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2 - Frontend:
```cmd
cd frontend
npm run dev
```

## First Time Chat

1. Go to http://localhost:3000
2. Type: "What products do you offer?"
3. The agent will search the FAQ and respond!

## Troubleshooting

### Backend won't start
- Make sure AWS credentials are set
- Check if port 8000 is available

### Frontend won't start
- Delete `node_modules` and run `npm install` again
- Check if port 3000 is available

### Agent not responding
- Verify your agent ARN in `backend/app.py` (line 23)
- Check AWS credentials have Bedrock permissions

## What's Next?

- Read [ENTERPRISE_UI_README.md](./ENTERPRISE_UI_README.md) for full documentation
- Configure DynamoDB for session persistence
- Deploy to production

## Need Help?

Check the logs:
- Backend: Terminal window running uvicorn
- Frontend: Terminal window running vite
- Agent: `python check_logs.py`
