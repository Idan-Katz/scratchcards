import pandas as pd
import streamlit as st
import card_scraper
import matplotlib.pyplot as plt
import re
from sklearn.linear_model import LinearRegression
# Configure the page
st.set_page_config(page_title="Scratchcard dataset", page_icon="🎟️")
st.markdown(
    """
    <div style="text-align: center;">
        <h1>🎟️ Scratchcard dataset</h1>
        <h5>This app visualizes data from the <a href="https://www.pais.co.il/hishgad/" target="_blank">Pais site (Hishgad)</a>.</h5>
        <h6>Helping you discover which scratchcard offers the best ROI (Return on Investment).</h6>
        <h6> Simply use the widgets below to dive in and explore!</h6>
    </div>
    """,
    unsafe_allow_html=True
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
        "Ticket Cost", ticket_cost_options
    )
    # If no ticket cost options are selected, set to all options
    if not ticket_cost:
        ticket_cost = ticket_cost_options

    ROI = st.slider("ROI", 1, 100, (1, 100))

    # Filter DataFrame
    df_filtered = df_data[
        (df_data.index.get_level_values("ticket_cost").isin(ticket_cost)) & (df_data["ROI"].between(ROI[0], ROI[1]))
    ]

    # Reset the index to convert MultiIndex levels into regular columns and reorder it
    df_filtered = df_filtered.reset_index()
    df_filtered = df_filtered[['image','name','ticket_cost','ROI', 'prize', 'prize_count']]

    # Regex to extract the first number (use '#' to comment on url for display_text later)
    regex = r"(?<=\/)(\d+)(?=_)"
    df_filtered['name'] = 'https://www.pais.co.il/hishgad/cards.aspx?cardId='+df_filtered['image'].apply(lambda x: re.search(regex, x).group(1) if re.search(regex, x) else None)+"#"+df_filtered['name']

    # Display the filtered DataFrame with image URLs as preview images and link to the card page

    st.data_editor(
        df_filtered,
        column_config={
            "image": st.column_config.ImageColumn(
                "Image", help="Streamlit app preview screenshots"
            ),
            "name": st.column_config.LinkColumn(
            help="The top trending Streamlit apps",
            max_chars=100,
            display_text=r".*#(.*)"
            ),
        },
        hide_index=True,
    )


if not df_data.empty:
    # Plot the data points
    plt.scatter(df_filtered["ticket_cost"], df_filtered["ROI"], color='blue', alpha=0.5, label='Ticket cost')

    # Fit a linear regression model
    if df_filtered["ticket_cost"].shape[0] > 0 and df_filtered["ROI"].shape[0] > 0:
        st.markdown(
        """
        <div style="text-align: center;">
        <h2>Higher stakes, higher rewards</h2>
        <h6>Unless anomalies ruin the fun!</h6>
        </div>
        """, unsafe_allow_html=True
        )
        model = LinearRegression()
        model.fit(df_filtered["ticket_cost"].values.reshape(-1, 1), df_filtered["ROI"])

        # Plot the linear regression line
        plt.plot(df_filtered["ticket_cost"], model.predict(df_filtered["ticket_cost"].values.reshape(-1, 1)), color='red', label='Trend')

        # Labels and title
        plt.xlabel('Ticket Cost')
        plt.ylabel('ROI')
        plt.title('Ticket Cost vs ROI')

        # Adjust layout for better fit
        plt.tight_layout()
        plt.grid(axis='y', linestyle="dashed", alpha=1)

        # Display the plot
        graph = st.pyplot(plt, use_container_width=True)