#networkapp

import streamlit as st
import networkx as nx
import random
import matplotlib.pyplot as plt

# Function to visualize the graph
def visualize_graph_with_purchases(G, title, pos, influencer_paths=False):
    plt.figure(figsize=(11.7, 8.3))

    # Draw nodes in "Nicht-Kauf" state
    nx.draw_networkx_nodes(G, pos,
                           nodelist=[n for n, d in G.nodes(data=True) if d['state'] == "Nicht-Kauf"],
                           node_color='grey',
                           alpha=0.6,
                           node_size=50)

    # Draw nodes in "Kauf" state
    nx.draw_networkx_nodes(G, pos,
                           nodelist=[n for n, d in G.nodes(data=True) if d['state'] == "Kauf"],
                           node_color='blue',
                           alpha=0.6,
                           node_size=50)

    # Draw edges
    nx.draw_networkx_edges(G, pos, alpha=0.2)

    if influencer_paths:
        # Draw influencer paths with higher transparency
        influencer_neighbors = [n for n in G.neighbors(influencer_node)]
        influencer_edges = [(influencer_node, neighbor) for neighbor in influencer_neighbors]
        nx.draw_networkx_edges(G, pos, edgelist=influencer_edges, edge_color='red', alpha=0.8)

    plt.title(title)
    plt.axis('off')
    st.pyplot(plt)

# Function to count the buying nodes
def count_buying_nodes(G):
    return sum(1 for _, attributes in G.nodes(data=True) if attributes['state'] == "Kauf")

# Streamlit user input for constants
st.title('Network Simulation with Influence Spread')

NUM_PERSONS = st.slider('Number of People', 100, 1000, 500)
INFLUENCER_NET_REACH = st.slider('Influencer Net Reach (%)', 0.0, 1.0, 0.15)
INFLUENCER_CONVINCING_PROB = st.slider('Influencer Convincing Probability', 0.0, 1.0, 0.2)
FRIEND_SINGLE_BUYING_PROB = st.slider('Friend Single Buying Probability', 0.0, 1.0, 0.1)
FRIEND_MULTIPLE_BUYING_PROB = st.slider('Friend Multiple Buying Probability', 0.0, 1.0, 0.2)

# Graph initialization
G = nx.random_geometric_graph(NUM_PERSONS, 0.1)
nx.set_node_attributes(G, "Person", "type")
nx.set_node_attributes(G, "Nicht-Kauf", "state")

# Set influencer
influencer_node = "Kampagne"
G.add_node(influencer_node, state="Influencer", type="Kauf")
G.nodes[influencer_node]['pos'] = (0.5, 1.1)
pos = nx.get_node_attributes(G, "pos")

# Graph 1: Initial network
st.subheader("Graph 1: Initial Network")
visualize_graph_with_purchases(G, "Initial Network", pos)

# Step 2: Connect influencer to a fraction of the network
num_connections = int(INFLUENCER_NET_REACH * len(G.nodes))
nodes_to_connect = random.sample(list(G.nodes)[:-1], num_connections)
for node in nodes_to_connect:
    G.add_edge(influencer_node, node)

# Graph 2: Network with influencer
st.subheader("Graph 2: Network with Influencer Connections")
visualize_graph_with_purchases(G, "Network with Influencer", pos, influencer_paths=True)

# Step 3: Convince nodes influenced by the influencer
for neighbor in G.neighbors(influencer_node):
    if random.random() < INFLUENCER_CONVINCING_PROB:
        G.nodes[neighbor]['state'] = "Kauf"

# Step 4: Convince nodes influenced by friends
for person, attributes in G.nodes(data=True):
    if attributes['state'] == "Nicht-Kauf":
        buying_neighbors_count = sum(1 for neighbor in G.neighbors(person) if G.nodes[neighbor]['state'] == "Kauf")
        
        if buying_neighbors_count == 1 and random.random() < FRIEND_SINGLE_BUYING_PROB:
            G.nodes[person]['state'] = "Kauf"
        elif buying_neighbors_count > 2 and random.random() < FRIEND_MULTIPLE_BUYING_PROB:
            G.nodes[person]['state'] = "Kauf"

# Graph 3: Final network after peer influence
st.subheader("Graph 3: Network after Peer Influence")
visualize_graph_with_purchases(G, "Network after Peer Influence", pos)

# Step 5: Influence spread from convinced individuals to their friends (New Feature)
for person, attributes in G.nodes(data=True):
    if attributes['state'] == "Kauf":
        for neighbor in G.neighbors(person):
            if random.random() < FRIEND_SINGLE_BUYING_PROB:
                G.nodes[neighbor]['state'] = "Kauf"

# Graph 4: Influence spread by convinced individuals
st.subheader("Graph 4: Influence Spread by Convinced Individuals")
visualize_graph_with_purchases(G, "Influence Spread by Convinced Individuals", pos)

# Simulation summary
st.subheader("Simulation Summary")
node_kauf_list = count_buying_nodes(G)
pct_kauf = node_kauf_list / NUM_PERSONS
st.write(f"Percentage of 'Kauf' nodes: {pct_kauf * 100:.2f}%")
