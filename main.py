#!/usr/bin/env python3
import os
import time
import threading
import webbrowser
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs, urlencode
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
REDIRECT_URI = os.getenv("STRAVA_REDIRECT_URI")
ACCESS_TOKEN = os.getenv("STRAVA_ACCESS_TOKEN")
REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")
EXPIRES_AT = int(os.getenv("STRAVA_EXPIRES_AT") or "0")

AUTH_URL = "https://www.strava.com/oauth/authorize"
TOKEN_URL = "https://www.strava.com/oauth/token"

auth_code_result: dict[str, str | None] = {"code": None}

class RedirectHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        query_params = parse_qs(parsed.query)
        code = query_params.get("code", [None])[0] if "code" in query_params else None
        auth_code_result["code"] = code
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        if code:
            self.wfile.write(b"<h1>Authorization successful! You can close this window.</h1>")
        else:
            self.wfile.write(b"<h1>Authorization failed. No code received.</h1>")

def start_local_server():
    httpd = HTTPServer(("localhost", 8080), RedirectHandler)
    print("🔌 Waiting for Strava redirect at http://localhost:8080/exchange_token ...")
    httpd.handle_request()
    httpd.server_close()

def perform_browser_auth():
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "approval_prompt": "force",
        "scope": "read,activity:read_all"
    }

    url = f"{AUTH_URL}?{urlencode(params)}"
    webbrowser.open(url)
    thread = threading.Thread(target=start_local_server)
    thread.start()
    thread.join()
    return auth_code_result["code"]

def exchange_code_for_token(code):
    resp = requests.post(TOKEN_URL, data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code"
    })
    resp.raise_for_status()
    return resp.json()

def refresh_access_token(refresh_token):
    resp = requests.post(TOKEN_URL, data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    })
    resp.raise_for_status()
    return resp.json()

def save_token_info(data):
    # Read existing .env file
    env_path = ".env"
    with open(env_path, "r") as f:
        lines = f.readlines()
    
    # Update token values
    updated_lines = []
    for line in lines:
        if line.startswith("STRAVA_ACCESS_TOKEN="):
            updated_lines.append(f"STRAVA_ACCESS_TOKEN={data['access_token']}\n")
        elif line.startswith("STRAVA_REFRESH_TOKEN="):
            updated_lines.append(f"STRAVA_REFRESH_TOKEN={data['refresh_token']}\n")
        elif line.startswith("STRAVA_EXPIRES_AT="):
            updated_lines.append(f"STRAVA_EXPIRES_AT={data['expires_at']}\n")
        else:
            updated_lines.append(line)
    
    # Write back to .env file
    with open(env_path, "w") as f:
        f.writelines(updated_lines)
    
    print("\n✅ Token values saved to .env file:")
    print(f"   STRAVA_ACCESS_TOKEN={data['access_token'][:20]}...")
    print(f"   STRAVA_REFRESH_TOKEN={data['refresh_token'][:20]}...")
    print(f"   STRAVA_EXPIRES_AT={data['expires_at']}  # {time.ctime(data['expires_at'])}")

def main():
    now = int(time.time())
    if ACCESS_TOKEN and REFRESH_TOKEN and EXPIRES_AT > 0:
        if EXPIRES_AT - now > 60:
            print("✅ Token still valid. No action needed.")
            return
        else:
            print("🔄 Token expired. Refreshing...")
            data = refresh_access_token(REFRESH_TOKEN)
            save_token_info(data)
            return

    print("🌐 No valid tokens. Starting full OAuth flow...")
    code = perform_browser_auth()
    if not code:
        print("❌ Failed to get authorization code.")
        return

    data = exchange_code_for_token(code)
    save_token_info(data)

if __name__ == "__main__":
    main()
