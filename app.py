import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import excel_handler as eh

# Page Configuration Setup
st.set_page_config(page_title="Perill Team Diagnostic App", layout="wide", page_icon="🛡️")

# Initialize and pull configurations
eh.initialize_excel()
departments, questions_map = eh.load_config()

def classify_tier(score):
    if 4.5 <= score <= 5.0:
        return "High Performing", "🟩", "This pillar shows world-class execution and alignment."
    elif 3.5 <= score < 4.5:
        return "Performing, Balanced", "🟨", "Solid baseline with minor optimizations required."
    elif 2.5 <= score < 3.5:
        return "Needs Support", "🟧", "Clear systemic vulnerabilities needing targeted intervention."
    else:
        return "Dysfunctional", "🟥", "Critical operational risk requiring urgent restructuring."

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

# Application UI Header
st.title("🛡️ Perill Team Effectiveness Diagnostic Suite")
st.markdown("---")

# Navigation Sidebar Panel
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
            
            # Group questions dynamically by their assigned pillar
            pillars_grouped = {}
            for q, p in questions_map.items():
                pillars_grouped.setdefault(p, []).append(q)
                
            form_answers = {}
            
            for pillar, queries in pillars_grouped.items():
                st.subheader(f"🔷 Pillar: {pillar}")
                for q_text in queries:
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
# VIEW 2: ADMINISTRATOR DASHBOARD (Gatekeeping Free)
# ==========================================
elif view_mode == "📊 Administrator Dashboard":
    st.header("Admin Analytics & Diagnostics Engine")
    
    df_res = eh.load_responses()
    
    if df_res.empty or len(df_res) == 0:
        st.info("The application backend database contains no response records yet. Complete an evaluation survey to initialize metrics.")
    else:
        st.sidebar.subheader("Filter Configurations")
        all_depts = sorted(df_res["Department"].dropna().unique().tolist())
        
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
            # ADVANCED METRIC PROCESSING MECHANICS (Feature Upgrade 3)
            # ----------------------------------------------------
            active_questions = [q for q in questions_map.keys() if q in filtered_df.columns]
            
            # Coerce columns to numeric structures explicitly to run computations safely
            for col in active_questions:
                filtered_df[col] = pd.to_numeric(filtered_df[col], errors='coerce')
            
            # Dictionaries to aggregate raw score pools for statistical processing
            pillar_raw_scores = {}
            for q_text in active_questions:
                pillar = questions_map[q_text]
                pillar_raw_scores.setdefault(pillar, [])
                valid_scores = filtered_df[q_text].dropna().tolist()
                pillar_raw_scores[pillar].extend(valid_scores)
            
            perill_order = [
                "Purpose & Motivation", 
                "External-facing systems & processes", 
                "Relationships", 
                "Internal-facing systems & processes", 
                "Learning", 
                "Leadership"
            ]
            
            final_means = {}
            final_stdevs = {}
            
            # Calculate mean and standard deviation across the full distribution of each pillar
            for pillar in perill_order:
                scores_list = pillar_raw_scores.get(pillar, [])
                if scores_list:
                    final_means[pillar] = np.mean(scores_list)
                    final_stdevs[pillar] = np.std(scores_list, ddof=1) if len(scores_list) > 1 else 0.0
                else:
                    final_means[pillar] = 0.0
                    final_stdevs[pillar] = 0.0
            
            # ----------------------------------------------------
            # VISUALIZATION ENGINE - PLOTLY RADAR
            # ----------------------------------------------------
            categories = perill_order
            values = [final_means[p] for p in perill_order]
            
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
                    angularaxis=dict(tickfont=dict(size=12))
                ),
                showlegend=False,
                margin=dict(l=80, r=80, t=40, b=40),
                height=500
            )
            
            col1, col2 = st.columns([1, 1.2], gap="medium")
            
            with col1:
                st.markdown("### 🕸️ Strategic Vector Performance")
                st.plotly_chart(fig, use_container_width=True)
                
            with col2:
                st.markdown("### 📋 Executive Summary Table")
                
                # Build summary matrix containing standard deviation metrics
                grid_rows = []
                for pillar in perill_order:
                    mean_val = final_means[pillar]
                    std_val = final_stdevs[pillar]
                    tier_name, icon, _ = classify_tier(mean_val)
                    
                    grid_rows.append({
                        "Perill Strategic Pillar": pillar,
                        "Mean Score": f"{mean_val:.2f} / 5.00",
                        "Standard Deviation (σ)": f"{std_val:.2f}",
                        "Classification Status": f"{icon} {tier_name}"
                    })
                st.table(pd.DataFrame(grid_rows))
            
            st.markdown("---")
            
            # ----------------------------------------------------
            # ADVANCED VARIANCE INSIGHT GENERATOR (Feature Upgrade 3)
            # ----------------------------------------------------
            st.subheader("🔍 Polarization & Variance Analysis")
            
            polarized_pillars = []
            for p, std_v in final_stdevs.items():
                if std_v > 1.15:
                    polarized_pillars.append((p, std_v))
            
            if polarized_pillars:
                st.error("⚠️ **High Polarization Warning detected within specific pillars!**")
                st.markdown(
                    "A standard deviation higher than **1.15** indicates that your team members do not agree on these conditions. "
                    "The mean score looks neutral, but the data reveals an internal polarization (e.g., some members rating it highly positive while others rate it highly negative):"
                )
                
                p_cols = st.columns(len(polarized_pillars))
                for idx, (p_name, std_v) in enumerate(polarized_pillars):
                    with p_cols[idx]:
                        st.metric(
                            label=f"Polarized: {p_name}", 
                            value=f"σ = {std_v:.2f}", 
                            delta="High Disagreement", 
                            delta_color="inverse"
                        )
                        st.caption(f"Recommendation: Avoid using simple averages to evaluate *{p_name}*. Address internal workflow division immediately.")
            else:
                st.success("✅ **High Internal Consistency:** Standard deviation checks confirm cohesive responses across the dataset. Team perspectives are unified.")
            
            st.markdown("---")
            
            # ----------------------------------------------------
            # AUTOMATED INSIGHT GENERATION ENGINE
            # ----------------------------------------------------
            st.subheader("💡 Automated Insights Summary")
            
            sorted_pillars = sorted(final_means.items(), key=lambda item: item[1], reverse=True)
            max_score = sorted_pillars[0][1]
            min_score = sorted_pillars[-1][1]
            
            strengths_list = [p for p, v in sorted_pillars if v == max_score or (max_score - v) < 0.05]
            growth_list = [p for p, v in sorted_pillars if v == min_score or (v - min_score) < 0.05]
            
            c1, c2 = st.columns(2)
            
            with c1:
                st.success("#### 💪 Identified Strategic Strengths")
                for s in strengths_list:
                    tier_lbl, _, desc = classify_tier(final_means[s])
                    st.markdown(f"**{s}** (`{final_means[s]:.2f}` → {tier_lbl})")
                    st.caption(desc)
                    
            with c2:
                st.error("#### ⚠️ Primary Optimization Opportunities")
                for g in growth_list:
                    tier_lbl, _, desc = classify_tier(final_means[g])
                    st.markdown(f"**{g}** (`{final_means[g]:.2f}` → {tier_lbl})")
                    st.caption(desc)
                    
            st.markdown("### 🚀 Tailored Actionable Recommendations")
            
            action_items_rendered = 0
            for p_name, p_val in final_means.items():
                if p_val < 3.5:
                    action_items_rendered += 1
                    tier_lbl, icon, _ = classify_tier(p_val)
                    st.markdown(f"#### {icon} Due to underperformance in **{p_name}** ({p_val:.2f}):")
                    for recommendation in ACTIONABLE_SUGGESTIONS.get(p_name, []):
                        st.markdown(f"* 📍 {recommendation}")
                        
            if action_items_rendered == 0:
                st.info("🌟 **All pillars are currently tracking within target thresholds!** Direct your efforts toward continuous optimization frameworks and ongoing performance monitoring.")
