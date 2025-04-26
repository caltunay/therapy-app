import streamlit as st
import requests
import random

UNSPLASH_ACCESS_KEY = st.secrets['general']['unsplash_api_key']

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

# --- Streamlit app ---
st.title("Konusursun, konusursuuuuuuun!! 🗣️")

words = load_words()

# Initialize session state
if 'used_words' not in st.session_state:
    st.session_state.used_words = []
if 'current_word' not in st.session_state:
    st.session_state.current_word = None
if 'current_image' not in st.session_state:
    st.session_state.current_image = None

def get_new_word():
    available_words = list(set(words) - set(st.session_state.used_words))
    if not available_words:
        st.success("Bütün kelimeleri kullandın! 🎉")
        return None, None
    
    new_word = random.choice(available_words)
    image_url = get_unsplash_image(new_word)
    if image_url:
        st.session_state.used_words.append(new_word)
        return new_word, image_url
    else:
        # If no image, try again recursively
        return get_new_word()

# Button
if st.button('Yeni bir kelime getir 🔄'):
    word, img = get_new_word()
    st.session_state.current_word = word
    st.session_state.current_image = img

# Display
if st.session_state.current_image:
    st.image(st.session_state.current_image, caption="Bu fotograftaki sey nedir?")
# elif st.session_state.current_word is None:
    # st.write("Bütün kelimeler kullanıldı veya başlamak için butona basın.")
