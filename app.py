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


def get_data() -> pd.DataFrame:
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

    raw_df = pd.read_csv(f"data/{connections_file}", skiprows=3)

    # delete the data
    shutil.rmtree("data", ignore_errors=True)

    return raw_df


def main():
    # streamlit config
    st.set_page_config(
        page_title="Linkedin Network Visualizer",
        page_icon="🕸️",
        initial_sidebar_state="expanded",
    )

    # import bootstrap
    st.markdown(
        """
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        # LinkedIn Connection Insights 🪄
        #### The _missing feature_ in LinkedIn, get to know your connections today!
        #### First, upload your data 💾
        """
    )
    st.caption(
        """
    Don't know where to find it? 
    [Click here](https://github.com/benthecoder/linkedin-visualizer#how-to-get-the-data). Don't worry, [your data is in safe hands](https://docs.streamlit.io/streamlit-cloud/trust-and-security)
    """
    )

    df_ori = get_data()

    # if data not uploaded yet, return None
    if df_ori is None:
        return

    df_clean = clean_df(df_ori)

    st.markdown(
        """
        ---
        ### See your data 👀
        """
    )

    # View data
    if st.checkbox("Show raw data"):
        df_ori

    # Data wrangling
    agg_df_company = agg_sum(df_clean, "company")
    agg_df_position = agg_sum(df_clean, "position")

    this_month_df = df_clean[
        (df_clean["connected_on"].dt.month == 1)
        & (df_clean["connected_on"].dt.year == 2022)
    ]

    # Getting some stats
    total_conn = len(df_ori)
    top_pos = agg_df_position["position"][0]
    top_comp = agg_df_company["company"][0]
    second_comp = agg_df_company["company"][1]
    top_pos_count = agg_df_position["count"][0]
    first_c = df_clean.iloc[-1]
    last_c = df_clean.iloc[0]

    # calculating stats
    st.markdown(
        """
        ---    
        ### Here's a breakdown of your connections 👇
        """
    )

    # Metrics
    conn, comp = st.columns(2)
    conn.metric(
        "Total Position", f"{top_pos[0:18]}..." if len(top_pos) > 18 else top_pos
    )
    comp.metric(
        "Top Company", f"{top_comp[0:18]}..." if len(top_comp) > 18 else top_comp
    )
    st.metric("Top Connection", f"{total_conn}", len(this_month_df))

    # Summary
    st.subheader("Full summary")
    st.markdown(
        f"""
        - You have _{len(this_month_df)}_ new ⭐ connections this month, with a total of _{total_conn}_!
        - Most of your connections work at **{top_comp}**" (dream company?), closely followed by {second_comp}
        - You love connecting with people 🤵 with the title – **{top_pos}**, _{top_pos_count}_ of them!
        - Your first ever connection is {first_c['name']} and they work as a {first_c.position} at {first_c.company}
        - Your most recent connection is {last_c['name']} and they work as a {last_c.position} at {last_c.company}

        ---
        """
    )

    st.caption("Scroll down 🖱️⬇️ to see some cool visualizations!")

    # visualizations
    st.sidebar.subheader("Sliders to plot more/less data")
    st.sidebar.subheader("Bar Charts")

    top_n = st.sidebar.slider("Top n", 0, 50, 10, key="1")

    # top n companies and positions
    st.subheader(f"Top {top_n} companies")

    st.plotly_chart(plot_bar(agg_df_company, top_n), use_container_width=True)

    st.subheader(f"Top {top_n} positions")
    st.plotly_chart(plot_bar(agg_df_position, top_n), use_container_width=True)

    if st.checkbox("View top companies data", key="company"):
        st.dataframe(agg_df_company)
    if st.checkbox("View top positions data", key="position"):
        st.dataframe(agg_df_position)

    # connections timeline
    st.subheader("Timeline of connections")
    st.plotly_chart(plot_timeline(df_clean), use_container_width=True)

    # cumulative graph
    st.subheader("Connections overtime")
    st.plotly_chart(plot_cumsum(df_clean), use_container_width=True)

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

    st.subheader("Positions Network")
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
