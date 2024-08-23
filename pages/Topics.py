from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
import streamlit as st
import pandas as pd

n_topics = int(st.sidebar.text_input("Number of TOpics","10"))
n_top_words = 10
transcript_df=st.session_state.get('transcript_df',"No data Found")

tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
tf = tf_vectorizer.fit_transform(transcript_df['text'])
nmf = NMF(n_components=n_topics, random_state=42).fit(tf)
tf_feature_names = tf_vectorizer.get_feature_names_out()

def display_topics(model, feature_names, no_top_words):
    topics = []
    for topic_idx, topic in enumerate(model.components_):
        topic_words = [feature_names[i] for i in topic.argsort()[:-no_top_words - 1:-1]]
        topics.append(" ".join(topic_words))
    return topics



def Topic_distribution():
    topic_distribution = nmf.transform(tf)

    topic_distribution_trimmed = topic_distribution[:len(transcript_df)]

    transcript_df['dominant_topic'] = topic_distribution_trimmed.argmax(axis=1)
    logical_breaks = []

    for i in range(1, len(transcript_df)):
        if transcript_df['dominant_topic'].iloc[i] != transcript_df['dominant_topic'].iloc[i - 1]:
            logical_breaks.append(transcript_df['start'].iloc[i])
    threshold = 60  
    consolidated_breaks = []
    last_break = None

    for break_point in logical_breaks:
        if last_break is None or break_point - last_break >= threshold:
            consolidated_breaks.append(break_point)
            last_break = break_point
    final_chapters = []
    last_chapter = (consolidated_breaks[0], transcript_df['dominant_topic'][0])

    for break_point in consolidated_breaks[1:]:
        current_topic = transcript_df[transcript_df['start'] == break_point]['dominant_topic'].values[0]
        if current_topic == last_chapter[1]:
            last_chapter = (last_chapter[0], current_topic)
        else:
            final_chapters.append(last_chapter)
            last_chapter = (break_point, current_topic)

    final_chapters.append(last_chapter)
    chapter_points = []
    chapter_names = []

    for i, (break_point, topic_idx) in enumerate(final_chapters):
        chapter_time = pd.to_datetime(break_point, unit='s').strftime('%H:%M:%S')
        chapter_points.append(chapter_time)

        chapter_text = transcript_df[(transcript_df['start'] >= break_point) & (transcript_df['dominant_topic'] == topic_idx)]['text'].str.cat(sep=' ')

        vectorizer = TfidfVectorizer(stop_words='english', max_features=3)
        tfidf_matrix = vectorizer.fit_transform([chapter_text])
        feature_names = vectorizer.get_feature_names_out()
        chapter_name = " ".join(feature_names)

        chapter_names.append(f"Chapter {i+1}: {chapter_name}")

    st.write("\nFinal Chapter Points with Names:")
    for time, name in zip(chapter_points, chapter_names):
        st.write(f"{time} - {name}")

Choose=st.sidebar.radio("Choose",["display_topics","Time_Final"])
if Choose=="display_topics":
    topics = display_topics(nmf, tf_feature_names, n_top_words)
    st.write("\nIdentified Topics:")
    for i, topic in enumerate(topics):
        st.write(f"Topic {i + 1}: {topic}")


else:
    Topic_distribution()
import pyautogui
if st.sidebar.button("Reset"):
        pyautogui.hotkey("ctrl","F5")