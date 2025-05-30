Looking at your Strava auth code and the MCP server structure, there are several approaches to integrate Strava authentication into an MCP server. Let me break down the key considerations and options:

## Key Challenges with MCP + OAuth

1. **MCP servers run as background processes** - they don't have direct user interaction capabilities
2. **OAuth requires browser redirects** - which MCP servers can't handle directly
3. **Token management** - need persistent storage and refresh logic
4. **Security** - tokens need to be stored securely

## Approach Options

### 1. **Separate Auth Setup (Recommended)**

Keep authentication as a separate setup step, similar to what you have now:

```python
# auth_setup.py (separate from MCP server)
# Your existing main.py code goes here
```

Then modify your MCP server to read tokens from the `.env` file:

```python
# In your MCP server
import os
from dotenv import load_dotenv
import requests
import time

class StravaClient:
    def __init__(self):
        load_dotenv()
        self.client_id = os.getenv("STRAVA_CLIENT_ID")
        self.client_secret = os.getenv("STRAVA_CLIENT_SECRET")
        self.access_token = os.getenv("STRAVA_ACCESS_TOKEN")
        self.refresh_token = os.getenv("STRAVA_REFRESH_TOKEN")
        self.expires_at = int(os.getenv("STRAVA_EXPIRES_AT", "0"))
    
    def ensure_valid_token(self):
        """Refresh token if needed"""
        if time.time() >= self.expires_at - 300:  # Refresh 5 mins early
            self.refresh_access_token()
    
    def refresh_access_token(self):
        # Your refresh logic here
        pass
    
    def get_activities(self, per_page=50):
        self.ensure_valid_token()
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(
            "https://www.strava.com/api/v3/athlete/activities",
            headers=headers,
            params={"per_page": per_page}
        )
        return response.json()
```

### 2. **MCP Tool for Auth Status**

Add an MCP tool to check/report authentication status:

```python
@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="check_strava_auth",
            description="Check Strava authentication status and token validity",
            inputSchema={"type": "object", "properties": {}}
        ),
        # ... other tools
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "check_strava_auth":
        client = StravaClient()
        if not client.access_token:
            return {"status": "not_authenticated", 
                   "message": "Run python auth_setup.py to authenticate"}
        elif time.time() >= client.expires_at:
            return {"status": "expired", 
                   "message": "Token expired. Run python auth_setup.py to refresh"}
        else:
            return {"status": "valid", 
                   "expires_at": time.ctime(client.expires_at)}
```

### 3. **Enhanced Token Management**

Create a token manager that handles all the OAuth complexity:

```python
# token_manager.py
import os
import time
import requests
from typing import Optional, Dict, Any

class StravaTokenManager:
    def __init__(self, env_file: str = ".env"):
        self.env_file = env_file
        self.load_tokens()
    
    def load_tokens(self):
        # Load from .env file
        pass
    
    def save_tokens(self, token_data: Dict[str, Any]):
        # Update .env file with new tokens
        pass
    
    def get_valid_token(self) -> Optional[str]:
        """Returns a valid access token, refreshing if necessary"""
        if not self.access_token or not self.refresh_token:
            return None
        
        if time.time() >= self.expires_at - 300:  # 5 min buffer
            if self.refresh_token_if_needed():
                return self.access_token
            return None
        
        return self.access_token
    
    def refresh_token_if_needed(self) -> bool:
        """Refresh the token and save to .env"""
        try:
            # Your refresh logic
            # Save new tokens to .env
            return True
        except Exception as e:
            print(f"Token refresh failed: {e}")
            return False
```

## Setup Workflow

1. **Initial Setup:**
   ```bash
   # User runs this once to authenticate
   python auth_setup.py
   ```

2. **MCP Server Usage:**
   ```json
   // claude_desktop_config.json
   {
     "mcpServers": {
       "workout_mcp_server": {
         "command": "uvx",
         "args": ["workout_mcp_server"],
         "env": {
           "STRAVA_ENV_PATH": "/path/to/your/.env"
         }
       }
     }
   }
   ```

## Security Considerations

1. **Environment Variables:** Store tokens in `.env` file (not in code)
2. **File Permissions:** Make sure `.env` has restricted permissions (600)
3. **Token Rotation:** Implement automatic refresh before expiration
4. **Error Handling:** Graceful degradation when auth fails

## Migration Strategy

1. Keep your existing fake data as fallback
2. Add a config flag to switch between fake/real data
3. Gradual transition:

```python
# In your MCP server
USE_STRAVA = os.getenv("USE_STRAVA", "false").lower() == "true"

def get_workouts():
    if USE_STRAVA:
        return get_strava_workouts()
    else:
        return get_fake_workouts()
```

This approach separates concerns cleanly - authentication setup remains a user-driven process, while the MCP server focuses on data retrieval and analysis. The token management happens transparently in the background.

Would you like me to elaborate on any of these approaches or help you implement a specific part?