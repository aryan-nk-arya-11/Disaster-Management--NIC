import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Function to convert images to base64 strings for embedding in the dashboard
@st.cache_data
def get_image_as_base64(path):
    try:
        with open(path, "rb") as image_file:
            encoded_str = base64.b64encode(image_file.read()).decode()
        ext = path.split('.')[-1].lower()
        if ext in ["jpg", "jpeg"]:
            return f"data:image/jpeg;base64,{encoded_str}"
        elif ext == "png":
            return f"data:image/png;base64,{encoded_str}"
        else:
            return f"data:image/png;base64,{encoded_str}"
    except FileNotFoundError:
        st.warning(f"Image file not found at {path}. Show default or nothing.")
        return None

# Establishes and caches database connection using config from .toml file
@st.cache_resource
def init_db_connection():
    from sqlalchemy import create_engine
    import os
    config_path = os.path.join(".streamlit", "Dashboard2.toml")
    if os.path.exists(config_path):
        config = {}
        with open(config_path, 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip().strip('"')
        connection_url = config.get('url',
            f"mssql+pyodbc://{config.get('db_server', 'localhost')}/"
            f"{config.get('db_database', 'eoc')}?"
            "driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes")
    else:
        st.error("Dashboard2.toml file missing in .streamlit folder")
        return None
    return create_engine(connection_url)

# Function to load incident data with caching to improve app speed and responsiveness
@st.cache_data(ttl=1800)  # Cache for 30 mins
def load_data_from_db():
    try:
        engine = init_db_connection()
        if not engine:
            return pd.DataFrame()
        query = """
        SELECT CAST(HR.IncidentDate AS DATE) AS date,
            TRIM(MD.DistrictName) AS district,
            TRIM(MB.BlockName) AS block,
            H.Name AS incident_type,
            SUM(CASE WHEN HLR.HLCode = 2 THEN 1 ELSE 0 END) AS deaths,
            SUM(CASE WHEN HLR.HLCode = 1 THEN 1 ELSE 0 END) AS injured,
            CASE WHEN HR.IsFinal = 1 THEN 'Final'
                 WHEN HR.IsFinal = 2 THEN 'Verified'
                 ELSE 'Unknown' END AS entry_type
        FROM dbo.HazardReport AS HR
        LEFT JOIN dbo.Hazards AS H ON HR.HazardCode = H.ID
        LEFT JOIN dbo.mstDistricts AS MD ON HR.DistrictCode = MD.DistrictCode
        LEFT JOIN dbo.mstBlocks AS MB ON HR.BlockCode = MB.BlockCode AND HR.DistrictCode = MB.DistrictCode
        LEFT JOIN dbo.HumanLossReport AS HLR ON HR.ID = HLR.HzdReptID
        WHERE HR.IncidentDate >= DATEADD(YEAR, -5, GETDATE())  -- Last 5 years
        GROUP BY CAST(HR.IncidentDate AS DATE), MD.DistrictName, MB.BlockName, H.Name, HR.IsFinal
        ORDER BY date
        """
        df = pd.read_sql(query, engine)

        # Clean up data types and values
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        for col in ['district', 'block', 'incident_type', 'entry_type']:
            df[col] = df[col].astype(str).str.strip().str.title()
        for col in ['deaths', 'injured']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        df.drop_duplicates(inplace=True)
        df.reset_index(drop=True, inplace=True)

        return df
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return pd.DataFrame()

# Main dashboard running function
def run():
    df_main = load_data_from_db()

    if df_main.empty:
        st.error("No incident data loaded. Check DB connection or filters.")
        return

    st.title("Bihar Disaster Incident Dashboard")
    st.markdown(f"**Data last updated:** {datetime.now():%Y-%m-%d %H:%M:%S}")

    # Example KPI cards (total incidents, deaths, injured)
    total_incidents = df_main.shape[0]
    total_deaths = df_main['deaths'].sum()
    total_injured = df_main['injured'].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Incidents", total_incidents)
    col2.metric("Total Deaths", total_deaths)
    col3.metric("Total Injured", total_injured)

    # Further filter inputs, charts, and visualizations would go here...

if __name__ == "__main__":
    run()
