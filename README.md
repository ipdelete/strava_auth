# strava_auth

A command-line tool for managing Strava OAuth 2.0 authentication. This tool handles the complete OAuth flow including initial authentication, token storage, and automatic token refresh.

## What is this?

This tool helps developers authenticate with the Strava API by:
- Managing the OAuth 2.0 authorization flow
- Storing tokens securely in a `.env` file
- Automatically refreshing expired access tokens
- Providing a simple command-line interface for authentication

## Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- Strava API application credentials

## Development Setup

1. **Create and activate a virtual environment:**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Configure environment variables:**
   ```bash
   cp env.sample .env
   ```
   Edit `.env` and add your Strava API credentials:
   - `STRAVA_CLIENT_ID`: Your Strava app client ID
   - `STRAVA_CLIENT_SECRET`: Your Strava app client secret

## Usage

Run the authentication tool:
```bash
uv run python main.py
```

The tool will:
1. Check if you have a valid access token
2. If not, open your browser for authorization
3. Capture the callback and exchange the code for tokens
4. Save the tokens to your `.env` file
5. Automatically refresh tokens when they expire

## How it Works

1. **Initial Authentication**: Opens a browser to Strava's OAuth page where you authorize the app
2. **Token Exchange**: Captures the authorization code via a local HTTP server and exchanges it for access/refresh tokens
3. **Token Storage**: Saves tokens to your `.env` file for future use
4. **Auto Refresh**: Checks token expiry on each run and refreshes automatically if needed