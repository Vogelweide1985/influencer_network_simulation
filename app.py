import streamlit as st
import networkx as nx
import random
import matplotlib.pyplot as plt


# Inject CSS to center subheaders
st.markdown(
    """
    <style>
    .centered-title {
        text-align: center;
        font-size: 32px;
        font-weight: bold;
        color: black;
    }
    .centered-subheader {
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        color: black;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def visualize_graph_with_purchases(G, title, pos, influencer_paths=False, show_peer_influence=True):
    plt.figure(figsize=(11.7, 8.3))

    # Copy the graph to avoid modifying the original
    G_copy = G.copy()

    # Remove influencer's edges and node if influencer_paths is False
    if not influencer_paths:
        influencer_neighbors = list(G_copy.neighbors(influencer_node))
        for neighbor in influencer_neighbors:
            G_copy.remove_edge(influencer_node, neighbor)
        G_copy.remove_node(influencer_node)

    # Draw nodes in "No-Buyer" state
    nx.draw_networkx_nodes(G_copy, pos,
                           nodelist=[n for n, d in G_copy.nodes(data=True) if d['state'] == "No-Buyer"],
                           node_color='grey',
                           alpha=0.6,
                           node_size=50)

    # Draw nodes in "Buyer" state (direct or peer-influenced)
    if show_peer_influence:
        # Draw peer-influenced buyers in green
        nx.draw_networkx_nodes(G_copy, pos,
                               nodelist=[n for n, d in G_copy.nodes(data=True) if d['state'] == "Buyer" and d['influenced_by'] == "peer"],
                               node_color='green',
                               alpha=0.6,
                               node_size=50)

    # Draw direct influencer buyers in blue
    nx.draw_networkx_nodes(G_copy, pos,
                           nodelist=[n for n, d in G_copy.nodes(data=True) if d['state'] == "Buyer" and d['influenced_by'] == "influencer"],
                           node_color='blue',
                           alpha=0.6,
                           node_size=50)

    # Draw edges between all network nodes except influencer's edges
    nx.draw_networkx_edges(G_copy, pos, alpha=0.2)

    # Only draw the influencer's edges and node if influencer_paths is True
    if influencer_paths:
        # Draw influencer node and paths with higher transparency
        influencer_neighbors = [n for n in G.neighbors(influencer_node)]
        influencer_edges = [(influencer_node, neighbor) for neighbor in influencer_neighbors]
        nx.draw_networkx_edges(G, pos, edgelist=influencer_edges, edge_color='blue', alpha=0.1)

        # Draw the influencer node itself
        nx.draw_networkx_nodes(G, pos,
                               nodelist=[influencer_node],
                               node_color='blue',
                               alpha=0.6,
                               node_size=100)

    plt.title(title)
    plt.axis('off')
    st.pyplot(plt)

# Function to count direct and peer-influenced buyers
def count_buying_nodes(G):
    direct_buyers = sum(1 for _, attributes in G.nodes(data=True) if attributes['state'] == "Buyer" and attributes['influenced_by'] == "influencer")
    peer_influenced_buyers = sum(1 for _, attributes in G.nodes(data=True) if attributes['state'] == "Buyer" and attributes['influenced_by'] == "peer")
    return direct_buyers, peer_influenced_buyers

# Streamlit user input for constants
st.markdown("<p class='centered-title'>Show your Viral Influencer Reach</p>", unsafe_allow_html=True)

NUM_PERSONS = st.slider('Select the Size of the Network. More People will create a denser network. Start with 500 people.', 100, 1000, 500)
INFLUENCER_NET_REACH = st.slider('How many people will you reach? (Influencer Net Reach in %) ', 0.0, 1.0, 0.15)
INFLUENCER_CONVINCING_PROB = st.slider('How many will you influence to buy the product in %?', 0.0, 1.0, 0.2)
FRIEND_SINGLE_BUYING_PROB = st.slider('What is the probability that the person will influence his friend?', 0.0, 1.0, 0.1)
FRIEND_MULTIPLE_BUYING_PROB = st.slider('What is the probability that two or more persons will influence a friend?', 0.0, 1.0, 0.25)

# Graph initialization
G = nx.random_geometric_graph(NUM_PERSONS, 0.1)
nx.set_node_attributes(G, "Person", "type")
nx.set_node_attributes(G, "No-Buyer", "state")
nx.set_node_attributes(G, "none", "influenced_by")  # New attribute to track influence source

# Set influencer
influencer_node = "Kampagne"
G.add_node(influencer_node, state="Influencer", type="Buyer", influenced_by="none")
G.nodes[influencer_node]['pos'] = (0.5, 1.1)
pos = nx.get_node_attributes(G, "pos")

# Graph 1: Initial network
st.markdown("<p class='centered-subheader'>Simulation of your Audience Network</p>", unsafe_allow_html=True)
visualize_graph_with_purchases(G, "Initial audience with their connections", pos)

# Step 2: Connect influencer to a fraction of the network
num_connections = int(INFLUENCER_NET_REACH * len(G.nodes))
nodes_to_connect = random.sample(list(G.nodes)[:-1], num_connections)
for node in nodes_to_connect:
    G.add_edge(influencer_node, node)



# Step 3: Convince nodes influenced by the influencer (no peer influence yet)
for neighbor in G.neighbors(influencer_node):
    if random.random() < INFLUENCER_CONVINCING_PROB:
        G.nodes[neighbor]['state'] = "Buyer"
        G.nodes[neighbor]['influenced_by'] = "influencer"

# Graph 3: Final network after direct influence (no peer influence yet)
st.markdown("<p class='centered-subheader'>Week 1: Influencer Campaign converts direct buyers</p>", unsafe_allow_html=True)
visualize_graph_with_purchases(G, "Buyers (blue) after Influencer Campaign", pos, show_peer_influence=False, influencer_paths=True)

# Step 4: Convince nodes influenced by peers (introducing peer influence)
for person, attributes in G.nodes(data=True):
    if attributes['state'] == "No-Buyer":
        buying_neighbors_count = sum(1 for neighbor in G.neighbors(person) if G.nodes[neighbor]['state'] == "Buyer")
        
        if buying_neighbors_count == 1 and random.random() < FRIEND_SINGLE_BUYING_PROB:
            G.nodes[person]['state'] = "Buyer"
            G.nodes[person]['influenced_by'] = "peer"
        elif buying_neighbors_count > 2 and random.random() < FRIEND_MULTIPLE_BUYING_PROB:
            G.nodes[person]['state'] = "Buyer"
            G.nodes[person]['influenced_by'] = "peer"

# Graph 4: Influence spread by convinced individuals in Week 1(show peer influence)
st.markdown("<p class='centered-subheader'>Week 2: Influence Spread by Convinced Individuals</p>", unsafe_allow_html=True)
visualize_graph_with_purchases(G, "Viral Reach after Campaign: Buyers (green) by Convinced Friends", pos)


# Step 5: Convince nodes influenced by peers Week 2 (introducing peer influence)
for person, attributes in G.nodes(data=True):
    if attributes['state'] == "No-Buyer":
        buying_neighbors_count = sum(1 for neighbor in G.neighbors(person) if G.nodes[neighbor]['state'] == "Buyer")
        
        if buying_neighbors_count == 1 and random.random() < FRIEND_SINGLE_BUYING_PROB:
            G.nodes[person]['state'] = "Buyer"
            G.nodes[person]['influenced_by'] = "peer"
        elif buying_neighbors_count > 2 and random.random() < FRIEND_MULTIPLE_BUYING_PROB:
            G.nodes[person]['state'] = "Buyer"
            G.nodes[person]['influenced_by'] = "peer"

# Graph 5: Influence spread by convinced individuals in Week 2 (show peer influence)
st.markdown("<p class='centered-subheader'>Week 3: Influence Spread by more Convinced Individuals</p>", unsafe_allow_html=True)
visualize_graph_with_purchases(G, "Viral Reach after Campaign: Buyers (green) by even more Convinced Friends", pos)

# Simulation summary
st.markdown("<p class='centered-subheader'>Simulation Summary</p>", unsafe_allow_html=True)
direct_buyers, peer_influenced_buyers = count_buying_nodes(G)
total_buyers = direct_buyers + peer_influenced_buyers
pct_direct = (direct_buyers / NUM_PERSONS) * 100
pct_peer = (peer_influenced_buyers / NUM_PERSONS) * 100

st.write(f"Total Buyers: {total_buyers} ({(total_buyers / NUM_PERSONS) * 100:.2f}%)")
st.write(f"Direct Buyers (Influenced by Influencer): {direct_buyers} ({pct_direct:.2f}%)")
st.write(f"Peer-Influenced Buyers: {peer_influenced_buyers} ({pct_peer:.2f}%)")
