import logging
import os
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import dateparser
import time

logger = logging.getLogger("voice-assistant")
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_google_calendar_creds():
    """Get Google Calendar credentials, creating them if they don't exist."""
    creds = None
    token_path = 'token.json'
    credentials_path = 'credentials.json'

    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        except Exception as e:
            logger.error(f"Error loading credentials: {e}")
            os.remove(token_path)
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                logger.error(f"Error refreshing token: {e}")
                os.remove(token_path)
                creds = None

        if not creds:
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(
                    "No credentials.json found. Please download it from Google Cloud Console "
                    "and place it in the root directory."
                )
            
            import socket
            def find_free_port():
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', 0))
                    s.listen(1)
                    port = s.getsockname()[1]
                return port

            port = find_free_port()
            redirect_uri = f'http://localhost:{port}'
            
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, 
                SCOPES,
                redirect_uri=redirect_uri
            )
            creds = flow.run_local_server(
                port=port,
                prompt='consent',
                authorization_prompt_message="Please visit this URL to authorize Graham: "
            )

        with open(token_path, 'w') as token:
            token.write(creds.to_json())
            logger.info("Saved new credentials to token.json")

    return creds

def parse_natural_date(date_str: str) -> str:
    """Convert natural language date to YYYY-MM-DD format."""
    if not date_str:
        return datetime.now().strftime('%Y-%m-%d')
        
    try:
        date_str = date_str.lower().strip()
        now = datetime.now()
        
        if 'tonight' in date_str or 'this evening' in date_str:
            return now.strftime('%Y-%m-%d')
            
        if 'next week' in date_str:
            return (now + timedelta(days=7)).strftime('%Y-%m-%d')
            
        if 'next' in date_str:
            day_name = date_str.replace('next', '').strip()
            current_day = now.weekday()
            target_day = time.strptime(day_name, '%A').tm_wday
            days_ahead = target_day - current_day
            if days_ahead <= 0:
                days_ahead += 7
            return (now + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
            
        parsed_date = dateparser.parse(date_str, settings={
            'RELATIVE_BASE': now,
            'PREFER_DATES_FROM': 'future',
            'PREFER_DAY_OF_MONTH': 'current'
        })
        
        if parsed_date:
            if parsed_date < now and any(day in date_str.lower() for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']):
                parsed_date += timedelta(days=7)
            return parsed_date.strftime('%Y-%m-%d')
            
        raise ValueError(f"Could not parse date: {date_str}")
    except Exception as e:
        logger.error(f"Error parsing date {date_str}: {str(e)}")
        return date_str

async def _check_calendar_availability(date: str) -> list:
    """Internal function to check calendar availability."""
    try:
        formatted_date = parse_natural_date(date)
        
        creds = get_google_calendar_creds()
        service = build('calendar', 'v3', credentials=creds)
        
        date_obj = datetime.strptime(formatted_date, '%Y-%m-%d')
        time_min = date_obj.isoformat() + 'Z'
        time_max = (date_obj + timedelta(days=1)).isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        return events_result.get('items', [])
    except Exception as e:
        logger.error(f"Error in _check_calendar_availability: {str(e)}")
        raise

async def _create_calendar_event(date: str, time: str, duration: int, title: str, description: str = "") -> dict:
    """Internal function to create a calendar event."""
    try:
        creds = get_google_calendar_creds()
        service = build('calendar', 'v3', credentials=creds)
        
        local_tz = datetime.now().astimezone().tzinfo
        
        start_datetime = datetime.strptime(f"{date} {time}", '%Y-%m-%d %H:%M').replace(tzinfo=local_tz)
        end_datetime = start_datetime + timedelta(minutes=duration)
        
        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': str(local_tz),
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': str(local_tz),
            },
        }
        
        return service.events().insert(calendarId='primary', body=event).execute()
    except Exception as e:
        logger.error(f"Error creating calendar event: {str(e)}")
        raise

def format_date_for_display(date_str: str) -> str:
    """Convert YYYY-MM-DD to natural language date."""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        
        if date_obj.date() == today.date():
            return "today"
        elif date_obj.date() == tomorrow.date():
            return "tomorrow"
        else:
            return date_obj.strftime("%A, %B %d")
    except Exception as e:
        logger.error(f"Error formatting date {date_str}: {str(e)}")
        return date_str

def format_time_for_display(time_str: str) -> str:
    """Convert HH:MM to natural 12-hour format."""
    try:
        time_obj = datetime.strptime(time_str, '%H:%M')
        return time_obj.strftime("%I:%M %p").lstrip("0").lower()
    except Exception as e:
        logger.error(f"Error formatting time {time_str}: {str(e)}")
        return time_str 