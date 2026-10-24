"""Deploy script with UTF-8 encoding support"""
import os
import sys
import subprocess

# Set UTF-8 encoding
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["AGENTCORE_SUPPRESS_RECOMMENDATION"] = "1"

# Run deployment
result = subprocess.run(
    [sys.executable, "-m", "bedrock_agentcore_starter_toolkit.cli.cli", "deploy"],
    cwd=os.path.dirname(os.path.abspath(__file__)),
    encoding="utf-8",
    errors="replace"
)

sys.exit(result.returncode)
