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
if 'hint_word' not in st.session_state:
    st.session_state.hint_word = None
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

# Button to get a new word
if st.button('Yeni bir kelime getir 🔄'):
    word, img = get_new_word()
    turkish_word = translate_deepl(word)
    st.session_state.current_word = word
    st.session_state.current_image = img
    st.session_state.turkish_current_word = turkish_word
    st.session_state.hint_word = ['*' for _ in turkish_word]  # Initialize hint
    st.session_state.revealed_indices = set()

# Display image
if st.session_state.current_image:
    st.image(st.session_state.current_image, caption="Bu fotograftaki sey nedir?")

# Display hidden word and button to reveal letters
if st.session_state.hint_word:
    st.write(f"Kelime: **{''.join(st.session_state.hint_word)}**")

    if st.button('Bir harf göster 🔍'):
        turkish_word = st.session_state.turkish_current_word
        hidden_indices = [i for i in range(len(turkish_word)) if i not in st.session_state.revealed_indices]
        if hidden_indices:
            random_index = random.choice(hidden_indices)
            st.session_state.hint_word[random_index] = turkish_word[random_index]
            st.session_state.revealed_indices.add(random_index)
