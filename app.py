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


def get_data(usr_file, data="connections") -> pd.DataFrame:

    if usr_file is None:
        return

    with ZipFile(usr_file, "r") as zipObj:
        # Extract all the contents of zip file in current directory
        zipObj.extractall("data")

    raw_df = pd.read_csv("data/Connections.csv", skiprows=3)

    if data == "messages":
        raw_df = pd.read_csv("data/messages.csv")

    # delete the data
    shutil.rmtree("data", ignore_errors=True)

    return raw_df


def main():
    # streamlit config
    st.set_page_config(
        page_title="Linkedin Network Visualizer",
        page_icon="🕸️",
        initial_sidebar_state="expanded",
        layout="wide",
    )
    st.markdown(
        """
        <h1 style='text-align: center; color: whtie;'>Linkedin Network Visualizer</h1>
        <h3 style='text-align: center; color: white;'>The missing feature in LinkedIn</h3>

        """,
        unsafe_allow_html=True,
    )

    # center image
    col1, col2, col3 = st.columns([1, 5, 1])
    col2.image("media/app/everything.png", use_column_width=True)

    st.subheader("First, upload your data 💾")
    st.caption(
        """
    Don't know where to find it?
    [Click here](https://github.com/benthecoder/linkedin-visualizer/tree/main/data_guide#how-to-get-the-data).
    """
    )
    # upload files
    usr_file = st.file_uploader("Drop your zip file 👇", type={"zip"})

    df_ori = get_data(usr_file)

    # if data not uploaded yet, return None
    if df_ori is None:
        return

    df_clean = clean_df(df_ori)

    with st.expander("Show raw data"):
        st.dataframe(df_ori)

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
    pos, comp, conn = st.columns(3)
    pos.metric("Top Position", f"{top_pos[0:18]}..." if len(top_pos) > 18 else top_pos)
    comp.metric(
        "Top Company", f"{top_comp[0:18]}..." if len(top_comp) > 18 else top_comp
    )
    conn.metric("Top Connection", f"{total_conn}", len(this_month_df))

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
    st.sidebar.subheader("Bar Charts")
    top_n = st.sidebar.slider("Top n", 0, 50, 10, key="1")

    # top n companies and positions
    st.subheader(f"Top {top_n} companies & positions")

    company_plt, positions_plt = st.columns(2)
    company_plt.plotly_chart(plot_bar(agg_df_company, top_n), use_container_width=True)
    positions_plt.plotly_chart(
        plot_bar(agg_df_position, top_n), use_container_width=True
    )

    col1, col2 = st.columns(2)
    with col1:
        with st.expander("View top companies data", expanded=True):
            st.dataframe(agg_df_company)
    with col2:
        with st.expander("View top positions data", expanded=True):
            st.dataframe(agg_df_position)

    # connections timeline
    st.subheader("Timeline of connections")
    st.plotly_chart(plot_timeline(df_clean), use_container_width=True)

    st.write("let's look at on what days do you have the most connections")
    st.plotly_chart(plot_day(df_clean), use_container_width=True)

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

    log_bool = False
    if st.sidebar.checkbox("Log scale"):
        log_bool = True

    st.subheader("Company Network")
    generate_network(df_clean, agg_df_company, log_bool, network_num)

    st.subheader("Positions Network")
    generate_network(df_clean, agg_df_position, log_bool, network_num)

    # emails
    st.write("Now to put your connections to good use")
    st.subheader("Who can you cold email 📧?")

    emails = df_clean[df_clean.notnull()["email_address"]].drop(
        ["connected_on", "weekday"], axis=1
    )

    st.write(f"Answer: {len(emails)} of your connections shared their emails!")
    st.dataframe(emails)

    st.sidebar.write(
        "Interested in the code? Head over to the [Github Repo](https://github.com/benthecoder/linkedin-visualizer)"
    )

    # chats
    st.markdown("---")
    st.subheader("Chats analysis")
    messages = get_data(usr_file, data="messages")
    messages["DATE"] = pd.to_datetime(messages["DATE"], format="%Y-%m-%d %H:%M:%S UTC")
    messages["DATE"] = (
        messages["DATE"].dt.tz_localize("UTC").dt.tz_convert("US/Central")
    )

    total, from_count, to_count = st.columns(3)
    total.metric("Total Conversations", f"{messages['CONVERSATION ID'].nunique()}")
    from_count.metric("Total Sent", f"{messages.FROM.nunique()}")
    to_count.metric("Total Received", f"{messages.TO.nunique()}")

    messages_FROM = agg_sum(messages, "FROM").iloc[1:]
    messages_TO = agg_sum(messages, "TO").iloc[1:]

    from_plt, to_plt = st.columns(2)
    from_plt.plotly_chart(
        plot_bar(messages_FROM, top_n, title="Messages FROM"), use_column_width=True
    )
    to_plt.plotly_chart(
        plot_bar(messages_TO, top_n, title="Messages TO"), use_column_width=True
    )

    st.write("what hour of the day do you have the most messages?")

    st.plotly_chart(plot_chat_hour(messages), use_container_width=True)

    st.write(
        "trend of your messages over time. p.s. hover over the line to see who you talked with"
    )
    st.plotly_chart(plot_chat_people(messages), use_container_width=True)

    st.subheader("wordcloud of all chats")

    with st.spinner("Wordcloud generating..."):
        st.pyplot(plot_wordcloud(messages))


if __name__ == "__main__":
    main()
