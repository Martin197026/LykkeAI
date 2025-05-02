# manualchat/app.py
import streamlit as st

# Helt først: konfiguration
st.set_page_config(page_title="Manual Chat", page_icon="🔧", layout="centered")

# Stil (CSS for pænere design)
st.markdown("""
    <style>
    body { font-family: 'Helvetica Neue', sans-serif; background-color: #f8f9fa; }
    .stApp { padding-top: 2rem; padding-bottom: 2rem; }
    h1, h2, h3, h4 { color: #003366; }
    .stButton>button { border-radius: 8px; background-color: #007bff; color: white; border: none; padding: 8px 16px; margin-top: 8px; margin-bottom: 8px; }
    .stCheckbox { margin-top: 10px; }
    .stTextInput>div>div>input { border-radius: 6px; }
    .stSlider>div>div>div { background-color: #007bff; }
    </style>
""", unsafe_allow_html=True)

import os
from loader import extract_chunks_from_pdf, render_pdf_page_as_image
from embedder import create_or_load_index, search_chunks
from chat import generate_answer
from store import list_manuals, load_manual_chunks, get_manual_path
from auth import init_db, register_user, login_user

# Init database
init_db()

# Login system
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Manual Chat Login")
    email = st.text_input("Email")
    password = st.text_input("Adgangskode", type="password")

    if st.button("Log ind"):
        if login_user(email, password):
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Forkert email eller adgangskode.")

    if st.button("Opret bruger"):
        if register_user(email, password):
            st.success("Bruger oprettet! Log nu ind.")
        else:
            st.error("Denne email findes allerede.")
    st.stop()

# Når brugeren er logget ind, starter resten af appen
st.title("🔧 Manual Chat med Lykke AI")

manuals = list_manuals()
manual_choice = st.selectbox("Vælg en manual eller upload en ny:", ["Upload ny"] + manuals)

if manual_choice == "Upload ny":
    uploaded_files = st.file_uploader("Upload PDF", type="pdf", accept_multiple_files=True)
    if uploaded_files:
        for file in uploaded_files:
            chunks = extract_chunks_from_pdf(file)
            create_or_load_index(file.name, chunks)

            # Gem PDF'en lokalt
            base_path = get_manual_path(file.name)
            os.makedirs(base_path, exist_ok=True)
            with open(os.path.join(base_path, "original.pdf"), "wb") as f:
                f.write(file.getbuffer())

        st.success("✅ Manualen er klar – vælg den i dropdown og stil et spørgsmål!")
        st.stop()
else:
    chunks = load_manual_chunks(manual_choice)

    st.markdown("### 🤖 Stil et spørgsmål til manualen:")
    question = st.text_input("Hvad vil du gerne vide?")

    # Læg slider og kontekst nederst
    k_value = st.slider("Antal tekstbidder til LLM (default 250)", 5, 500, 250)

    if question:
        with st.spinner("Tænker med Lykke AI... og drikker en Harboe Cola imens 🍹"):
            context, sources = search_chunks(manual_choice, question, chunks, k=k_value)
            answer = generate_answer(question, context)

            st.markdown("**Svar:**")
            st.write(answer)

            # Fast venlig tekst uanset hvad
            st.success("📄 **TIP:** Du kan måske finde svaret – eller yderligere relevant information – i de viste PDF-sider nedenfor.")

            # Vis konteksten i en expander
            with st.expander("🔍 Vis hele konteksten som modellen så den"):
                st.code(context)

            st.markdown("**🗂 Kilder (PDF-sider):**")
            for page, _ in sources:
                try:
                    page_num = int(page.replace("Side ", "")) - 1
                    pdf_path = os.path.join(get_manual_path(manual_choice), "original.pdf")
                    image = render_pdf_page_as_image(pdf_path, page_num)
                    st.image(image, caption=f"📄 PDF-side {page_num + 1}", use_container_width=True)

                    if st.checkbox(f"Vis tekst fra {page}", key=page):
                        full_page_texts = [t for p, t in chunks if p == page]
                        st.code("\n\n".join(full_page_texts))
                except Exception as e:
                    st.warning(f"Kunne ikke vise side {page}: {e}")
