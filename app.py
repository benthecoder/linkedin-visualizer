# import libraries
import re
import streamlit as st
import pandas as pd
import janitor
import streamlit.components.v1 as components
from zipfile import ZipFile
from pathlib import Path
import shutil

# helper functions
from helpers import *


def main():
    # streamlit config
    st.set_page_config(
        page_title="Linkedin Network Visualizer",
        page_icon="🕸️",
        initial_sidebar_state="expanded",
    )

    st.title("LinkedIn Connection Insights 🪄")
    st.subheader("Get helpful information about your LinkedIn connection!")
    st.subheader("First, upload your data 💾")
    st.write(
        """
    Don't know where to find it? 
    [Click here](https://github.com/benthecoder/linkedin-visualizer#how-to-get-the-data)
    """
    )

    st.write(
        """Don't worry, [your data is in safe hands](https://docs.streamlit.io/streamlit-cloud/trust-and-security)"""
    )

    # remove data folder in case it exists
    shutil.rmtree("data", ignore_errors=True)

    # upload files
    usr_file = st.file_uploader("Upload/Drop your downloaded zip file 👇", type={"zip"})

    if usr_file is None:
        return

    with ZipFile(usr_file, "r") as zipObj:
        # Extract all the contents of zip file in current directory
        zipObj.extractall("data")

    for p in Path("./data").glob("*.csv"):
        connections_file = p.name

    df_ori = pd.read_csv(f"data/{connections_file}", skiprows=3)
    # shutil.rmtree("data", ignore_errors=True)
    df_clean = clean_df(df_ori)

    st.caption("Thank you! Now scroll down and enjoy!")
    st.subheader("See your data 👀")

    # View data
    if st.checkbox("Show raw data"):
        st.dataframe(df_ori)

    if st.checkbox("Show clean data"):
        st.dataframe(df_clean)

    # Data wrangling
    agg_df_company = agg_sum(df_clean, "company")
    agg_df_position = agg_sum(df_clean, "position")

    # calculating stats
    st.subheader("Here's a breakdown of your connections 🪄")

    total_conn = len(df_ori)
    top_pos = agg_df_position["position"][0]
    top_comp = agg_df_company["company"][0]
    second_comp = agg_df_company["company"][1]
    top_pos_count = agg_df_position["count"][0]
    first_c = df_clean.iloc[-1]
    last_c = df_clean.iloc[0]

    this_month_df = df_clean[
        (df_clean["connected_on"].dt.month == 1)
        & (df_clean["connected_on"].dt.year == 2022)
    ]

    # Metrics
    conn, comp = st.columns(2)
    conn.metric("Total Connections", f"{total_conn}", len(this_month_df))
    comp.metric("Top Company", f"{top_comp}")
    st.metric("Top Position", f"{top_pos}")

    # Summary
    st.caption("full summary")
    st.markdown(
        f"""
        - You have _{len(this_month_df)}_ new ⭐ connections this month, with a total of _{total_conn}_!
        - Most of your connections work at **{top_comp}** (dream company?), closely followed by {second_comp}
        - You love connecting with people 🤵 with the title – **{top_pos}**, _{top_pos_count}_ of them!
        - Your first ever connection is {first_c['name']} and they work as a {first_c.position} at {first_c.company}
        - Your most recent connection is {last_c['name']} and they work as a {last_c.position} at {last_c.company}
        """
    )

    st.caption("Scroll down 🖱️⬇️ to see some cool visualizations!")

    # visualizations
    st.sidebar.subheader("Sliders to plot more/less data")
    st.sidebar.subheader("Bar Charts")

    # top n companies and positions
    st.subheader("Top 10 companies")
    top_n = st.sidebar.slider("Top n", 0, 50, 10, key="1")
    st.plotly_chart(plot_bar(agg_df_company, top_n))

    st.subheader("Top 10 positions")
    st.plotly_chart(plot_bar(agg_df_position, top_n))

    if st.checkbox("View top companies data", key="company"):
        st.dataframe(agg_df_company)
    if st.checkbox("View top positions data", key="position"):
        st.dataframe(agg_df_position)

    # connections timeline
    st.subheader("Timeline of connections")
    st.plotly_chart(plot_timeline(df_clean))

    # cumulative graph
    st.subheader("Connections overtime")
    st.plotly_chart(plot_cumsum(df_clean))

    # Graph network
    st.sidebar.subheader("Connection network")
    network_num = st.sidebar.slider(
        "cutoff point for connections (the smaller it is the larger the network)",
        2,
        50,
        6,
        key="3",
    )

    st.subheader("Company Network")
    generate_network(df_clean, agg_df_company, network_num)

    st.subheader("Position Network")
    generate_network(df_clean, agg_df_position, network_num)

    # emails
    st.write("Now to put your connections to good use")
    st.subheader("Who can you cold email 📧?")

    emails = df_clean[df_clean.notnull()["email_address"]].drop(
        ["connected_on"], axis=1
    )

    st.write(f"Answer: {len(emails)} of your connections shared their emails!")
    st.dataframe(emails)

    st.sidebar.write(
        "Interested in the code? Head over to the [Github Repo](https://github.com/benthecoder/linkedin-visualizer)"
    )


if __name__ == "__main__":
    main()
