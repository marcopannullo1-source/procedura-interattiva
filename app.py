import streamlit as st
from streamlit_mermaid import st_mermaid

# Configurazione Layout
st.set_page_config(page_title="DD Workflow Interactive Guide", layout="wide")

# --- INIZIALIZZAZIONE STATO ---
if "step_history" not in st.session_state:
    st.session_state.step_history = []  # Tracker verticale
if "current_node" not in st.session_state:
    st.session_state.current_node = "START" # Nodo attivo nel workflow
if "workflow_data" not in st.session_state:
    st.session_state.workflow_data = {} # Dati raccolti durante il drill-down

# Funzione per avanzare nel workflow
def proceed_to(node, label, data=None):
    st.session_state.current_node = node
    step_entry = {"node": node, "label": label}
    if step_entry not in st.session_state.step_history:
        st.session_state.step_history.append(step_entry)
    if data:
        st.session_state.workflow_data.update(data)

# --- SIDEBAR (SCHERMO VERTICALE: STEP TRACKER) ---
with st.sidebar:
    st.header("📋 Step Tracker")
    st.write(f"Percorso attuale: **{len(st.session_state.step_history)}** passaggi")
    
    # Visualizzazione dinamica degli step percorsi
    for i, step in enumerate(st.session_state.step_history):
        st.success(f"Step {i+1}: {step['label']}")
    
    st.divider()
    if st.button("Reset Workflow"):
        st.session_state.step_history = []
        st.session_state.current_node = "START"
        st.session_state.workflow_data = {}
        st.rerun()

# --- MAIN AREA (SCHERMO ORIZZONTALE) ---
st.title("🛡️ Guida Interattiva Procedura Due Diligence")

# Layout a due colonne per Interazione vs Visualizzazione
col_ui, col_viz = st.columns([1, 2])

with col_ui:
    st.subheader("🛠️ Azioni What/If")
    
    # --- LOGICA DI NAVIGAZIONE INTERATTIVA ---
    
    # 1. FASE INIZIALE E SCOPING (Master) 
    if st.session_state.current_node == "START":
        st.markdown("**FASE 1-2: Verifica e Scoping**")
        scoping = st.radio("Seleziona Fattispecie Accordo:", 
                          ["M&A / Investimenti / JV", "Business Associate / Agenti", "Fornitori / Clienti"])
        if st.button("Conferma Scoping"):
            proceed_to("QuestCheck", f"Scoping: {scoping}", {"cat": scoping})

    # 2. CHECK QUESTIONARIO [cite: 13, 15]
    elif st.session_state.current_node == "QuestCheck":
        st.markdown("**Verifica Documentale**")
        ha_questionario = st.checkbox("Il Questionario DD (Par. 6.2) è stato ricevuto?")
        if ha_questionario:
            if st.button("Procedi a Satellite B"):
                proceed_to("SatB", "Ricezione Questionario OK")
        else:
            st.error("AZIONE: Richiesta Questionario alla CTP obbligatoria.")
            if st.button("Reset dopo richiesta"): st.rerun()

    # 3. SATELLITE B: ASSETTO E SOGLIE (Drill-down) [cite: 7, 8]
    elif st.session_state.current_node == "SatB":
        st.markdown("### SATELLITE B: Ricostruzione Assetto")
        st.info("Identifica la soglia di controllo in base alla fattispecie.")
        
        soglia_opzione = st.selectbox("Seleziona Scenario Soglia:", [
            "L1 Strategico (M&A/JV) -> Soglia 10%",
            "Business Associate / Agenti -> Soglia 10% Rafforzata",
            "L3-4 Fornitori/Clienti -> Soglia 25% (AML)",
            "L2 Fornitori/Clienti -> Soglia 50% (Diritto)",
            "L1 Fornitori/Clienti -> Soglia 0% (LR e Referenti)"
        ])
        
        if st.button("Consolida Lista Nominativi"):
            proceed_to("SatC", f"Assetto: {soglia_opzione.split('->')[1]}")

    # 4. SATELLITE C: SCREENING E FORNITORI TECNICI (Drill-down) 
    elif st.session_state.current_node == "SatC":
        st.markdown("### SATELLITE C: Screening Reputazionale")
        rischio = st.selectbox("Definisci Scenario di Rischio per Triage:", ["Alto", "Standard", "Basso"])
        
        # Integrazione Dettagli Tecnici Fornitori 
        if rischio == "Alto":
            st.warning("**Sistemi Richiesti:** DD4Eni 2.0, ORBIS, DJ ASAM, DJ Factiva, WCO, Google-Bing Web")
        elif rischio == "Standard":
            st.info("**Sistemi Richiesti:** DD4Eni 2.0, CRIBIS-D&B, DJ Factiva, Google Web")
        else:
            st.success("**Sistemi Richiesti:** DD4Eni 2.0, Liste Sanzioni (DJ ASAM / WCO)")
            
        st.divider()
        riscontro = st.radio("Esito dello Screening:", ["Nessun Riscontro", "Falso Positivo", "Red Flag / Positività"])
        
        if st.button("Concludi Analisi"):
            proceed_to("Final", f"Esito Screening: {riscontro}", {"esito": riscontro})

    # 5. CONCLUSIONE E REPORTING [cite: 6, 14]
    elif st.session_state.current_node == "Final":
        st.subheader("🏁 Chiusura Pratica")
        esito = st.session_state.workflow_data.get("esito")
        if esito == "Red Flag / Positività":
            st.error("AZIONE: Invio RAPPORTO DD (FORM 2) al Presidio BIC / AC-AML")
        else:
            st.success("AZIONE: Invio RAPPORTO DD (FORM 1) a DDM")
        
        if st.button("Inizia Nuova Pratica"):
            st.session_state.current_node = "START"
            st.session_state.step_history = []
            st.rerun()

# --- VISUALIZZAZIONE WORKFLOW (SCHERMO ORIZZONTALE) ---
with col_viz:
    # Colora il nodo in base alla posizione attuale
    color_map = {
        "START": "START", "QuestCheck": "QuestCheck", 
        "SatB": "SatB", "SatC": "SatC", "Final": "EvalOutcome"
    }
    active_node = color_map.get(st.session_state.current_node, "START")
    
    # Diagramma Master semplificato che evidenzia lo stato
    master_mmd = f"""
    flowchart LR
       START(["RICEZIONE PRATICA"]) --> QuestCheck{{"VERIFICA DOCUMENTALE"}}
       QuestCheck --> SatB[["SATELLITE B: ASSETTO"]]
       SatB --> SatC[["SATELLITE C: SCREENING"]]
       SatC --> EvalOutcome{{"VALUTAZIONE FINALE"}}
       EvalOutcome --> Form1["FORM 1: CHIUSURA"]
       EvalOutcome --> Form2["FORM 2: ESCALATION BIC"]
       
       style {active_node} fill:#fffd75,stroke:#333,stroke-width:4px
    """
    st_mermaid(master_mmd, height=400)
    
    # Mostra il dettaglio del Satellite se l'utente è lì
    if st.session_state.current_node == "SatB":
        st.caption("Dettaglio Tecnico: SATELLITE B (Soglie Assetto)")
        st_mermaid("graph TD; A[Triage] --> B[Soglia 10%]; A --> C[Soglia 25%]; A --> D[Soglia 50%]; B & C & D --> E[Lista Nominativi]", height=200)
    
    if st.session_state.current_node == "SatC":
        st.caption("Dettaglio Tecnico: SATELLITE C (Esecuzione Ricerca)")
        st_mermaid("graph TD; P[Provider Selection] --> S[Search Execution] --> R{Riscontro?}; R -- SI --> Red[Analisi Criticità]; R -- NO --> End[Ok]", height=200)