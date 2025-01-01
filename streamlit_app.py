import pandas as pd
import streamlit as st
import card_scraper
# Configure the page
st.set_page_config(page_title="Movies dataset", page_icon="🎟️")
st.title("🎟️ Scratchcard dataset")
st.write(
    """
    This app visualizes data from [Pais site (hishgad)](https://www.pais.co.il/hishgad/), 
    It shows which scratchcard has the best ROI.  
    Just click on the widgets below to explore!"""   
)

# Define the load_data function 
def load_data():
    try:
        # Check if there is data
        df_data = pd.read_pickle("scratchcards_database.pkl")["data"]
        df_data = card_scraper.calculate_ROI(df_data)
        df_data["ROI"] = df_data["ROI"].astype(float)
        return df_data
    except FileNotFoundError:
        # Handle the case where the pickle file doesn't exist
        st.error("Pickle file not found. Please run the data scraper first.")
        return pd.DataFrame()

# Load data
df_data = load_data()

# Validate data before continuing
if not df_data.empty:
    # Extract ticket_cost options
    ticket_cost_options = sorted(df_data.index.unique("ticket_cost").tolist())

    # Add widgets
    ticket_cost = st.multiselect(
        "Ticket Cost", ticket_cost_options, default=ticket_cost_options
    )
    ROI = st.slider("ROI", 1, 100, (1, 100))

    # Filter DataFrame
    df_filtered = df_data[
        (df_data.index.get_level_values("ticket_cost").isin(ticket_cost)) & (df_data["ROI"].between(ROI[0], ROI[1]))
    ]

    # Reset the index to convert MultiIndex levels into regular columns and reorder it
    df_filtered = df_filtered.reset_index()
    df_filtered = df_filtered[['image','name','ticket_cost','ROI', 'prize', 'prize_count']]

    # Display the filtered DataFrame with image URLs as preview images
    st.data_editor(
        df_filtered,
        column_config={
            "image": st.column_config.ImageColumn(
                "Image", help="Streamlit app preview screenshots"
            )
        },
        hide_index=True,
    )
