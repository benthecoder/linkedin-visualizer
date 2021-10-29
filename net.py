import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components

def generate_network(df, agg_df, cutoff=5):

    g = nx.Graph()
    g.add_node('root') # intialize user as central node

    nt = Network(height='700px', width='700px', bgcolor="black", font_color='white')

    # reduce size of connections
    df_reduced = agg_df.loc[agg_df['count']>=cutoff]
    
    # use iterrows tp iterate through the data frame
    for _, row in df_reduced.iterrows():
        
        # store company name and count
        company = row['company']
        count = row['count']

        title = f"<b>{company}</b> – {count}"
        positions = set([x for x in df[company == df['company']]['position']])
        positions = ''.join('<li>{}</li>'.format(x) for x in positions)

        position_list = f"<ul>{positions}</ul>"
        hover_info = title + position_list

        g.add_node(company, size=count*2, title=hover_info, color='#3449eb')
        g.add_edge('root', company, color='grey')

    # generate the graph
    nt.from_nx(g)
    nt.hrepulsion()
    nt.show('company_network.html')

    # Save and read graph as HTML file (on Streamlit Sharing)
    try:
        path = '/tmp'
        nt.save_graph(f'{path}/company_network.html')
        HtmlFile = open(f'{path}/company_network.html', 'r', encoding='utf-8')

    # Save and read graph as HTML file (locally)
    except:
        path = '/html_files'
        nt.save_graph(f'{path}/company_network.html')
        HtmlFile = open(f'{path}/company_network.html', 'r', encoding='utf-8')

    # Load HTML file in HTML component for display on Streamlit page
    components.html(HtmlFile.read(), width=1000, height=1000)