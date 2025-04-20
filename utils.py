import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import os

def union_find(vacated, compounds):
    """Union-find to check number of contiguous zones."""
    parent = {v: v for v in vacated}
    
    def find(u):
        if parent[u] != u:
            parent[u] = find(parent[u])  # Path compression
        return parent[u]
    
    for i in vacated:
        for adj in compounds[i-1]['adjacent']:
            if adj in vacated:
                pu = find(i)
                pv = find(adj)
                if pu != pv:
                    parent[pv] = pu
    
    roots = {find(u) for u in vacated}
    return len(roots)

def plot_pareto_front(fval, filename="pareto_front.png"):
    """Plot 2D Pareto front."""
    plt.figure(figsize=(8, 6))
    plt.scatter(-fval[:, 0], fval[:, 1]/1e4, c='blue', alpha=0.5)
    plt.xlabel('Vacated Compounds')
    plt.ylabel('Total Relocation Cost (10k Yuan)')
    plt.title('Pareto Front')
    plt.grid(True)
    plt.savefig(filename)
    plt.close()

def plot_cost_effectiveness(households, m, best_h, best_m, filename="cost_effectiveness.png"):
    """Plot cost-effectiveness vs. households."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=households, y=m, mode='lines+markers', name='m vs. Households'))
    fig.add_trace(go.Scatter(x=[best_h], y=[best_m], mode='markers', name='Inflection Point',
                             marker=dict(size=10, color='red')))
    fig.update_layout(
        title='Cost-effectiveness vs. Relocated Households',
        xaxis_title='Relocated Households',
        yaxis_title='Cost-effectiveness (m)',
        showlegend=True
    )
    fig.write_image(filename)