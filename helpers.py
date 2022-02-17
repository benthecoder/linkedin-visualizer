from re import I
import streamlit.components.v1 as components
import pandas as pd

# fuzzy match
from thefuzz import fuzz
from thefuzz import process

# visualizations
import plotly.express as px
import networkx as nx
from pyvis.network import Network


def clean_df(df: pd.DataFrame, privacy: bool = False) -> pd.DataFrame:
    """This function cleans the dataframe containing LinkedIn
    connections data"


    Args:
        df (pd.DataFrame): data frame before cleaning

    Returns:
        pd.DataFrame: data frame after cleaning
    """
    if privacy:
        df.drop(columns=["first_name", "last_name", "email_address"])
    else:
        clean_df = (
            df
            # remomves spacing and capitalization in column names
            .clean_names()
            # drop missing values in company and position
            .dropna(subset=["company", "position"])
            # join first name and last name
            .concatenate_columns(
                column_names=["first_name", "last_name"],
                new_column_name="name",
                sep=" ",
            )
            # drop first name and last name
            .drop(columns=["first_name", "last_name"])
            # truncate company names that exceed
            .transform_column("company", lambda s: s[:35])
            .to_datetime("connected_on")
            .filter_string(
                column_name="company",
                search_string=r"[Ff]reelance|[Ss]elf-[Ee]mployed|\.|\-",
                complement=True,
            )
        )

    # fuzzy match on Data Scientist titles
    replace_fuzzywuzzy_match(clean_df, "position", "Data Scientist")
    # fuzzy match on Software Engineer titles
    replace_fuzzywuzzy_match(clean_df, "position",
                             "Software Engineer", min_ratio=85)

    return clean_df


def replace_fuzzywuzzy_match(
    df: pd.DataFrame, column: str, query: str, min_ratio: int = 75
):
    """Replace the fuzz matches with query string
    thefuzz github : https://github.com/seatgeek/thefuzz

    Args:
        df (pd.DataFrame): data frame of connections
        column (str): column to performn fuzzy matching
        query (str): query string
        min_ratio (int, optional): minimum score to remove. Defaults to 60.
    """

    # get list of all unique positions
    pos_names = df[column].unique()

    # get top 500 close matches
    matches = process.extract(query, pos_names, limit=500)

    # filter matches with ratio >= 75
    matching_pos_name = [match[0]
                         for match in matches if match[1] >= min_ratio]

    # for position in above_ratio:
    #     print(f"replacing {position} with {query}")

    # get rows of all close matches
    matches_rows = df[column].isin(matching_pos_name)

    # replace all rows containing close matches with query string
    df.loc[matches_rows, column] = query


def agg_sum(df: pd.DataFrame, name: str) -> pd.DataFrame:
    """Does a value count on company and positions and sorts by count

    Args:
        df (pd.DataFrame): data frame before aggregation
        name (str): company | position

    Returns:
        pd.DataFrame: aggregated data frame
    """
    df = df[name].value_counts().reset_index()
    df.columns = [name, "count"]
    df = df.sort_values(by="count", ascending=False)
    return df


def plot_bar(df: pd.DataFrame, rows: int):
    height = 500
    if rows > 25:
        height = 700

    name, count = list(df.columns)

    fig = px.histogram(
        df.head(rows),
        x=count,
        y=name,
        template="plotly_dark",
        hover_data={name: False},
    )
    fig.update_layout(
        height=height,
        width=700,
        margin=dict(pad=5),
        hovermode="y",
        xaxis_title="Count",
        yaxis_title="",
        yaxis=dict(autorange="reversed"),
    )
    return fig


def plot_timeline(df: pd.DataFrame):
    df = df["connected_on"].value_counts().reset_index()
    df.rename(columns={"index": "connected_on",
              "connected_on": "count"}, inplace=True)
    df = df.sort_values(by="connected_on", ascending=True)
    fig = px.line(df, x="connected_on", y="count")

    # add range slider
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list(
                    [
                        dict(count=1, label="1m", step="month",
                             stepmode="backward"),
                        dict(count=6, label="6m", step="month",
                             stepmode="backward"),
                        dict(count=1, label="YTD",
                             step="year", stepmode="todate"),
                        dict(count=1, label="1y", step="year",
                             stepmode="backward"),
                        dict(step="all"),
                    ]
                ),
                bgcolor="black",
            ),
            rangeslider=dict(visible=True),
            type="date",
        ),
        xaxis_title="Date",
    )

    return fig


def plot_cumsum(df: pd.DataFrame):
    df = df["connected_on"].value_counts().reset_index()
    df.rename(columns={"index": "connected_on",
              "connected_on": "count"}, inplace=True)
    df = df.sort_values(by="connected_on", ascending=True)
    df["cum_sum"] = df["count"].cumsum()

    fig = px.area(df, x='connected_on', y='cum_sum')

    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(visible=True),
            type="date",
        ),
        xaxis_title="Date",
        yaxis_title="count"
    )

    return fig


def generate_network(df: pd.DataFrame, agg_df: pd.DataFrame, cutoff: int = 5):
    """This function generates a network of connections of the user

    Args:
        df (pd.DataFrame): data frame containing
        agg_df (pd.DataFrame):
        cutoff (int, optional): the min number of connections at which nodes are created. Defaults to 5.
    """

    col_name = agg_df.columns[0]

    # initialize a graph
    g = nx.Graph()
    # intialize user as central node
    g.add_node("you")

    # create network and provide specifications
    nt = Network(height="700px", width="700px",
                 bgcolor="black", font_color="white")

    # reduce size of connections
    df_reduced = agg_df.loc[agg_df["count"] >= cutoff]

    # use iterrows tp iterate through the data frame
    for _, row in df_reduced.iterrows():

        # store company name and count
        name = row[col_name][:50]
        count = row["count"]

        title = f"<b>{name}</b> – {count}"
        positions = set([x for x in df[name == df[col_name]]["position"]])
        positions = "".join("<li>{}</li>".format(x) for x in positions)

        position_list = f"<ul>{positions}</ul>"
        hover_info = title + position_list

        g.add_node(name, size=count * 2, title=hover_info, color="#3449eb")
        g.add_edge("you", name, color="grey")

    # generate the graph
    nt.from_nx(g)
    nt.hrepulsion()
    nt.toggle_stabilization(True)
    nt.show("network.html")

    # Save and read graph as HTML file (on Streamlit Sharing)
    try:
        path = "/tmp"
        nt.save_graph(f"{path}/network.html")
        HtmlFile = open(f"{path}/network.html", "r", encoding="utf-8")

    # Save and read graph as HTML file (locally)
    except:
        path = "/html_files"
        nt.save_graph(f"{path}/network.html")
        HtmlFile = open(f"{path}/network.html", "r", encoding="utf-8")

    # Load HTML file in HTML component for display on Streamlit page
    components.html(HtmlFile.read(), width=1000, height=800)
