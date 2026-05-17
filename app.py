import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import excel_handler as eh

# Page Config
st.set_page_config(page_title="Perill Team Diagnostic App", layout="wide", page_icon="📈")

# Ensure Excel state on load
eh.initialize_excel()
departments, questions_map = eh.load_config()

# Define Performance Tiers
def classify_tier(score):
    if 4.5 <= score <= 5.0:
        return "High Performing", "🟩", "This pillar shows world-class execution and alignment. Maintain current strategies and leverage this team as an internal benchmark."
    elif 3.5 <= score < 4.5:
        return "Performing, Balanced", "🟨", "Solid baseline with minor optimizations required. The team functions reliably but has latent capacity."
    elif 2.5 <= score < 3.5:
        return "Needs Support", "🟧", "Clear systemic vulnerabilities. Targeted interventions, workflow reviews, or training are required to prevent degradation."
    else:
        return "Dysfunctional", "🟥", "Critical operational risk. Structural friction, leadership gaps, or process failures require urgent intervention."

# Tailored suggestions template for low-scoring dimensions
ACTIONABLE_SUGGESTIONS = {
    "Purpose & Motivation": [
        "Facilitate a structured vision workshop to re-align team outcomes with enterprise goals.",
        "Implement explicit, measurable OKRs (Objectives & Key Results) that explicitly map to individual contributions."
    ],
    "External-facing systems & processes": [
        "Establish formal Service Level Agreements (SLAs) and communication conduits with interface teams.",
        "Appoint a stakeholder liaison to manage intake protocols and decouple the core team from scope creep."
    ],
    "Relationships": [
        "Introduce facilitated psychological safety retrospectives to address unvoiced team concerns.",
        "Organize deliberate trust-building cadences focused on understanding individual communication profiles."
    ],
    "Internal-facing systems & processes": [
        "Conduct a comprehensive audit of existing meetings to prune unstructured or unproductive syncs.",
        "Formally document operational standard operating procedures (SOPs) within a centralized knowledge base."
    ],
    "Learning": [
        "Incorporate a blameless post-mortem framework for all key project cycles to emphasize structural over personal accountability.",
        "Dedicate structured sprint allocations or budgets exclusively to engineering/process R&D and cross-training."
    ],
    "Leadership": [
        "Transition management checkpoints toward an empowerment-coaching archetype to alleviate micromanagement friction.",
        "Implement transparent leadership stand-ups explaining macro-organizational strategy and shifts."
    ]
}

# App Layout Header
st.title("🛡️ Perill Team Effectiveness Diagnostic Suite")
st.markdown("---")

# Navigation Sidebar
view_mode = st.sidebar.radio("Navigation Hub", ["📋 Team Assessment Survey", "📊 Administrator Dashboard"])

# ==========================================
# VIEW 1: TEAM ASSESSMENT SURVEY
# ==========================================
if view_mode == "📋 Team Assessment Survey":
    st.header("Team Diagnostic Questionnaire")
    st.write("Please answer the following questions honestly based on your day-to-day team experiences. Submissions are compiled anonymously.")
    
    if not departments or not questions_map:
        st.error("Configuration mapping could not be resolved from Excel. Please inspect the spreadsheet settings.")
    else:
        with st.form("survey_form"):
            selected_dept = st.selectbox("Select Your Current Department/Group:", ["-- Select Department --"] + departments)
            st.markdown("---")
            
            # Group questions dynamically by their assigned pillar for an elegant UI layout
            pillars_grouped = {}
            for q, p in questions_map.items():
                pillars_grouped.setdefault(p, []).append(q)
                
            form_answers = {}
            
            for pillar, queries in pillars_grouped.items():
                st.subheader(f"🔷 Pillar: {pillar}")
                for q_text in queries:
                    # Implement standard horizontal numeric 1-5 Likert scale representation
                    form_answers[q_text] = st.select_slider(
                        q_text,
                        options=[1, 2, 3, 4, 5],
                        value=3,
                        format_func=lambda x: {
                            1: "1 - Strong Disagreement / Poor",
                            2: "2 - Disagree",
                            3: "3 - Neutral",
                            4: "4 - Agree",
                            5: "5 - Strong Agreement / Excellent"
                        }[x]
                    )
                st.markdown("---")
                
            submit_btn = st.form_submit_button("Submit Confidential Evaluation")
            
            if submit_btn:
                if selected_dept == "-- Select Department --":
                    st.error("Submission blocked: You must specify a valid Department selection.")
                else:
                    with st.spinner("Processing results data storage protocols..."):
                        eh.save_submission(selected_dept, form_answers)
                    st.success(f"Thank you! Your diagnostics have been securely saved to the database for {selected_dept}.")

# ==========================================
# VIEW 2: ADMINISTRATOR ANALYTICS DASHBOARD
# ==========================================
elif view_mode == "📊 Administrator Dashboard":
    st.header("Admin Analytics & Diagnostics Engine")
    
    df_res = eh.load_responses()
    
    if df_res.empty or len(df_res) == 0:
        st.info("The application backend database contains no response records yet. Complete an evaluation survey to initialize metrics.")
    else:
        st.sidebar.subheader("Filter Configurations")
        all_depts = sorted(df_res["Department"].dropna().unique().tolist())
        
        # Dynamic filter engine architecture
        filter_type = st.sidebar.radio("Scope Selection Method", ["All Departments", "Specific Filters"])
        
        if filter_type == "All Departments":
            filtered_df = df_res
            scope_title = "All Enterprise Departments"
        else:
            selected_depts = st.sidebar.multiselect("Select Targeted Department(s):", all_depts, default=all_depts[:1] if all_depts else [])
            filtered_df = df_res[df_res["Department"].isin(selected_depts)]
            scope_title = ", ".join(selected_depts) if selected_depts else "No cohorts selected"
            
        st.subheader(f"Analyzing Target Profile: `{scope_title}` ({len(filtered_df)} total responses compiled)")
        
        if filtered_df.empty:
            st.warning("No metrics match the selected department filters. Broaden your administrative configuration criteria.")
        else:
            # ----------------------------------------------------
            # SCORE PROCESSING MECHANICS
            # ----------------------------------------------------
            # Calculate mean score for each specific column corresponding to active questions mapping
            active_questions = [q for q in questions_map.keys() if q in filtered_df.columns]
            
            # Map columns back to pillars and take calculations
            pillar_scores = {}
            for q_text in active_questions:
                pillar = questions_map[q_text]
                # Coerce data to float, ignoring empty values cleanly
                q_mean = pd.to_numeric(filtered_df[q_text], errors='coerce').mean(skipna=True)
                pillar_scores.setdefault(pillar, []).append(q_mean)
                
            # Aggregate calculations to derive definitive Pillar level scores
            final_pillar_averages = {p: sum(scores)/len(scores) for p, scores in pillar_scores.items() if scores}
            
            # Ensure order conformity across the 6 Perill Pillars
            perill_order = [
                "Purpose & Motivation", 
                "External-facing systems & processes", 
                "Relationships", 
                "Internal-facing systems & processes", 
                "Learning", 
                "Leadership"
            ]
            
            final_scores_ordered = {p: final_pillar_averages.get(p, 0.0) for p in perill_order}
            
            # ----------------------------------------------------
            # VISUALIZATION ENGINE - PLOTLY RADAR
            # ----------------------------------------------------
            categories = list(final_scores_ordered.keys())
            values = list(final_scores_ordered.values())
            
            # Pad arrays to close the line trace polygon loops natively inside Plotly engine
            categories_closed = categories + [categories[0]]
            values_closed = values + [values[0]]
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=values_closed,
                theta=categories_closed,
                fill='toself',
                name='Pillar Profile',
                fillcolor='rgba(26, 115, 232, 0.25)',
                line=dict(color='#1A73E8', width=3),
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[1.0, 5.0],
                        tickvals=[1.0, 2.0, 3.0, 4.0, 5.0],
                        tickfont=dict(size=10)
                    ),
                    angularaxis=dict(tickfont=dict(size=12)
                ),
                showlegend=False,
                margin=dict(l=80, r=80, t=40, b=40),
                height=500
            )
            
            # Split interface into a dual column layout
            col1, col2 = st.columns([1, 1.1], gap="medium")
            
            with col1:
                st.markdown("### 🕸️ Strategic Vector Performance")
                st.plotly_chart(fig, use_container_width=True)
                
            with col2:
                st.markdown("### 📋 Executive Summary Table")
                
                # Build an overview grid mapping scores out to their structural definitions
                grid_rows = []
                for pillar, val in final_scores_ordered.items():
                    tier_name, icon, _ = classify_tier(val)
                    grid_rows.append({
                        "Perill Strategic Pillar": pillar,
                        "Mean Score": f"{val:.2f} / 5.00",
                        "Classification Status": f"{icon} {tier_name}"
                    })
                st.table(pd.DataFrame(grid_rows))
            
            st.markdown("---")
            
            # ----------------------------------------------------
            # AUTOMATED INSIGHT GENERATION ENGINE
            # ----------------------------------------------------
            st.subheader("💡 Automated Insights Summary")
            
            # Determine maximums/minimums to parse strengths and structural deficiencies
            sorted_pillars = sorted(final_scores_ordered.items(), key=lambda item: item[1], reverse=True)
            max_score = sorted_pillars[0][1]
            min_score = sorted_pillars[-1][1]
            
            strengths_list = [p for p, v in sorted_pillars if v == max_score or (max_score - v) < 0.05]
            growth_list = [p for p, v in sorted_pillars if v == min_score or (v - min_score) < 0.05]
            
            c1, c2 = st.columns(2)
            
            with c1:
                st.success("#### 💪 Identified Strategic Strengths")
                for s in strengths_list:
                    tier_lbl, _, desc = classify_tier(final_scores_ordered[s])
                    st.markdown(f"**{s}** (`{final_scores_ordered[s]:.2f}` → {tier_lbl})")
                    st.caption(desc)
                    
            with c2:
                st.error("#### ⚠️ Primary Optimization Opportunities")
                for g in growth_list:
                    tier_lbl, _, desc = classify_tier(final_scores_ordered[g])
                    st.markdown(f"**{g}** (`{final_scores_ordered[g]:.2f}` → {tier_lbl})")
                    st.caption(desc)
                    
            st.markdown("### 🚀 Tailored Actionable Recommendations")
            
            # Pull suggestions for components tracking below target benchmarks
            action_items_rendered = 0
            for p_name, p_val in final_scores_ordered.items():
                if p_val < 3.5:  # Catches "Needs Support" and "Dysfunctional" tiers
                    action_items_rendered += 1
                    tier_lbl, icon, _ = classify_tier(p_val)
                    st.markdown(f"#### {icon} Due to underperformance in **{p_name}** ({p_val:.2f}):")
                    for recommendation in ACTIONABLE_SUGGESTIONS.get(p_name, []):
                        st.markdown(f"* 📍 {recommendation}")
                        
            if action_items_rendered == 0:
                st.info("🌟 **All pillars are currently tracking within target thresholds!** Direct your efforts toward continuous optimization frameworks and ongoing performance monitoring.")
