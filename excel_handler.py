import os
import pandas as pd
from datetime import datetime

EXCEL_FILE = "team_diagnostic.xlsx"

def initialize_excel():
    """Initializes the Excel workbook with standard configurations if it doesn't exist."""
    if os.path.exists(EXCEL_FILE):
        return

    departments = [
        "Human Resources", "Sales", "Engineering", "Finance", "Operations",
        "Marketing", "Academy", "Retail Customer & Experience", "Legal", "IT",
        "Data & Analytics", "IT Support", "Design / UX", "Cargo", "Lifestyle",
        "Supply Chain", "Procurement", "Corporate Strategy", "Public Relations", "Facilities"
    ]
    
    questions_data = [
        # Purpose & Motivation
        ("Our team has a clear, inspiring, and shared vision.", "Purpose & Motivation"),
        ("I clearly understand how my individual goals contribute to the team's objectives.", "Purpose & Motivation"),
        ("The team is highly motivated to achieve its long-term performance targets.", "Purpose & Motivation"),
        ("There is strong alignment across the team regarding our primary priorities.", "Purpose & Motivation"),
        ("Team members hold themselves and each other accountable for reaching our mission.", "Purpose & Motivation"),
        ("Our core team values are visibly lived out in our day-to-day work.", "Purpose & Motivation"),
        ("We frequently evaluate and realign on our collective purpose and value proposition.", "Purpose & Motivation"),
        ("Individual and team success metrics are highly clear, objective, and meaningful.", "Purpose & Motivation"),
        
        # External-facing systems & processes
        ("We proactively manage and nurture relationships with critical external stakeholders.", "External-facing systems & processes"),
        ("Our team is consistently successful at securing necessary resources and institutional support.", "External-facing systems & processes"),
        ("We effectively manage and de-escalate conflicting expectations from external groups.", "External-facing systems & processes"),
        ("We actively gather and integrate feedback from clients, customers, or cross-functional partners.", "External-facing systems & processes"),
        ("The team anticipates market shifts, regulatory changes, or external shocks effectively.", "External-facing systems & processes"),
        ("We maintain clear boundaries and service-level commitments with other internal teams.", "External-facing systems & processes"),
        ("External communications coming from our team are uniform, professional, and well-timed.", "External-facing systems & processes"),
        ("We successfully advocate for our team's structural interests within the broader organization.", "External-facing systems & processes"),
        
        # Relationships
        ("There is an exceptionally high level of interpersonal trust among all team members.", "Relationships"),
        ("It is entirely safe to take risks, voice dissenting opinions, and speak up on this team.", "Relationships"),
        ("Interpersonal conflicts within the team are managed constructively and respectfully.", "Relationships"),
        ("Team members genuinely support one another and collaborate rather than compete.", "Relationships"),
        ("Diversity of thought, background, and perspective is actively valued in daily operations.", "Relationships"),
        ("We systematically celebrate both individual milestones and collective team successes.", "Relationships"),
        ("Communication within the team is empathetic, transparent, and authentic.", "Relationships"),
        ("Mutual respect forms the unquestioned baseline for all day-to-day team interactions.", "Relationships"),
        
        # Internal-facing systems & processes
        ("Our day-to-day communication channels and platforms are efficient and clear.", "Internal-facing systems & processes"),
        ("Decision-making processes are transparent, well-understood, and executed predictably.", "Internal-facing systems & processes"),
        ("Work and operational responsibilities are delegated fairly and based on capability.", "Internal-facing systems & processes"),
        ("Our team meetings are highly productive, time-boxed, and result in clear action items.", "Internal-facing systems & processes"),
        ("Standard operating procedures (SOPs) and workflows are well-documented and optimized.", "Internal-facing systems & processes"),
        ("We use collaboration and project management tools effectively to track progress.", "Internal-facing systems & processes"),
        ("Roles and operational boundaries within the team are clearly delineated.", "Internal-facing systems & processes"),
        ("Time, bandwidth, and tasks are managed efficiently to meet deadlines consistently.", "Internal-facing systems & processes"),
        
        # Learning
        ("We routinely pause to reflect on our operational performance and workflows.", "Learning"),
        ("Mistakes are systematically treated as valuable opportunities for optimization and growth.", "Learning"),
        ("The team actively pursues continuous skill enhancement and upskilling opportunities.", "Learning"),
        ("We adapt fluidly and rapidly when institutional priorities or circumstances shift.", "Learning"),
        ("Calculated innovation and technical experimentation are actively encouraged.", "Learning"),
        ("We regularly cross-train and share specialized knowledge seamlessly across the team.", "Learning"),
        ("Post-mortem reviews are universally used to apply past lessons to new projects.", "Learning"),
        ("We strive for continuous marginal improvements rather than settling for the status quo.", "Learning"),
        
        # Leadership
        ("Team leadership provides clear, strategic direction and continuous guidance.", "Leadership"),
        ("Leadership fosters an environment of empowerment rather than micromanagement.", "Leadership"),
        ("Our leaders lead by example, demonstrating the team's core values transparently.", "Leadership"),
        ("Leadership actively and swiftly clears structural roadblocks that hinder performance.", "Leadership"),
        ("Leaders provide highly constructive, timely, and actionable feedback to team members.", "Leadership"),
        ("Leadership ensures that work distribution is sustainable and prevents burnout.", "Leadership"),
        ("Our leaders inspire systemic confidence and motivate the team through volatile periods.", "Leadership"),
        ("Leadership effectively communicates and contextualizes macro organizational updates.", "Leadership")
    ]

    config_rows = []
    for dept in departments:
        config_rows.append({"Type": "Department", "Content": dept, "Pillar": ""})
    for q_text, pillar in questions_data:
        config_rows.append({"Type": "Question", "Content": q_text, "Pillar": pillar})
        
    df_config = pd.DataFrame(config_rows)
    response_headers = ["Timestamp", "Department"] + [q[0] for q in questions_data]
    df_responses = pd.DataFrame(columns=response_headers)
    
    with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
        df_config.to_excel(writer, sheet_name="Configuration", index=False)
        df_responses.to_excel(writer, sheet_name="Responses", index=False)

def load_config():
    """Reads configuration sheet to fetch current departments and questions map."""
    initialize_excel()
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name="Configuration")
        depts = df[df["Type"] == "Department"]["Content"].dropna().tolist()
        questions_df = df[df["Type"] == "Question"]
        questions_map = dict(zip(questions_df["Content"], questions_df["Pillar"]))
        return depts, questions_map
    except Exception as e:
        return [], {}

def load_responses():
    """Loads all logs from the Responses sheet."""
    initialize_excel()
    try:
        return pd.read_excel(EXCEL_FILE, sheet_name="Responses")
    except Exception:
        return pd.DataFrame()

def save_submission(department, answers):
    """Appends an individual submission row into the Responses sheet."""
    initialize_excel()
    df_existing = load_responses()
    
    new_row = {"Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Department": department}
    new_row.update(answers)
    
    df_new_row = pd.DataFrame([new_row])
    
    if not df_existing.empty:
        df_combined = pd.concat([df_existing, df_new_row], ignore_index=True, sort=False)
    else:
        df_combined = df_new_row
        
    with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df_combined.to_excel(writer, sheet_name="Responses", index=False)

# Add this function to excel_handler.py to record admin activity
def log_admin_action(username, action, status="Success"):
    """Records administrative access attempts and actions into a secure ledger."""
    initialize_excel()
    log_file = "team_diagnostic.xlsx"
    
    # Define log entry structure
    new_log = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Username": username,
        "Action Executed": action,
        "Status": status
    }
    df_new_log = pd.DataFrame([new_log])
    
    try:
        # Try to load existing logs
        df_logs = pd.read_excel(log_file, sheet_name="AdminLogs")
        df_combined = pd.concat([df_logs, df_new_log], ignore_index=True, sort=False)
    except Exception:
        # If the sheet doesn't exist yet, start a fresh one
        df_combined = df_new_log

    # Save back to Excel safely
    with pd.ExcelWriter(log_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df_combined.to_excel(writer, sheet_name="AdminLogs", index=False)
