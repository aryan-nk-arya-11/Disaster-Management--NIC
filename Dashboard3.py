import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Function to establish and cache SQL database connection
@st.cache_resource
def init_db_connection():
    from sqlalchemy import create_engine
    import os
    # Load DB config from .toml file
    config_path = os.path.join(".streamlit", "Dashboard3.toml")
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
        st.error("Dashboard3.toml file missing in .streamlit folder")
        return None
    return create_engine(connection_url)

# Cached function to load and process flood data from the database
@st.cache_data(ttl=900)  # Cache the data for 15 minutes
def load_data_from_db():
    try:
        engine = init_db_connection()
        if not engine:
            st.info("Database connection unavailable. Loading sample data instead.")
            return pd.DataFrame()  # Return empty or sample data here if needed

        # SQL query to fetch key disaster metrics and details
        sql_query = """
            SELECT
                dm.DistrictName AS District,
                m.RecordDate AS Date,
                d.pdHumanAffected AS TotalPopulationAffected,
                d.pdMigratedPopulation AS TotalPopulationEvacuated,
                d.pdDeadPeoples AS NumberOfDeaths,
                d.pdAffectedAnimals AS TotalAnimalsAffected,
                d.pdAffectedKutchaHouses AS PartlyAffectedKutchaHouses,
                d.pdAffectedPakkaHouses AS PartlyAffectedPakkaHouses,
                d.pdAffectedHuts AS TotalHouseDamage,
                d.pdAffectedAgriLand AS AgricultureArea,
                d.pdDamagedCropArea AS CropDamageArea,
                d.pdFoodPackets AS FoodPacketsDistributed,
                d.pdReliefCentreOpened AS TotalReliefCentres,
                d.pdPeopleRegistered AS TotalPersonsInRelief,
                d.pdHealthCampToday AS TotalHealthCentres,
                d.pdPeopleTreated AS TotalPersonsTreated,
                d.pdMotorBoatToday AS TotalBoatsDeployed
            FROM dbo.FloodMain AS m
            JOIN dbo.FloodDetailsCum AS d ON m.ID = d.ID
            JOIN dbo.mstDistricts AS dm ON m.DistrictCode = dm.DistrictCode
            ORDER BY m.RecordDate DESC;
        """
        df = pd.read_sql(sql_query, engine)

        # Data cleaning and formatting for better dashboard use
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        for col in ['District']:
            df[col] = df[col].astype(str).str.strip().str.title()
        numeric_cols = [
            'TotalPopulationAffected', 'TotalPopulationEvacuated', 'NumberOfDeaths', 'TotalAnimalsAffected',
            'PartlyAffectedKutchaHouses', 'PartlyAffectedPakkaHouses', 'TotalHouseDamage', 'AgricultureArea',
            'CropDamageArea', 'FoodPacketsDistributed', 'TotalReliefCentres', 'TotalPersonsInRelief',
            'TotalHealthCentres', 'TotalPersonsTreated', 'TotalBoatsDeployed'
        ]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        df.drop_duplicates(inplace=True)
        df.reset_index(drop=True, inplace=True)

        return df
    except Exception as e:
        st.error(f"Failed to load data from DB: {e}")
        return pd.DataFrame()

# Main function to render Streamlit dashboard
def run():
    df_main = load_data_from_db()

    if df_main.empty:
        st.error("Unable to load flood disaster data. Please check your DB connection or try again later.")
        return

    # Dashboard title and last update time
    st.title("Bihar Flood Disaster Dashboard")
    st.markdown(f"**Last Data Update:** {datetime.now():%Y-%m-%d %H:%M:%S}")

    # Display critical KPIs at a glance using columns
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Population Affected", int(df_main['TotalPopulationAffected'].sum()))
    col2.metric("Total Deaths", int(df_main['NumberOfDeaths'].sum()))
    col3.metric("Food Packets Distributed", int(df_main['FoodPacketsDistributed'].sum()))

    # Additional charts and filters can be added here

if __name__ == "__main__":
    run()
