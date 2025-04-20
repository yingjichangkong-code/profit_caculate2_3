import streamlit as st
import pandas as pd
import json
import os
from data_handler import load_compounds, load_params
from problem_two import compute_problem_two
from problem_three import compute_problem_three
import plotly.graph_objects as go
from zipfile import ZipFile

st.set_page_config(page_title="Urban Renewal Decision Software", layout="wide")

st.title("Urban Renewal Decision Software")

# Sidebar for inputs
st.sidebar.header("Input Parameters")
cost_per_household = st.sidebar.number_input("Cost per Household (Yuan)", min_value=0, value=50000)
alpha = st.sidebar.number_input("Alpha (Rent Multiplier)", min_value=1.0, value=50.0)
years = st.sidebar.number_input("Investment Years", min_value=1, value=10)
target_m = st.sidebar.number_input("Target m", min_value=0.0, value=20.0)
population_size = st.sidebar.number_input("Population Size", min_value=10, value=100)
max_generations = st.sidebar.number_input("Max Generations", min_value=10, value=200)

params = {
    'cost_per_household': cost_per_household,
    'alpha': alpha,
    'years': years,
    'target_m': target_m,
    'population_size': population_size,
    'max_generations': max_generations
}

# File uploads
st.sidebar.header("Data Upload")
compounds_file = st.sidebar.file_uploader("Upload Compounds CSV", type="csv")
params_file = st.sidebar.file_uploader("Upload Parameters JSON", type="json")

# Load data
if compounds_file:
    compounds_df = pd.read_csv(compounds_file)
    compounds = [
        {
            'id': int(row['id']),
            'area': float(row['area']),
            'households': int(row['households']),
            'adjacent': eval(row['adjacent']),
            'rent': float(row['rent']),
            'alpha': 50.0
        } for _, row in compounds_df.iterrows()
    ]
else:
    compounds = load_compounds()

if params_file:
    params = json.load(params_file)

# Display and edit compounds
st.header("Compounds Data")
compounds_df = pd.DataFrame([
    {'id': c['id'], 'area': c['area'], 'households': c['households'],
     'adjacent': str(c['adjacent']), 'rent': c['rent']}
    for c in compounds
])
edited_df = st.data_editor(compounds_df, num_rows="dynamic")
if edited_df is not None:
    compounds = [
        {
            'id': int(row['id']),
            'area': float(row['area']),
            'households': int(row['households']),
            'adjacent': eval(row['adjacent']),
            'rent': float(row['rent']),
            'alpha': 50.0
        } for _, row in edited_df.iterrows()
    ]

# Run buttons
col1, col2, col3 = st.columns(3)
with col1:
    run_problem_two = st.button("Run Problem 2")
with col2:
    run_problem_three = st.button("Run Problem 3")
with col3:
    export = st.button("Export Results")

# Results
if run_problem_two:
    sorted_df, feasible_sequence = compute_problem_two(compounds, params)
    st.header("Problem 2 Results")
    st.write("Sorted Compounds by Marginal Cost-effectiveness:")
    st.dataframe(sorted_df)
    st.write(f"Feasible Sequence: {feasible_sequence}")
    sorted_df.to_csv("sorting_results.csv", index=False)

if run_problem_three:
    best_solution, results, F = compute_problem_three(compounds, params)
    st.header("Problem 3 Results")
    
    output = "=== Optimal Solution ===\n"
    if results['m'] >= params['target_m']:
        output += f"Found inflection point (m = {results['m']:.2f}):\n"
    else:
        output += f"No inflection point with m >= {params['target_m']:.1f}. Maximum m = {results['m']:.2f}:\n"
    output += f"- Vacated Compounds: {results['vacated_compounds']}\n"
    output += f"- Relocated Households: {results['households']}\n"
    output += f"- Total Relocation Cost: {results['cost']/1e4:.2f} 10k Yuan\n"
    output += f"- Total Vacated Area: {results['area']:.2f} m²\n"
    output += f"- Total Income: {results['income']/1e4:.2f} 10k Yuan\n"
    output += f"- Total Profit: {results['profit']/1e4:.2f} 10k Yuan\n"
    output += "- Vacated Compounds:\n"
    for i in results['vacated_ids']:
        c = next(c for c in compounds if c['id'] == i)
        output += f"  - Compound {i} (Area: {c['area']:.1f} m², Households: {c['households']})\n"
    output += "- Contiguous Zones:\n"
    for zone_idx, (root, cids) in enumerate(results['cluster_groups'].items(), 1):
        cluster_area = sum(c['area'] for c in compounds if c['id'] in cids)
        output += f"  Zone {zone_idx}: Compounds {sorted(cids)} (Total Area: {cluster_area:.1f} m²)\n"
    output += "- Relocation Details: Residents relocated to external housing.\n"
    
    st.text(output)
    
    # Visualizations
    st.subheader("Pareto Front")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=-F[:, 0], y=F[:, 1]/1e4, mode='markers', name='Pareto Front'))
    fig.update_layout(
        xaxis_title='Vacated Compounds',
        yaxis_title='Total Relocation Cost (10k Yuan)',
        title='Pareto Front'
    )
    st.plotly_chart(fig)
    
    st.subheader("Cost-effectiveness Curve")
    st.image("cost_effectiveness.png")
    
    with open("inflection_results.txt", "w") as f:
        f.write(output)

if export:
    with ZipFile("results.zip", "w") as z:
        if os.path.exists("sorting_results.csv"):
            z.write("sorting_results.csv")
        if os.path.exists("inflection_results.txt"):
            z.write("inflection_results.txt")
        if os.path.exists("pareto_front.png"):
            z.write("pareto_front.png")
        if os.path.exists("cost_effectiveness.png"):
            z.write("cost_effectiveness.png")
    with open("results.zip", "rb") as f:
        st.download_button("Download Results", f, file_name="results.zip")

if __name__ == "__main__":
    st.write("Urban Renewal Decision Software loaded successfully.")