import re
import pandas as pd
from datetime import datetime

def preprocess(data):
    if not data or not isinstance(data, str):
        raise ValueError("Input data must be a non-empty string")

    try:
        # More comprehensive WhatsApp date pattern
        pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s'
        
        # Validate we have matching dates and messages
        dates = re.findall(pattern, data)
        if not dates:
            raise ValueError("No WhatsApp timestamps found - invalid chat format")
            
        messages = re.split(pattern, data)[1:]
        if len(dates) != len(messages):
            raise ValueError("Mismatch between dates and messages count")

        # Clean dates and create DataFrame
        dates = [d.strip(" -") for d in dates]
        df = pd.DataFrame({'user_message': messages, 'message_date': dates})
        
        # More robust date parsing with fallback
        try:
            df['message_date'] = pd.to_datetime(df['message_date'], format='%m/%d/%y, %H:%M')
        except ValueError:
            df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %H:%M')
            
        df.rename(columns={'message_date': 'date'}, inplace=True)

        # Process users and messages
        users = []
        messages_clean = []
        phone_pattern = re.compile(r'^(\+\d{2}[ -]?\d{5}[ -]?\d{5}|\+\d{2}[ -]?\d{10}|\d{10})(?=:\s)')

        for message in df['user_message']:
            entry = re.split(r'([\w\W]+?):\s', message, 1)
            if len(entry) > 2:
                user = entry[1]
                if phone_match := phone_pattern.match(user):
                    users.append(phone_match.group(1).replace(' ', ''))
                else:
                    users.append(user)
                messages_clean.append(entry[2])
            else:
                users.append('group_notification')
                messages_clean.append(entry[0])

        df = df.drop('user_message', axis=1)
        df['user'] = users
        df['message'] = messages_clean
        
        # Date features
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month_name()
        df['day'] = df['date'].dt.day
        df['hour'] = df['date'].dt.hour
        df['minute'] = df['date'].dt.minute
        df['month_num'] = df['date'].dt.month
        df['only_date'] = df['date'].dt.date
        df['day_name'] = df['date'].dt.day_name()

        # Period column
        df['period'] = df['hour'].apply(
            lambda hour: f"{hour}-{hour+1}" if hour != 23 else "23-00"
        )

        return df

    except Exception as e:
        raise ValueError(f"Error processing WhatsApp data: {str(e)}") from e