import streamlit as st
from streamlit_mermaid import st_mermaid

# Configurazione estetica
st.set_page_config(page_title="DD Interactive Engine", layout="wide")

# --- 1. GESTIONE DELLO STATO (Il "Cervello" dell'app) ---
if "step" not in st.session_state:
    st.session_state.step = 1 # Inizia dallo Step 1
if "history" not in st.session_state:
    st.session_state.history = [] # Tracciamento verticale
if "scoping_choice" not in st.session_state:
    st.session_state.scoping_choice = None

# Funzione per registrare le decisioni
def log_decision(label):
    if label not in st.session_state.history:
        st.session_state.history.append(label)

# --- 2. SIDEBAR (SCHERMO VERTICALE - CONTATORE STEP) ---
with st.sidebar:
    st.header("📟 Step Tracker")
    st.write(f"Ti trovi allo step: **{st.session_state.step}**")
    st.divider()
    # Mostra la lista delle decisioni prese finora
    for i, h in enumerate(st.session_state.history):
        st.success(f"{i+1}. {h}")
    
    if st.button("Riavvia Procedura"):
        st.session_state.step = 1
        st.session_state.history = []
        st.rerun()

# --- 3. INTERFACCIA PRINCIPALE (SCHERMO ORIZZONTALE) ---
st.title("🛡️ Sistema Interattivo di Due Diligence")

col_interrogazione, col_visualizzazione = st.columns([1, 1.5])

with col_interrogazione:
    st.subheader("📝 Interrogazione Checkpoint")

    # --- STEP 1: MATRICE DI SCOPING ---
    if st.session_state.step == 1:
        st.info("FASE 2: Identifica la fattispecie dell'accordo")
        scoping = st.radio("Seleziona Fattispecie:", 
                          ["M&A / JV / Investimenti", "Business Associate / Agenti", "Fornitori / Clienti"])
        if st.button("Conferma Scoping"):
            st.session_state.scoping_choice = scoping
            log_decision(f"Scoping: {scoping}")
            st.session_state.step = 2
            st.rerun()

    # --- STEP 2: VERIFICA DOCUMENTALE ---
    elif st.session_state.step == 2:
        st.info("CHECKPOINT: Documentazione Obbligatoria")
        q_ok = st.checkbox("Questionario DD ricevuto e completo?")
        check_tvr = st.checkbox("TVR acquisita?")
        
        if q_ok and check_tvr:
            if st.button("Procedi a Satellite B"):
                log_decision("Documentazione Verificata")
                st.session_state.step = 3
                st.rerun()
        else:
            st.warning("Completa i check per proseguire")

    # --- STEP 3: SATELLITE B (SOGLIE) ---
    elif st.session_state.step == 3:
        st.info("SATELLITE B: Analisi Assetto Proprietario")
        soglia = st.selectbox("Seleziona il livello di rischio/soglia:", 
                             ["L1 Strategico (10%)", "Standard AML (25%)", "Controllo Diritto (50%)", "Soglia 0% (LR)"])
        if st.button("Consolida Lista Nominativi"):
            log_decision(f"Soglia definita: {soglia}")
            st.session_state.step = 4
            st.rerun()

    # --- STEP 4: SATELLITE C (DETTAGLI TECNICI FORNITORI) ---
    elif st.session_state.step == 4:
        st.info("SATELLITE C: Screening Reputazionale")
        triage = st.radio("Livello di Rischio emerso:", ["Alto", "Standard", "Basso"])
        
        # INTERROGAZIONE FORNITORI
        st.markdown("### 🔍 Fornitori Tecnici da consultare:")
        if triage == "Alto":
            st.warning("- DD4Eni 2.0 (Full)\n- DJ Factiva (Global)\n- ORBIS (Assetto)\n- WCO (Sanzioni)")
        else:
            st.success("- DD4Eni 2.0 (Standard)\n- CRIBIS / D&B\n- Google Web")
        
        esito = st.radio("Riscontro individuato?", ["Nessuno (Clean)", "Positività / Red Flag"])
        if st.button("Concludi Workflow"):
            log_decision(f"Screening: {esito}")
            st.session_state.step = 5
            st.rerun()

    # --- STEP 5: REPORTING ---
    elif st.session_state.step == 5:
        st.balloons()
        st.subheader("🏁 Esito Procedura")
        if "Red Flag" in st.session_state.history[-1]:
            st.error("AZIONE: Invio FORM 2 a Presidio BIC / AC-AML")
        else:
            st.success("AZIONE: Invio FORM 1 a DDM (Chiusura)")

# --- 4. VISUALIZZAZIONE DINAMICA (DIAGRAMMA) ---
with col_visualizzazione:
    # Qui il diagramma Mermaid cambia "luce" in base allo step
    # Usiamo colori diversi per mostrare all'utente dove si trova
    
    nodi = {1: "Fase2", 2: "DocCheck", 3: "SatB", 4: "SatC", 5: "Reporting"}
    current_node = nodi.get(st.session_state.step, "Fase2")

    mermaid_code = f"""
    flowchart TD
        Start([RICEZIONE]) --> Fase2{{MATRICE SCOPING}}
        Fase2 --> DocCheck[VERIFICA DOCUMENTALE]
        DocCheck --> SatB[[SATELLITE B: ASSETTO]]
        SatB --> SatC[[SATELLITE C: SCREENING]]
        SatC --> Reporting{{REPORTING FINALE}}
        
        style {current_node} fill:#ff4b4b,stroke:#333,stroke-width:4px,color:#fff
    """
    st_mermaid(mermaid_code, height=500)
