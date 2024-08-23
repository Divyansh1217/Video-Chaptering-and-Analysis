import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download("vader_lexicon")
import pandas as pd
import streamlit as st
data=st.session_state.get('transcript_df',"No data Found")
data = data.dropna()
sentiments = SentimentIntensityAnalyzer()
data["Positive"] = [sentiments.polarity_scores(i)["pos"] for i in data["text"]]
data["Negative"] = [sentiments.polarity_scores(i)["neg"] for i in data["text"]]
data["Neutral"] = [sentiments.polarity_scores(i)["neu"] for i in data["text"]]
data['Compound'] = [sentiments.polarity_scores(i)["compound"] for i in data["text"]]
score = data["Compound"].values
sentiment = []
for i in score:
    if i >= 0.05 :
        sentiment.append('Positive')
    elif i <= -0.05 :
        sentiment.append('Negative')
    else:
        sentiment.append('Neutral')

data["Sentiment"] = sentiment
st.write(data)
st.write(data["Sentiment"].value_counts())
from better_profanity import profanity
profanity.load_censor_words()
safe=st.session_state.get('transcript','Not Found')
if profanity.contains_profanity(safe):
    st.sidebar.write("Not Safe to read")
else:
    st.sidebar.write("Safe to read")

