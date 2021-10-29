# import libraries
import streamlit as st
import pandas as pd
import janitor
import streamlit.components.v1 as components

# plotting libraries
import plotly.express as px

# helper functions
from net import generate_network
from clean_df import clean_df


def agg_sum(df):
    df = df.value_counts().reset_index()
    df.columns = ['company', 'count']
    df = df.sort_values(by="count", ascending=False)
    return df

def plot_bar(df, rows):
    height = 500
    if rows > 25:
        height = 700
    
    fig = px.histogram(df.head(rows), x = 'count', y='company', 
    template='plotly_dark', hover_data={'company':False})
    fig.update_layout(
        height=height,
        width=700,
        margin=dict(
        pad=5
        ),
        hovermode="y",
        xaxis_title="Count",
        yaxis_title="",
        yaxis = dict(autorange="reversed")
    )
    return fig

def plot_hist(df):
    fig = px.histogram(df, x="connected_on", nbins=15, template='plotly_dark')
    fig.update_layout(bargap=0.2, xaxis_title="Date")
    return fig


def main():
    # streamlit config
    st.set_page_config(
        page_title="Linkedin Network Visualizer",
        page_icon="🕸️",
        initial_sidebar_state="expanded"
    )

    st.title('LinkedIn Connection Network 🕸️')
    st.caption('Visualize your LinkedIn network now!')
    st.subheader("Upload data 💾")
    st.write('''
    Don't know where to find it? 
    Read [this article](https://medium.com/bitgrit-data-science-publication/visualize-your-linkedin-network-with-python-59a213786c4) to find out
    ''')
    usr_file = st.file_uploader("Upload your Connection.csv file 👇", type={"csv"})

    if not usr_file:
        return
    
    df_ori = pd.read_csv(usr_file, skiprows=2)
    df_clean = clean_df(df_ori)

    st.subheader("See your data 👀")
    
    if st.checkbox('Show raw data'):
        st.dataframe(df_ori)
    
    if st.checkbox('Show clean data'):
        st.dataframe(df_clean)

    # eda plots
    agg_df_company = agg_sum(df_clean['company'])
    agg_df_position = agg_sum(df_clean['position'])

    st.subheader("Top 10 companies")
    st.sidebar.subheader("Top 10 companies")
    if st.sidebar.checkbox('Show Top 10 companies data'):
        st.dataframe(agg_df_company, width=500)
    
    top_comp = st.sidebar.slider('Select Top n companies', 0, 50, 10, key="1")
    st.plotly_chart(plot_bar(agg_df_company, top_comp))

    st.subheader("Top 10 positions")
    st.sidebar.subheader("Top 10 position")
    if st.sidebar.checkbox('Show Top 10 positions data'):
        st.dataframe(agg_df_position, width=500)

    top_pos = st.sidebar.slider('Select Top n positions', 0, 50, 10,  key="2")
    st.plotly_chart(plot_bar(agg_df_position, top_pos))

    st.subheader("Timeline of connections")
    st.plotly_chart(plot_hist(df_clean['connected_on']))

    # generating network
    st.subheader("Connection Network")
    st.sidebar.subheader("Connection network")
    network_num = st.sidebar.slider('Select cutoff point (smaller = larger network)', 2, 50, 6,  key="3")
    generate_network(df_clean, agg_df_company, network_num)

    st.sidebar.write("[Source Code](https://github.com/benthecoder/linkedin-visualizer)")


if __name__ == '__main__':
    main()