import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns

st.sidebar.title("WhatsApp Chat Analyzer")
uploaded_file = st.sidebar.file_uploader("Choose a file")

if uploaded_file is not None:
    data = uploaded_file.getvalue().decode("utf-8-sig")
    df = preprocessor.preprocess(data)
    
    # st.dataframe(df)  # Displays the exact structure you requested
    
    
    
#    fetch unique users
    user_list = df['user'].unique().tolist()
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0,"Overall")
    selected_user = st.sidebar.selectbox("Show analysis with respect to",user_list)
    if st.sidebar.button("Show Analysis"):
        # Get statistics
        num_messages, words, num_media, links = helper.fetch_stats(selected_user, df)
        
        # Display stats in columns
        st.title("📈 Top Statistics")
        col1, col2= st.columns(2)
        
        with col1:
            st.header("Total Messages")
            st.title(num_messages)
            
        with col2:
            st.header("Total Words")
            st.title(words)
            
        col3, col4 = st.columns(2)
        with col3:
            st.header("Media Shared")
            st.title(num_media)
            
        with col4:
            st.header("Links Shared")
            st.title(links)

        #    plotting the monthly timelines:
        st.title('Monthly Timeline')
        timeline = helper.monthly_timeline(selected_user,df)
        fig,ax=plt.subplots()
        ax.plot(timeline['time'],timeline['message'])
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # plotting the daily timeline:
        st.title('Daily Timeline')
        daily_timeline = helper.daily_timeline(selected_user,df)
        fig,ax=plt.subplots()
        ax.plot(daily_timeline['only_date'],daily_timeline['message'],color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)


        # Activity
        st.title("Activity Map")
        col1,col2 = st.columns(2)
        
        with col1:
            busy_day = helper.week_timeline(selected_user,df)
            st.header("Most Busy day")
            fig,ax=plt.subplots()
            ax.bar(busy_day.index,busy_day.values)
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        with col2:
            busy_month = helper.month_timeline(selected_user,df)
            st.header("Most Busy Month")
            fig,ax=plt.subplots()
            ax.bar(busy_month.index,busy_month.values,color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        st.title("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user,df)
        fig,ax = plt.subplots()
        ax = sns.heatmap(user_heatmap)
        st.pyplot(fig)

        # finding busiest users in group(Group Level)
        

        if selected_user == "Overall":
            st.title('Most Busy Users 📊')
            name,count,newdf = helper.mostBusyUser(df)
            
            fig,ax = plt.subplots()
           
            col1,col2 = st.columns(2)
            with col1:
                ax.bar(name,count)
                plt.xticks(rotation="vertical")
                st.pyplot(fig)
            with col2:
                st.dataframe(newdf)
        # ------------#
        # WordCloud
        st.title("Word Cloud 🌈")
        df_wc = helper.create_wordcloud(selected_user,df)
        fig,ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)
            

        # most common words
        st.title('📊 Most Common Words')
        most_common_df = helper.most_common_words(selected_user,df)
        
        fig,ax = plt.subplots()

        ax.barh(most_common_df[0],most_common_df[1])
        plt.xticks(rotation="vertical")
        
        st.pyplot(fig)

        # Emoji Analysis
        st.title(' 😍 Emoji Analysis')
        emoji_df = helper.most_common_emoji(selected_user, df)

        # Ensure proper column names
        emoji_df.columns = ['Emoji', 'Count']

        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)

        with col2:
            # Set a font that supports emojis
            plt.rcParams['font.family'] = 'Segoe UI Emoji'  # Windows emoji font
            # Alternatively for other systems: 'Apple Color Emoji' (Mac), 'Noto Color Emoji' (Linux)
            
            fig, ax = plt.subplots(figsize=(10, 10))
            
            # Only show top N emojis (others grouped as "Others")
            top_n = 8  # Reduced to make more readable
            if len(emoji_df) > top_n:
                others_sum = emoji_df['Count'].iloc[top_n:].sum()
                top_emojis = emoji_df.head(top_n).copy()
                top_emojis = pd.concat([top_emojis, 
                                    pd.DataFrame({'Emoji': ['Others'], 'Count': [others_sum]})])
            else:
                top_emojis = emoji_df.copy()
            
            # Explode the largest slice for emphasis
            explode = [0.1 if i == top_emojis['Count'].idxmax() else 0 for i in range(len(top_emojis))]
            
            # Create pie chart with better formatting
            wedges, texts, autotexts = ax.pie(
                top_emojis['Count'],
                labels=top_emojis['Emoji'],
                autopct=lambda p: f'{p:.1f}%' if p > 5 else '',  # Only show % for >5% slices
                startangle=90,
                explode=explode,
                shadow=True,
                textprops={'fontsize': 14},
                wedgeprops={'linewidth': 1, 'edgecolor': 'white'}
            )
            
            # Equal aspect ratio
            ax.axis('equal')
            
            # Add legend instead of labels if too crowded
            if len(top_emojis) > 5:
                ax.legend(wedges, top_emojis['Emoji'],
                        title="Emojis",
                        loc="center left",
                        bbox_to_anchor=(1, 0, 0.5, 1))
                # Clear the labels if using legend
                for text in texts:
                    text.set_text('')
            
            plt.title(f'Top {min(top_n, len(emoji_df))} Emojis Used', pad=20, fontsize=16)
            plt.tight_layout()
            st.pyplot(fig)
                            
                                
                                

