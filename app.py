import streamlit as st
import requests
import random
from gtts import gTTS
import os
import streamlit.components.v1 as components

UNSPLASH_ACCESS_KEY = st.secrets['general']['unsplash_api_key']
DEEPL_API_KEY = st.secrets['general']['deepl_api_key']
PIXABAY_API_KEY = st.secrets['general']['pixabay_api_key']

# Load the words ONCE
@st.cache_data
def load_words():
    with open('word_list.txt', 'r') as f:
        words = f.read().splitlines()
    return words

def get_unsplash_image(word):
    url = f"https://api.unsplash.com/search/photos?query={word}&client_id={UNSPLASH_ACCESS_KEY}"
    response = requests.get(url)
    data = response.json()
    if data.get('results'):
        return data['results'][0]['urls']['small']
    else:
        return None

def get_pixabay_image(query):
    url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={query}&image_type=photo"
    response = requests.get(url)
    data = response.json()
    if data['hits']:
        return data['hits'][0]['largeImageURL']
    else:
        return None

def translate_deepl(text):
    url = "https://api-free.deepl.com/v2/translate"
    params = {
        "auth_key": DEEPL_API_KEY,
        "text": text,
        "source_lang": "EN",
        "target_lang": "TR"
    }
    response = requests.post(url, data=params)
    result = response.json()
    return result['translations'][0]['text']

# --- Streamlit app ---
st.title("Alfabe:")
st.write("A B C Ç D E F G Ğ H")
st.write("İ I J K L M N O Ö")
st.write("P R S Ş T U Ü V Y Z")

words = load_words()

# Initialize session state
if 'used_words' not in st.session_state:
    st.session_state.used_words = []
if 'current_word' not in st.session_state:
    st.session_state.current_word = None
if 'current_image' not in st.session_state:
    st.session_state.current_image = None
if 'turkish_current_word' not in st.session_state:
    st.session_state.turkish_current_word = None
if 'revealed_indices' not in st.session_state:
    st.session_state.revealed_indices = set()

def get_new_word():
    available_words = list(set(words) - set(st.session_state.used_words))
    if not available_words:
        st.success("Bütün kelimeleri kullandın! 🎉")
        return None, None
    
    new_word = random.choice(available_words)
    image_url = get_unsplash_image(new_word) # get_pixabay_image(new_word)
    if image_url:
        st.session_state.used_words.append(new_word)
        return new_word, image_url
    else:
        # If no image, try again recursively
        return get_new_word()

def get_hint_display():
    if not st.session_state.turkish_current_word:
        return ""
    
    hint = []
    for i, char in enumerate(st.session_state.turkish_current_word):
        if i in st.session_state.revealed_indices:
            hint.append(char)
        else:
            hint.append('*')
    return ''.join(hint)

# New word button
if st.button('Yeni bir resim getir 🔄'):
    word, img = get_new_word()
    if word and img:
        turkish_word = translate_deepl(word)
        st.session_state.current_word = word
        st.session_state.current_image = img
        st.session_state.turkish_current_word = turkish_word
        st.session_state.revealed_indices = set()  # Reset revealed indices

# Display the image
if st.session_state.current_image:
    st.image(st.session_state.current_image, caption="Bu fotograftaki sey nedir?")

# Display the hint word
if st.session_state.turkish_current_word:
    hint_display = get_hint_display()
    st.write(f"Kelime: {hint_display}")

    # Reveal a random letter
    if st.button('Bir harf göster 🔍'):
        turkish_word = st.session_state.turkish_current_word
        hidden_indices = [i for i in range(len(turkish_word)) if i not in st.session_state.revealed_indices]
        
        if hidden_indices:  # Only reveal a letter if there are hidden letters
            random_index = random.choice(hidden_indices)
            st.session_state.revealed_indices.add(random_index)
    st.markdown("---")
    if st.button('Seslendir:'):
        turkish_word = st.session_state.turkish_current_word
        tts = gTTS(text=turkish_word, lang='tr')
        tts.save("output.mp3")
        audio_file = open('output.mp3', 'rb')
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format='audio/mp3')

st.markdown("---")

st.subheader("🎤 Sesini kaydet ve dinle")

# Embed HTML for audio recording and playback
components.html("""
    <audio id="player" controls></audio>
    <br>
    <button onclick="startRecording()">Kayda Başla</button>
    <button onclick="stopRecording()">Kaydı Durdur</button>

    <script>
    let mediaRecorder;
    let audioChunks = [];

    async function startRecording() {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.start();
        
        mediaRecorder.ondataavailable = function(event) {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = function() {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const audioUrl = URL.createObjectURL(audioBlob);
            document.getElementById("player").src = audioUrl;
            audioChunks = [];
        };

        console.log("Recording started");
    }

    function stopRecording() {
        if (mediaRecorder && mediaRecorder.state !== "inactive") {
            mediaRecorder.stop();
            console.log("Recording stopped");
        }
    }
    </script>
""", height=400)