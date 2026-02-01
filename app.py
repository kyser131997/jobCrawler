"""
Application Streamlit pour le scraping d'offres d'emploi data en France.
Interface moderne en dark mode avec dashboard statistiques et tableau interactif.
"""
import sys
import asyncio

# Fix pour Windows - DOIT ÊTRE FAIT AVANT TOUT AUTRE IMPORT
# Évite l'erreur NotImplementedError avec subprocess sur Windows
if sys.platform == 'win32':
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        pass

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from scraper.pipeline import ScrapingPipeline

from config import MAX_TABLE_ROWS

# Configuration de la page
st.set_page_config(
    page_title="Job Crawler - Offres Data France",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Fonction pour installer Playwright si nécessaire (pour Streamlit Cloud)
def ensure_playwright_installed():
    import subprocess
    import sys
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            try:
                p.chromium.launch(headless=True).close()
            except Exception:
                # Si le lancement échoue, on suppose qu'il faut installer
                print("Playwright browsers not found. Installing...")
                subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
                subprocess.check_call([sys.executable, "-m", "playwright", "install-deps"])
    except Exception as e:
        print(f"Error checking Playwright: {e}")

# Exécuter la vérification au démarrage (mais pas à chaque rerun)
if 'playwright_checked' not in st.session_state:
    with st.spinner("Vérification des dépendances..."):
        ensure_playwright_installed()
    st.session_state.playwright_checked = True

# CSS personnalisé pour le dark mode
st.markdown("""
<style>
    /* Background noir */
    .stApp {
        background-color: #000000;
    }
    
    /* Cartes en gris foncé */
    .css-1r6slb0, .css-12oz5g7 {
        background-color: #1a1a1a;
        border-radius: 10px;
        padding: 20px;
    }
    
    /* Texte clair */
    .stMarkdown, .stText, p, span, label {
        color: #e0e0e0 !important;
    }
    
    /* Titres */
    h1, h2, h3 {
        color: #ffffff !important;
    }
    
    /* Bouton principal */
    .stButton > button {
        background: linear-gradient(90deg, #2196F3 0%, #1976D2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-size: 16px;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #1976D2 0%, #1565C0 100%);
        box-shadow: 0 4px 12px rgba(33, 150, 243, 0.4);
    }
    
    /* Métriques */
    [data-testid="stMetricValue"] {
        color: #2196F3 !important;
        font-size: 28px !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #b0b0b0 !important;
    }
    
    /* Tableau */
    .dataframe {
        background-color: #1a1a1a !important;
        color: #e0e0e0 !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #2196F3 !important;
    }
    
    /* Cards personnalisées */
    .stat-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border-radius: 12px;
        padding: 20px;
        border-left: 4px solid #2196F3;
        margin: 10px 0;
    }
    
    .success-message {
        background-color: #1b5e20;
        color: #a5d6a7;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #4caf50;
    }
    
    .error-message {
        background-color: #b71c1c;
        color: #ef9a9a;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #f44336;
    }
</style>
""", unsafe_allow_html=True)

# Initialisation du pipeline
@st.cache_resource
def get_pipeline():
    return ScrapingPipeline()

pipeline = get_pipeline()

# État de session
if 'scraping_done' not in st.session_state:
    st.session_state.scraping_done = False
if 'is_scraping' not in st.session_state:
    st.session_state.is_scraping = False
if 'last_stats' not in st.session_state:
    st.session_state.last_stats = None


# En-tête
st.markdown("<p style='text-align: center; color: #b0b0b0; margin-bottom: 30px;'>Scraping automatique d'offres d'emploi data publiées dans les 3 derniers jours</p>", unsafe_allow_html=True)

# Barre latérale pour la configuration
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3845/3845696.png", width=50)
    st.header("Configuration")
    
    # Gestion des mots-clés
    st.subheader("🔑 Mots-clés")
    
    if 'search_queries' not in st.session_state:
        st.session_state.search_queries = [
            "Data Analyst",
            "Business Analyst",
            "Data Engineer",
            "Data Scientist",
            "Analytics Engineer"
        ]
    
    # Éditeur de liste pour les mots-clés
    # On utilise text_area pour simplicité, une ligne par mot-clé
    queries_text = st.text_area(
        "Mots-clés à rechercher (un par ligne)",
        value="\n".join(st.session_state.search_queries),
        height=150,
        help="Ajoutez ou supprimez des métiers à rechercher."
    )
    
    # Mettre à jour la session state
    st.session_state.search_queries = [q.strip() for q in queries_text.split('\n') if q.strip()]
    
    st.divider()
    
    st.caption("ℹ️ Les modifications seront prises en compte au prochain scraping.")

# Zone de contrôle
# Zone de contrôle
# Recherche par défaut sur toute la France
country_choice = "France"
location_choice = "France"

st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    btn_label = "⏳ Scraping en cours..." if st.session_state.is_scraping else "🚀 Lancer le Scraping"
    if st.button(btn_label, use_container_width=True, disabled=st.session_state.is_scraping):
        st.session_state.is_scraping = True
        # Conteneur pour les logs
        progress_container = st.container()
        
        # Barre de progression visuelle
        progress_bar = st.progress(0, text="Initialisation...")
        
        log_placeholder = progress_container.empty()
        logs = []
        
        def progress_callback(message):
            logs.append(message)
            log_placeholder.code('\n'.join(logs[-10:]))  # Réduit à 10 pour plus de clarté
            
            # Mise à jour simplifiée de la barre de progression basée sur les sources
            if "📡 Source:" in message:
                current_source_idx = len([l for l in logs if "📡 Source:" in l])
                total_sources = 7
                progress = min(current_source_idx / total_sources, 0.9)
                progress_bar.progress(progress, text=f"Scraping de la source {current_source_idx}/{total_sources}...")
        
        with st.spinner("Récupération des offres..."):
            try:
                import subprocess
                import os
                
                # Utiliser le Python de l'environnement virtuel
                python_exe = sys.executable
                script_path = os.path.join(os.getcwd(), "scraper_cli.py")
                
                # Forcer l'encodage UTF-8 pour le processus fils
                env = os.environ.copy()
                env["PYTHONIOENCODING"] = "utf-8"
                
                # Préparer les arguments
                cmd = [python_exe, script_path, "--country", country_choice, "--location", location_choice]
                
                # Ajouter les queries si disponibles
                if 'search_queries' in st.session_state and st.session_state.search_queries:
                    queries_str = ",".join(st.session_state.search_queries)
                    cmd.extend(["--queries", queries_str])
                
                # Lancer le scraper en tant que processus séparé
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    encoding='utf-8',
                    errors='replace',
                    env=env
                )
                
                # Lire la sortie en temps réel
                while True:
                    line = process.stdout.readline()
                    if not line and process.poll() is not None:
                        break
                    if line:
                        progress_callback(line.strip())
                
                # Vérifier si le processus a réussi
                return_code = process.wait()
                
                st.session_state.is_scraping = False
                progress_bar.progress(1.0, text="Scraping terminé !")
                
                if return_code == 0:
                    st.session_state.scraping_done = True
                    # Recharger les stats (le DB a été mise à jour par le processus CLI)
                    st.success("Scraping terminé avec succès !")
                    st.rerun()
                else:
                    st.error(f"Le scraper a échoué avec le code : {return_code}")
                
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                st.markdown(f"""
                <div class="error-message">
                    <strong>❌ Erreur lors du scraping</strong><br>
                    {str(e)}
                </div>
                """, unsafe_allow_html=True)
                with st.expander("Détails de l'erreur"):
                    st.code(error_details)

st.markdown("---")

# Récupérer les données
jobs_data = pipeline.get_all_jobs(limit=MAX_TABLE_ROWS)
stats = pipeline.get_statistics()

if jobs_data:
    # Dashboard statistiques
    st.markdown("<h2>📊 Statistiques</h2>", unsafe_allow_html=True)
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Offres", stats['total'])
    
    with col2:
        data_analyst_count = stats['by_category'].get('Data Analyst', 0)
        st.metric("Data Analyst", data_analyst_count)
    
    with col3:
        business_analyst_count = stats['by_category'].get('Business Analyst', 0)
        st.metric("Business Analyst", business_analyst_count)
    
    with col4:
        data_engineer_count = stats['by_category'].get('Data Engineer', 0)
        st.metric("Data Engineer", data_engineer_count)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Graphiques
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Offres par catégorie
        if stats['by_category']:
            fig_category = px.bar(
                x=list(stats['by_category'].keys()),
                y=list(stats['by_category'].values()),
                title="Offres par Catégorie",
                labels={'x': 'Catégorie', 'y': 'Nombre d\'offres'},
                color=list(stats['by_category'].values()),
                color_continuous_scale='Blues'
            )
            fig_category.update_layout(
                plot_bgcolor='#1a1a1a',
                paper_bgcolor='#1a1a1a',
                font_color='#e0e0e0',
                showlegend=False
            )
            st.plotly_chart(fig_category, use_container_width=True)
    
    with chart_col2:
        # Offres par source
        if stats['by_source']:
            fig_source = px.pie(
                names=list(stats['by_source'].keys()),
                values=list(stats['by_source'].values()),
                title="Offres par Source",
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            fig_source.update_layout(
                plot_bgcolor='#1a1a1a',
                paper_bgcolor='#1a1a1a',
                font_color='#e0e0e0'
            )
            st.plotly_chart(fig_source, use_container_width=True)
    

    


    st.markdown("---")
    
    # Tableau des offres
    st.markdown("<h2>📋 Offres d'Emploi</h2>", unsafe_allow_html=True)
    
    # Convertir en DataFrame
    df = pd.DataFrame(jobs_data)
    
    # Ajouter le badge Nouveau (offres scrapées il y a moins de 24h)
    def check_new(scraped_at_val):
        try:
            if isinstance(scraped_at_val, str):
                scraped_at = pd.to_datetime(scraped_at_val)
            else:
                scraped_at = scraped_at_val
                
            if (datetime.utcnow() - scraped_at.replace(tzinfo=None)) < timedelta(hours=24):
                return "🆕 Nouveau"
            return ""
        except:
            return ""
            
    df['✨ Status'] = df['scraped_at'].apply(check_new)
    
    # S'assurer que les colonnes nécessaires existent (pour éviter KeyError si cache ancien)
    if 'applied' not in df.columns:
        df['applied'] = False
    if 'id' not in df.columns:
        df['id'] = range(len(df)) # Fallback id si manquant (ne permettra pas la persistance mais évite le crash)
    
    # Filtres
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        categories = ['Toutes'] + sorted(df['role_category'].unique().tolist())
        selected_category = st.selectbox("Catégorie", categories)
    
    with filter_col2:
        sources = ['Toutes'] + sorted(df['source'].unique().tolist())
        selected_source = st.selectbox("Source", sources)
    
    with filter_col3:
        search_term = st.text_input("Rechercher (titre, entreprise)", "")
    
    # Appliquer les filtres
    filtered_df = df.copy()
    
    # Filtre automatique par carte si actif

    
    if selected_category != 'Toutes':
        filtered_df = filtered_df[filtered_df['role_category'] == selected_category]
    
    if selected_source != 'Toutes':
        filtered_df = filtered_df[filtered_df['source'] == selected_source]
    
    if search_term:
        mask = (
            filtered_df['job_title'].str.contains(search_term, case=False, na=False) |
            filtered_df['company'].str.contains(search_term, case=False, na=False)
        )
        filtered_df = filtered_df[mask]
    
    # Afficher le nombre de résultats
    st.markdown(f"<p style='color: #b0b0b0;'>📊 {len(filtered_df)} offres affichées</p>", unsafe_allow_html=True)
    
    # Préparer le tableau pour l'affichage
    display_df = filtered_df[[
        'id', '✨ Status', 'applied', 'job_title', 'company', 'role_category', 'location', 
        'source', 'published_date', 'detected_keywords', 'url'
    ]].copy()
    
    # Renommer les colonnes
    display_df.columns = [
        'ID', 'Status', 'Appliqué', 'Titre', 'Entreprise', 'Catégorie', 'Localisation',
        'Source', 'Date Publication', 'Mots-clés', 'URL'
    ]
    
    # Formater les dates
    if 'Date Publication' in display_df.columns:
        # Conversion flexible sans format strict pour supporter différents styles ISO
        display_df['Date Publication'] = pd.to_datetime(display_df['Date Publication'], errors='coerce').dt.strftime('%Y-%m-%d')
        # Remplacer les NaT/NaN par une chaîne vide ou un tiret pour éviter "None" texte
        display_df['Date Publication'] = display_df['Date Publication'].fillna("-")
    
    # Afficher le tableau avec st.data_editor pour permettre la modification du statut "Appliqué"
    edited_df = st.data_editor(
        display_df,
        use_container_width=True,
        height=600,
        hide_index=True,
        column_config={
            "ID": None, # Cacher l'ID
            "Status": st.column_config.TextColumn("✨ Status", width="small"),
            "Appliqué": st.column_config.CheckboxColumn(
                "Postulé ?",
                help="Cochez si vous avez déjà postulé à cette offre",
                default=False,
            ),
            "URL": st.column_config.LinkColumn("Lien", display_text="Voir l'offre"),
            "Titre": st.column_config.TextColumn(width="medium"),
            "Entreprise": st.column_config.TextColumn(width="small"),
            "Mots-clés": st.column_config.TextColumn(width="medium"),
        },
        disabled=["ID", "Status", "Titre", "Entreprise", "Catégorie", "Localisation", "Source", "Date Publication", "Mots-clés", "URL"]
    )
    
    # Gérer les modifications du statut "Appliqué"
    if not edited_df.equals(display_df):
        # Identifier les lignes modifiées
        changes = edited_df[edited_df['Appliqué'] != display_df['Appliqué']]
        for _, row in changes.iterrows():
            job_id = int(row['ID'])
            new_status = bool(row['Appliqué'])
            if pipeline.update_job_status(job_id, new_status):
                st.toast(f"Statut mis à jour pour : {row['Titre']}", icon="✅")
            else:
                st.error(f"Erreur lors de la mise à jour pour : {row['Titre']}")
    
    # Export CSV
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Exporter en CSV",
        data=csv,
        file_name=f"offres_emploi_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

else:
    # Aucune donnée
    st.markdown("""
    <div style='text-align: center; padding: 60px; background-color: #1a1a1a; border-radius: 12px; margin-top: 40px;'>
        <h3 style='color: #b0b0b0;'>Aucune offre disponible</h3>
        <p style='color: #808080;'>Cliquez sur "Craquer les offres" pour lancer le scraping</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #606060; font-size: 12px;'>Job Crawler - Scraping d'offres d'emploi data en France 🇫🇷</p>", unsafe_allow_html=True)
