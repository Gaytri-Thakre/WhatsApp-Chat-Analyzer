import re #regular expression
import pandas as pd

def preprocess(data):
    # Pattern to match WhatsApp date format
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s'

    
    # Split messages and extract dates
    messages = re.split(pattern, data)[1:]
    
    
    # Clean dates
    dates = re.findall(pattern,data)
    dates = [d.strip(" -") for d in dates]
    
    # Create initial DataFrame
    df = pd.DataFrame({'user_message':messages, 'message_date':dates})
    #convert message_date type
    df['message_date'] = pd.to_datetime(df['message_date'], format='%m/%d/%y, %H:%M')
    df.rename(columns={'message_date': 'date'} ,inplace=True)
    
   
    
    # Process user and message
    users = []
    messages = []

    # Pattern to match unsaved numbers (e.g., +91 12345 67890 or similar formats)
    phone_pattern = re.compile(r'^(\+\d{2} \d{5} \d{5}|\+\d{2} \d{10}|\d{10})(?=:\s)')

    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message, 1)
        if len(entry) > 2:
            user = entry[1]
            # Check if the user is an unsaved number
            phone_match = phone_pattern.match(user)
            if phone_match:
                # Extract just the number (remove spaces if needed)
                phone_number = phone_match.group(1).replace(' ', '')
                users.append(phone_number)
            else:
                users.append(user)
            messages.append(entry[2])
        else:
            users.append('group_notification')
            messages.append(entry[0])
    # 
    df = df.drop('user_message', axis=1)
    df['user'] = users
    df['message'] = messages
    df['year']=df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day  # Extracts day as number (1-31)
    df['hour']=df['date'].dt.hour
    df['minute']=df['date'].dt.minute
    return df