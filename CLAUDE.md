# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Strava OAuth authentication helper tool that manages the OAuth 2.0 flow for Strava API access. It handles initial authentication, token storage, and automatic token refresh.

## Development Commands

Run the authentication tool:
```bash
python main.py
```

Install dependencies using uv:
```bash
uv pip install -e .
```

## Code Architecture

Single-file Python application (`main.py`) with the following key components:

1. **OAuth Flow Handler**: Manages the complete OAuth 2.0 authentication cycle
   - `perform_browser_auth()`: Opens browser for user authorization
   - `exchange_code_for_token()`: Exchanges authorization code for tokens
   - `refresh_access_token()`: Refreshes expired access tokens

2. **Local HTTP Server**: Captures OAuth redirect callbacks on `localhost:8080`

3. **Token Management**: Checks token expiry and automatically refreshes when needed

## Environment Configuration

The tool requires these environment variables in `.env`:
- `STRAVA_CLIENT_ID`: Your Strava app client ID
- `STRAVA_CLIENT_SECRET`: Your Strava app client secret
- `STRAVA_ACCESS_TOKEN`: Current access token (managed by the tool)
- `STRAVA_REFRESH_TOKEN`: Refresh token for obtaining new access tokens
- `STRAVA_TOKEN_EXPIRES_AT`: Unix timestamp of token expiration

## Key Dependencies

- `python-dotenv`: Environment variable management
- `requests`: HTTP client for API calls
- Python 3.11+