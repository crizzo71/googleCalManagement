# Google Calendar Meeting Manager

A command-line tool to connect to your Google Calendar and manage meetings efficiently.

## Features

- **List Events**: View upcoming meetings with customizable date ranges
- **Create Events**: Add new meetings with attendees and descriptions
- **Update Events**: Modify existing calendar events
- **Delete Events**: Remove unwanted meetings
- **OAuth2 Authentication**: Secure connection to your Google Calendar

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Enable Google Calendar API

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API
4. Configure the OAuth consent screen
5. Create OAuth 2.0 Client ID for a desktop application
6. Download the credentials and save as `credentials.json` in this directory

### 3. First Time Authentication

Run any command to trigger the authentication flow:

```bash
python calendar_manager.py list
```

This will open a browser window for you to authorize the application.

## Usage

### List Upcoming Events

```bash
# Show next 10 events in the next 7 days
python calendar_manager.py list

# Show next 20 events in the next 14 days
python calendar_manager.py list --max 20 --days 14
```

### Create a New Event

```bash
python calendar_manager.py create "Team Meeting" "2024-01-15T14:00:00" "2024-01-15T15:00:00" \
  --description "Weekly team sync" \
  --attendees john@example.com jane@example.com
```

### Update an Existing Event

```bash
python calendar_manager.py update EVENT_ID \
  --title "Updated Meeting Title" \
  --start "2024-01-15T15:00:00" \
  --end "2024-01-15T16:00:00"
```

### Delete an Event

```bash
python calendar_manager.py delete EVENT_ID
```

## DateTime Format

Use ISO 8601 format for dates and times: `YYYY-MM-DDTHH:MM:SS`

Examples:
- `2024-01-15T14:30:00` (January 15, 2024 at 2:30 PM)
- `2024-12-31T23:59:59` (December 31, 2024 at 11:59 PM)

## Files

- `calendar_manager.py` - Main application
- `requirements.txt` - Python dependencies
- `credentials.json` - Google OAuth credentials (you need to download this)
- `token.pickle` - Stored authentication tokens (created automatically)

## Security Notes

- Keep `credentials.json` secure and never commit it to version control
- The `token.pickle` file contains access tokens - treat it as sensitive data
- This tool only requests calendar access permissions