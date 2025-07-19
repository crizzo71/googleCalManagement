#!/usr/bin/env python3
"""
Google Calendar Meeting Manager

A command-line tool to connect to Google Calendar and manage meetings.
Provides functionality to list, create, update, and delete calendar events.
"""

import os
import pickle
import argparse
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar']
TOKEN_FILE = 'token.pickle'
CREDENTIALS_FILE = 'credentials.json'

class CalendarManager:
    def __init__(self):
        self.service = None
        self.authenticate()

    def authenticate(self):
        """Authenticate with Google Calendar API"""
        creds = None
        
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(CREDENTIALS_FILE):
                    print(f"Error: {CREDENTIALS_FILE} not found!")
                    print("Please download your OAuth 2.0 credentials from Google Cloud Console.")
                    return
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('calendar', 'v3', credentials=creds)
        print("Successfully authenticated with Google Calendar")

    def list_events(self, max_results: int = 10, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """List upcoming events"""
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            end_time = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                timeMax=end_time,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            if not events:
                print(f"No upcoming events found in the next {days_ahead} days.")
                return []
            
            print(f"\nUpcoming events (next {days_ahead} days):")
            print("-" * 60)
            
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                summary = event.get('summary', 'No title')
                event_id = event.get('id')
                
                if 'T' in start:
                    start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    formatted_time = start_dt.strftime('%Y-%m-%d %H:%M')
                else:
                    formatted_time = start
                
                print(f"• {formatted_time} - {summary} (ID: {event_id[:8]}...)")
            
            return events
            
        except HttpError as error:
            print(f"An error occurred: {error}")
            return []

    def create_event(self, title: str, start_time: str, end_time: str, 
                    description: str = "", attendees: List[str] = None) -> Optional[str]:
        """Create a new calendar event"""
        try:
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)
            
            event = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': start_dt.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_dt.isoformat(),
                    'timeZone': 'UTC',
                },
            }
            
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
            
            created_event = self.service.events().insert(
                calendarId='primary', body=event).execute()
            
            event_id = created_event.get('id')
            print(f"Event created successfully! ID: {event_id}")
            return event_id
            
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None
        except ValueError as error:
            print(f"Invalid datetime format: {error}")
            return None

    def update_event(self, event_id: str, title: str = None, start_time: str = None, 
                    end_time: str = None, description: str = None) -> bool:
        """Update an existing event"""
        try:
            event = self.service.events().get(calendarId='primary', eventId=event_id).execute()
            
            if title:
                event['summary'] = title
            if description is not None:
                event['description'] = description
            if start_time:
                start_dt = datetime.fromisoformat(start_time)
                event['start']['dateTime'] = start_dt.isoformat()
            if end_time:
                end_dt = datetime.fromisoformat(end_time)
                event['end']['dateTime'] = end_dt.isoformat()
            
            updated_event = self.service.events().update(
                calendarId='primary', eventId=event_id, body=event).execute()
            
            print(f"Event updated successfully! ID: {event_id}")
            return True
            
        except HttpError as error:
            print(f"An error occurred: {error}")
            return False
        except ValueError as error:
            print(f"Invalid datetime format: {error}")
            return False

    def delete_event(self, event_id: str) -> bool:
        """Delete an event"""
        try:
            self.service.events().delete(calendarId='primary', eventId=event_id).execute()
            print(f"Event deleted successfully! ID: {event_id}")
            return True
            
        except HttpError as error:
            print(f"An error occurred: {error}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Google Calendar Meeting Manager')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List events
    list_parser = subparsers.add_parser('list', help='List upcoming events')
    list_parser.add_argument('--max', type=int, default=10, help='Maximum number of events to show')
    list_parser.add_argument('--days', type=int, default=7, help='Number of days ahead to look')
    
    # Create event
    create_parser = subparsers.add_parser('create', help='Create a new event')
    create_parser.add_argument('title', help='Event title')
    create_parser.add_argument('start', help='Start time (ISO format: YYYY-MM-DDTHH:MM:SS)')
    create_parser.add_argument('end', help='End time (ISO format: YYYY-MM-DDTHH:MM:SS)')
    create_parser.add_argument('--description', default='', help='Event description')
    create_parser.add_argument('--attendees', nargs='*', help='Attendee email addresses')
    
    # Update event
    update_parser = subparsers.add_parser('update', help='Update an existing event')
    update_parser.add_argument('event_id', help='Event ID to update')
    update_parser.add_argument('--title', help='New event title')
    update_parser.add_argument('--start', help='New start time (ISO format)')
    update_parser.add_argument('--end', help='New end time (ISO format)')
    update_parser.add_argument('--description', help='New event description')
    
    # Delete event
    delete_parser = subparsers.add_parser('delete', help='Delete an event')
    delete_parser.add_argument('event_id', help='Event ID to delete')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize calendar manager
    calendar = CalendarManager()
    
    if not calendar.service:
        print("Failed to authenticate with Google Calendar")
        return
    
    # Execute commands
    if args.command == 'list':
        calendar.list_events(args.max, args.days)
    
    elif args.command == 'create':
        calendar.create_event(
            args.title, args.start, args.end, 
            args.description, args.attendees or []
        )
    
    elif args.command == 'update':
        calendar.update_event(
            args.event_id, args.title, args.start, 
            args.end, args.description
        )
    
    elif args.command == 'delete':
        calendar.delete_event(args.event_id)

if __name__ == '__main__':
    main()