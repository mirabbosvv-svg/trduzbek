# === MILLIYGRAM - GROK ICHIDA ISHLAYDI ===
# Faqat "Run" tugmasini bosing!

import streamlit as st
import hashlib
import os
from datetime import datetime
from PIL import Image
import io
import base64

# --- Ma'lumotlar bazasi (sessiyada saqlanadi) ---
if 'users' not in st.session_state:
    st.session_state.users = {}  # {username: {password_hash, country, phone, avatar, posts}}
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'posts' not in st.session_state:
    st.session_state.posts = []  # [{user, image, caption, time, likes}]

# --- SNG mamlakatlari ---
SNG = {
    "UZ": "Oʻzbekiston", "TJ": "Tojikiston", "KZ": "Qozogʻiston",
    "KG": "Qirgʻiziston", "TM": "Turkmaniston", "AZ": "Ozarbayjon",
    "AM": "Armaniston", "BY": "Belarus", "RU": "Rossiya"
}

def is_sng_phone(phone):
    return phone.startswith(('+998', '+992', '+7', '+993', '+994', '+374', '+375'))

def is_sng_email(email):
    return any(email.lower().endswith(f".{d.lower()}") for d in SNG.keys())

def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

# --- Sahifalar ---
page = st.sidebar.selectbox("Boʻlim", ["Roʻyxatdan oʻtish", "Kirish", "Feed", "Post joylash"])

# === RO'YXATDAN O'TISH ===
if page == "Roʻyxatdan oʻtish":
    st.header("MilliyGram – Faqat biz uchun!")
    with st.form("register"):
        username = st.text_input("Username")
        email = st.text_input("Email (masalan: user@mail.uz)")
        phone = st.text_input("Telefon (+998901234567)")
        password = st.text_input("Parol", type="password")
        country = st.selectbox("Mamlakat", list(SNG.keys()), format_func=lambda x: SNG[x])
        avatar = st.file_uploader("Avatar (rasm)", type=['png', 'jpg', 'jpeg'])
        submit = st.form_submit_button("Roʻyxatdan oʻtish")

        if submit:
            if username in st.session_state.users:
                st.error("Bu username band!")
            elif not (is_sng_email(email) or is_sng_phone(phone)):
                st.error("Faqat SNG foydalanuvchilari! (.uz, .ru, +998 va h.k.)")
            else:
                avatar_b64 = None
                if avatar:
                    img = Image.open(avatar)
                    buf = io.BytesIO()
                    img.save(buf, format="PNG")
                    avatar_b64 = base64.b64encode(buf.getvalue()).decode()

                st.session_state.users[username] = {
                    'password': hash_password(password),
                    'email': email,
                    'phone': phone,
                    'country': country,
                    'avatar': avatar_b64,
                    'posts': []
                }
                st.success(f"Xush kelibsiz, {username}!")
                st.session_state.current_user = username

# === KIRISH ===
elif page == "Kirish":
    st.header("Kirish")
    username = st.text_input("Username")
    password = st.text_input("Parol", type="password")
    if st.button("Kirish"):
        if username in st.session_state.users and \
           st.session_state.users[username]['password'] == hash_password(password):
            st.session_state.current_user = username
            st.success("Muvaffaqiyatli kirish!")
        else:
            st.error("Notoʻgʻri login yoki parol")

# === POST JOYLASH ===
elif page == "Post joylash" and st.session_state.current_user:
    st.header("Yangi post")
    user = st.session_state.current_user
    caption = st.text_area("Izoh (ixtiyoriy)")
    image = st.file_uploader("Rasm yuklash", type=['png', 'jpg', 'jpeg'])
    if st.button("Joylash") and image:
        img = Image.open(image)
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        img_b64 = base64.b64encode(buf.getvalue()).decode()

        post = {
            'user': user,
            'image': img_b64,
            'caption': caption,
            'time': datetime.now().strftime("%d.%m %H:%M"),
            'likes': 0
        }
        st.session_state.posts.insert(0, post)
        st.success("Post joylandi!")

# === FEED ===
elif page == "Feed":
    st.header("MilliyGram Feed")
    if not st.session_state.posts:
        st.info("Hozircha post yoʻq. Birinchi boʻlib joylang!")
    else:
        for post in st.session_state.posts:
            with st.container():
                col1, col2 = st.columns([1, 6])
                with col1:
                    avatar_b64 = st.session_state.users[post['user']].get('avatar')
                    if avatar_b64:
                        st.image(f"data:image/png;base64,{avatar_b64}", width=50)
                    else:
                        st.image("https://via.placeholder.com/50?text=👤", width=50)
                with col2:
                    st.write(f"**{post['user']}** • {post['time']}")
                    st.image(f"data:image/jpeg;base64,{post['image']}")
                    if post['caption']:
                        st.write(post['caption'])
                    col_like, col_count = st.columns([1, 1])
                    with col_like:
                        if st.button("❤️", key=f"like_{id(post)}"):
                            post['likes'] += 1
                    with col_count:
                        st.write(f"**{post['likes']} ta yoqdi**")
                st.markdown("---")

# === FOYDALANUVCHI HOLATI ===
if st.session_state.current_user:
    user = st.session_state.current_user
    country = SNG[st.session_state.users[user]['country']]
    st.sidebar.success(f"Salom, **{user}**!")
    st.sidebar.write(f"📍 {country}")
    if st.sidebar.button("Chiqish"):
        st.session_state.current_user = None
        st.rerun()
else:
    st.sidebar.info("Iltimos, kiring yoki roʻyxatdan oʻting")

# === MilliyGram logotipi ===
st.sidebar.image("https://em-content.zobj.net/source/telegram/386/flag-uzbekistan_1f1fa-1f1ff.png", width=30)
st.sidebar.markdown("## **MilliyGram**")
st.sidebar.caption("SNG va oʻzbeklar uchun ijtimoiy tarmoq")
