import streamlit as st
from streamlit_mermaid import st_mermaid

# 1. Configurazione della pagina
st.set_page_config(page_title="DD Interactive Engine", layout="wide")

# 2. Inizializzazione del motore decisionale (Session State)
if "current_step" not in st.session_state:
    st.session_state.current_step = "START"
if "history" not in st.session_state:
    st.session_state.history = []
if "data" not in st.session_state:
    st.session_state.data = {}

# Funzione per avanzare nella procedura
def move_to(node, label, decision_data=None):
    st.session_state.current_step = node
    st.session_state.history.append(f"Step {len(st.session_state.history)+1}: {label}")
    if decision_data:
        st.session_state.data.update(decision_data)

# --- SCHERMO VERTICALE: SIDEBAR (STEP TRACKER) ---
with st.sidebar:
    st.title("📟 Step Tracker")
    st.write(f"Decisioni prese: **{len(st.session_state.history)}**")
    for item in st.session_state.history:
        st.success(item)
    
    st.divider()
    if st.button("Reset Procedura"):
        st.session_state.current_step = "START"
        st.session_state.history = []
        st.session_state.data = {}
        st.rerun()

# --- SCHERMO ORIZZONTALE: INTERFACCIA INTERROGABILE ---
st.title("🛡️ Sistema Decisionale Due Diligence")

col_input, col_viz = st.columns([1, 1.5])

with col_input:
    st.subheader("📝 Checkpoint Decisionale")
    
    # --- LOGICA WHAT/IF ---
    
    # STEP 1: MATRICE DI SCOPING
    if st.session_state.current_step == "START":
        st.info("FASE 2: Identificazione Fattispecie")
        fattispecie = st.radio("Tipo di Accordo:", ["M&A / JV", "Business Associate / Agenti", "Fornitori / Clienti"])
        if st.button("Conferma Scoping"):
            move_to("QUEST", f"Scoping: {fattispecie}", {"tipo": fattispecie})
            st.rerun()

    # STEP 2: VERIFICA DOCUMENTALE
    elif st.session_step == "QUEST" or st.session_state.current_step == "QUEST":
        st.info("CHECKPOINT: Documentazione")
        c1 = st.checkbox("Questionario DD ricevuto?")
        c2 = st.checkbox("TVR / Company Card acquisita?")
        if c1 and c2:
            if st.button("Procedi a SATELLITE B"):
                move_to("SATB", "Documentazione OK")
                st.rerun()
        else:
            st.warning("Azione necessaria: Richiedere documenti mancanti.")

    # STEP 3: SATELLITE B (DRILL DOWN ASSETTO)
    elif st.session_state.current_step == "SATB":
        st.info("SATELLITE B: Analisi Assetto")
        rischio = st.selectbox("Livello Rischio/Fattispecie:", 
                              ["M&A Strategico (Soglia 10%)", "Standard AML (Soglia 25%)", "Controllo Diritto (Soglia 50%)"])
        if st.button("Consolida Lista Nominativi"):
            move_to("SATC", f"Soglia definita: {rischio}")
            st.rerun()

    # STEP 4: SATELLITE C (SCREENING TECNICO)
    elif st.session_state.current_step == "SATC":
        st.info("SATELLITE C: Screening Reputazionale")
        triage = st.select_slider("Triage di Rischio:", options=["Basso", "Standard", "Alto"])
        
        # DETTAGLI TECNICI DINAMICI
        st.markdown("#### 🔍 Fornitori da utilizzare:")
        if triage == "Alto":
            st.warning("**FULL ACCESS:** DD4Eni 2.0, DJ Factiva, ORBIS, WCO")
        elif triage == "Standard":
            st.info("**STANDARD:** DD4Eni 2.0, CRIBIS, DJ Factiva")
        else:
            st.success("**ESSENTIAL:** DD4Eni 2.0, Liste Sanzioni")
            
        esito = st.radio("Risultato Screening:", ["Nessun Riscontro", "Red Flag"])
        if st.button("Concludi Analisi"):
            move_to("FINAL", f"Esito: {esito}", {"esito": esito})
            st.rerun()

    # STEP 5: CONCLUSIONE
    elif st.session_state.current_step == "FINAL":
        st.balloons()
        if st.session_state.data.get("esito") == "Red Flag":
            st.error("AZIONE: Invio FORM 2 a Presidio BIC / AC-AML")
        else:
            st.success("AZIONE: Invio FORM 1 a DDM")

# --- VISUALIZZAZIONE DINAMICA ---
with col_viz:
    st.subheader("🗺️ Mappa del Workflow")
    
    # Definiamo quale nodo illuminare in base allo step attuale
    mapping = {"START": "F2", "QUEST": "Doc", "SATB": "B", "SATC": "C", "FINAL": "End"}
    active = mapping.get(st.session_state.current_step, "F2")
    
    # Il codice Mermaid ora ha uno stile "style" dinamico
    master_mmd = f"""
    flowchart TD
        F2{{MATRICE SCOPING}} --> Doc[VERIFICA DOCUMENTALE]
        Doc --> B[[SATELLITE B: ASSETTO]]
        B --> C[[SATELLITE C: SCREENING]]
        C --> End{{REPORTING FINALE}}
        
        style {active} fill:#ff4b4b,stroke:#333,stroke-width:4px,color:#fff
    """
    st_mermaid(master_mmd, height=450)
