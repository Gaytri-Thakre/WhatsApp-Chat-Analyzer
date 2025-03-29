from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import re
import emoji
def fetch_stats(selected_user, df):
    if selected_user == "Overall":
        # Get overall stats
        num_messages = df.shape[0]
        words = sum(df['message'].str.split().str.len())
        num_media = df[df['message'] == '<Media omitted>\n'].shape[0]
        links = df[df['message'].str.contains('http')].shape[0]
    else:
        # Get user-specific stats
        num_messages = df[df['user'] == selected_user].shape[0]
        words = sum(df[df['user'] == selected_user]['message'].str.split().str.len())
        num_media = df[(df['user'] == selected_user) & 
                      (df['message'] == '<Media omitted>')].shape[0]
        links = df[(df['user'] == selected_user) & 
                  (df['message'].str.contains('http'))].shape[0]
    
    return num_messages, words, num_media, links



def mostBusyUser(df):
    # Get top users by message count
    busy_df = df['user'].value_counts().head()
    name = busy_df.index.tolist()  # Convert to list
    count = busy_df.values.tolist()  # Convert to list
    
    # Calculate percentage distribution (FIXED ERRORS HERE)
    ActivityDistribution = (
        df['user'].value_counts()  # Corrected to value_counts()
        .div(df.shape[0])         # Divide by total messages
        .mul(100)                 # Convert to percentage
        .round(2)                 # Round to 2 decimal places
        .reset_index()            # Convert to DataFrame
        .rename(columns={'index': 'name', 'user': 'percent'})  # Corrected 'column' to 'columns'
    )
    
    return name, count, ActivityDistribution



def create_wordcloud(selected_user, df):
    # Filter for specific user if not 'Overall'
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    # Read stop words
    with open('stop_hinglish.txt', 'r') as f:
        stop_words = f.read().split()  # Convert to list of words
    
    # Filter out group notifications and media messages
    temp = df[(df['user'] != 'group_notification') & 
              (df['message'] != '<Media omitted>\n') & 
              (df['message'] != 'This message was deleted\n')]
    
    def remove_stop_words(message):
        y = []
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)
    
    # Apply stop word removal
    temp['cleaned_message'] = temp['message'].apply(remove_stop_words)
    
    # Generate word cloud
    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    df_wc = wc.generate(' '.join(temp['cleaned_message']))
    
    return df_wc


def most_common_words(selected_user,df):
    f= open('stop_hinglish.txt','r')
    stop_words = f.read()
    if selected_user!='Overall':
        df=df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp =temp[temp['message'].ne('<Media omitted>\n') & temp['message'].ne('This message was deleted\n')]

    words = []

    for message in temp['message']:
        cleaned_message = re.sub(r'[^a-zA-Z\s]', '', message.lower())  # Remove numbers & punctuation
        for word in cleaned_message.split():
            if word not in stop_words:
                words.append(word)
    
    return_df = pd.DataFrame(Counter(words).most_common(20))
    return return_df

def most_common_emoji(selected_user,df):
    if selected_user!='Overall':
        df=df[df['user'] == selected_user]

    emojis=[]
    for message in df['message']:
        emojis.extend([c for c in message if emoji.is_emoji(c)])
        
    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    return emoji_df


def monthly_timeline(selected_user,df):
    if(selected_user!= 'Overall'):
        df = df[df['user']==selected_user]
    timeline= df.groupby(['year','month_num','month']).count()['message'].reset_index()
    time=[]
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]) )
    timeline['time']=time

    return timeline

def daily_timeline(selected_user,df) :
    if(selected_user!= 'Overall'):
        df = df[df['user']==selected_user]
    
    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline


def week_timeline(selected_user,df) :
    if(selected_user!= 'Overall'):
        df = df[df['user']==selected_user]
    
    return df['day_name'].value_counts()

def month_timeline(selected_user,df):
    if selected_user !='Overall':
        df = df[df['user']==selected_user]
    return df['month'].value_counts()

def activity_heatmap(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap