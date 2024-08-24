import re
import csv
import pandas as pd
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
import streamlit as st
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
ws=set(stopwords.words("English"))
ws.update(["um", "uh", "actually","oh","yeah","ll",",","often","let","okay"," ll "])
st.set_page_config(page_title="Project")
st.title("Main")
API_KEY= 'AIzaSyC3yFW6eJa5UWUb0dMZi2oBTx-Ad54JbBo'
def get_video_id(url):# Extract URL
    video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
    return video_id_match.group(1) if video_id_match else None

def get_video_title(video_id):
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    request = youtube.videos().list(
        part='snippet',
        id=video_id )
    response = request.execute()
    title = response['items'][0]['snippet']['title'] if response['items'] else 'Unknown Title'
    return title
def remove_stopwords(text):
    words = word_tokenize(text)
    filtered_words = [word for word in words if word.lower() not in ws]
    return ' '.join(filtered_words)

def get_video_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        st.session_state.transcript=transcript
        return transcript
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
def save_to_csv(title, transcript, filename):
    transcript_data = [{'start': entry['start'], 'text': entry['text']} for entry in transcript]
    df = pd.DataFrame(transcript_data)
    df.to_csv(filename, index=False)

    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Title:', title])
def main1():
    data="https://www.youtube.com/watch?v=jGwO_UgTS7I&list=PLoROMvodv4rMiGQp3WXShtMGgzqpfVfb"
    url = st.sidebar.text_input('Enter the YouTube video link: ',value=data,key='url_input')
    video_id = get_video_id(url)

    if not video_id:
        print('Invalid YouTube URL.')
        return

    title = get_video_title(video_id)
    transcript = get_video_transcript(video_id)

    if not transcript:
        print('No transcript available for this video.')
        return

    filename = f"{video_id}_transcript.csv"
    save_to_csv(title, transcript, filename)
    print(f'Transcript saved to {filename}')
    return filename


file=main1()
import pyautogui
if file:  
    transcript_df = pd.read_csv(file)
    transcript_df["text"]=transcript_df["text"].apply(remove_stopwords)
    st.write(transcript_df)
    st.session_state.transcript_df=transcript_df
    if st.sidebar.button("Reset"):
        pyautogui.hotkey("ctrl","F5")
else:
    st.write("Failed to retrieve the transcript file.")
    if st.sidebar.button("Reset"):
        pyautogui.hotkey("ctrl","F5")



