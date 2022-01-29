# import libraries
import streamlit as st
import pandas as pd
import janitor
import streamlit.components.v1 as components


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
    [Click here](https://tinyurl.com/yezvlquu) to find out
    """
    )

    st.caption("Don't worry, your data is in safe hands")

    usr_file = st.file_uploader("Upload your Connection.csv file 👇", type={"csv"})

    if not usr_file:
        return

    df_ori = pd.read_csv(usr_file, skiprows=2)
    df_clean = clean_df(df_ori)

    st.caption("Thank you! Now scroll down and enjoy!")
    st.subheader("See your data 👀")

    if st.checkbox("Show raw data"):
        st.dataframe(df_ori)

    if st.checkbox("Show clean data"):
        st.dataframe(df_clean)

    # data munging
    agg_df_company = agg_sum(df_clean, "company")
    agg_df_position = agg_sum(df_clean, "position")

    st.subheader("Here's a breakdown of your connections")

    # stats
    total_conn = len(df_ori)
    top_pos = agg_df_position["position"][0]
    top_comp = agg_df_company["company"][0]
    top_pos_count = agg_df_position["count"][0]

    first_c = df_clean.iloc[-1]
    last_c = df_clean.iloc[0]

    this_month_df = df_clean[
        (df_clean["connected_on"].dt.month == 1)
        & (df_clean["connected_on"].dt.year == 2022)
    ]

    st.caption("quick insight 🪄")
    conn, comp, pos = st.columns(3)
    conn.metric("Total Connections", f"{total_conn}", len(this_month_df))
    comp.metric("Top Company", f"{top_comp}")
    pos.metric("Top Position", f"{top_pos}")

    st.caption("full summary")
    st.markdown(
        f"""
        - You have _{len(this_month_df)}_ new connections this month, with a total of _{total_conn}_!
        - Most of your connections work at **{top_comp}**. Dream company?
        - You love connecting with people with the title – **{top_pos}**, _{top_pos_count}_ of them!
        - Your first ever connection is {first_c['name']} and they work as a {first_c.position} at {first_c.company}
        - Your most recent connection is {last_c['name']} and they work as a {last_c.position} at {last_c.company}
        """
    )

    st.sidebar.subheader("Sliders to plot more/less data")
    st.sidebar.subheader("Bar Charts")

    st.subheader("Top 10 companies")

    ## top n companeis and positions
    top_comp = st.sidebar.slider("Top n companies", 0, 50, 10, key="1")
    st.plotly_chart(plot_bar(agg_df_company, top_comp))
    if st.checkbox("View top companies data", key="company"):
        st.dataframe(agg_df_company)

    st.subheader("Top 10 positions")

    top_pos = st.sidebar.slider("Top n positions", 0, 50, 10, key="2")
    st.plotly_chart(plot_bar(agg_df_position, top_pos))

    if st.checkbox("View top positions data", key="position"):
        st.dataframe(agg_df_position)

    ## connections timeline
    st.subheader("Timeline of connections")
    st.plotly_chart(plot_line(df_clean["connected_on"]))

    ## Graph network
    st.sidebar.subheader("Connection network")
    network_num = st.sidebar.slider(
        "cutoff point for no. of conns (smaller = larger)", 2, 50, 6, key="3"
    )

    st.subheader("Company Network")
    generate_network(df_clean, agg_df_company, network_num)

    st.subheader("Position Network")
    generate_network(df_clean, agg_df_position, network_num)

    ## emails
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
