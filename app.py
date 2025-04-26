import streamlit as st
import requests
import random

UNSPLASH_ACCESS_KEY = st.secrets['general']['unsplash_api_key']
DEEPL_API_KEY = st.secrets['general']['deepl_api_key']

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
st.title("Konusursun, konusursuuuuuuun!! 🗣️")

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
    image_url = get_unsplash_image(new_word)
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
if st.button('Yeni bir kelime getir 🔄'):
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