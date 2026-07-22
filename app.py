import streamlit as st
import pandas as pd
from openai import OpenAI

# --- CONFIGURATION OPENAI ---
# C'EST CETTE LIGNE QUI EST MAGIQUE. 
# Le texte "OPENAI_API_KEY" est juste une étiquette. Ne mets JAMAIS ta vraie clé ici !
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- DESIGN DE LA PAGE (UX/UI) ---
st.set_page_config(page_title="IA Resto Finder", page_icon="🍽️", layout="centered")

st.markdown("""
    <style>
    .stButton>button {
        background-color: #FF4B4B;
        color: white;
        border-radius: 8px;
        font-weight: bold;
        padding: 10px 20px;
    }
    .reponse-ia {
        background-color: #262730;
        padding: 25px;
        border-radius: 10px;
        border-left: 5px solid #FF4B4B;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# --- EN-TÊTE DE L'APPLICATION ---
st.title("🍽️ Trouve ton resto parfait avec l'IA")
st.markdown("**Ton assistant gastronomique basé sur l'analyse de milliers de vrais avis.**")

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data
def load_data():
    return pd.read_csv("toy_dataset_restos.csv")

df = load_data()
noms_restos = df['restaurant_name'].unique()

st.success(f"✅ Base de données connectée : {len(df)} avis prêts à être analysés.")
st.markdown("---")

# --- ZONE DE RECHERCHE ---
st.subheader("Que cherches-tu aujourd'hui ?")
user_query = st.text_area(
    "Décris ton envie de manière naturelle :", 
    placeholder="Ex: Un endroit chic qui coûte cher avec de très bonnes viandes..."
)

# --- DÉCLENCHEMENT DE L'IA ---
if st.button("Lancer la recherche IA 🚀"):
    if not user_query:
        st.warning("⚠️ Oups ! Tu as oublié de décrire ce que tu cherchais.")
    else:
        with st.spinner("L'IA croise ta demande avec les avis des clients... 🧠"):
            
            contexte_avis = ""
            for resto in noms_restos:
                avis_resto = df[(df['restaurant_name'] == resto) & (df['rating_review'] >= 4)].head(5)['review_full'].tolist()
                contexte_avis += f"\n--- Restaurant: {resto} ---\n"
                for avis in avis_resto:
                    contexte_avis += f"- {avis}\n"

            prompt_systeme = """Tu es un critique gastronomique expert de Barcelone.
            Ta mission est d'analyser la demande de l'utilisateur et de trouver LE ou LES DEUX meilleurs restaurants correspondants, STRICTEMENT basés sur le contexte fourni.
            
            Tes règles d'or :
            1. Ne propose QUE des restaurants présents dans le contexte.
            2. Argumente ton choix en t'appuyant sur les détails des avis clients.
            3. Inclus 1 ou 2 citations traduites en français des avis pour prouver tes dires.
            4. Utilise un ton professionnel, clair et engageant (utilise du gras pour les noms de restos).
            5. Si aucun restaurant ne correspond vraiment, dis-le poliment et propose le choix le plus proche."""

            try:
                reponse = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": prompt_systeme},
                        {"role": "user", "content": f"CONTEXTE DES AVIS :\n{contexte_avis}\n\nDEMANDE DE L'UTILISATEUR : {user_query}"}
                    ],
                    temperature=0.5,
                    max_tokens=600
                )
                
                resultat_ia = reponse.choices[0].message.content
                
                st.markdown("---")
                st.subheader("✨ La recommandation du Chef (IA)")
                st.markdown(f'<div class="reponse-ia">{resultat_ia}</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error("🚨 Une erreur de connexion avec l'IA s'est produite.")
                st.code(e)
