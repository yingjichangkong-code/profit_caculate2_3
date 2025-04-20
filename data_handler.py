import pandas as pd
import json
import os
import ast

def load_compounds(filename="templates/compounds.csv"):
    """Load compound data from CSV."""
    if not os.path.exists(filename):
        create_default_data()
    df = pd.read_csv(filename)
    compounds = []
    for _, row in df.iterrows():
        compounds.append({
            'id': int(row['id']),
            'area': float(row['area']),
            'households': int(row['households']),
            'adjacent': ast.literal_eval(row['adjacent']),
            'rent': float(row['rent']),
            'alpha': 50.0
        })
    return compounds

def load_params(filename="templates/config.json"):
    """Load parameters from JSON."""
    if not os.path.exists(filename):
        create_default_data()
    with open(filename, 'r') as f:
        params = json.load(f)
    return params

def create_default_data():
    """Create default compounds.csv and config.json if not exist."""
    compounds_data = [
        {'id': 1, 'area': 54, 'households': 1, 'adjacent': [21, 2], 'rent': 100},
        {'id': 2, 'area': 42, 'households': 1, 'adjacent': [1, 3], 'rent': 100},
        {'id': 3, 'area': 487, 'households': 6, 'adjacent': [2, 4], 'rent': 100},
        {'id': 4, 'area': 93, 'households': 4, 'adjacent': [3, 5], 'rent': 100},
        {'id': 5, 'area': 116, 'households': 4, 'adjacent': [4, 6], 'rent': 100},
        {'id': 6, 'area': 210, 'households': 7, 'adjacent': [5, 7], 'rent': 100},
        {'id': 7, 'area': 158, 'households': 4, 'adjacent': [6, 8], 'rent': 100},
        {'id': 8, 'area': 122, 'households': 3, 'adjacent': [7, 9], 'rent': 100},
        {'id': 9, 'area': 184, 'households': 2, 'adjacent': [8, 10], 'rent': 100},
        {'id': 10, 'area': 119, 'households': 4, 'adjacent': [9, 11], 'rent': 100},
        {'id': 11, 'area': 570, 'households': 11, 'adjacent': [10, 12], 'rent': 100},
        {'id': 12, 'area': 490, 'households': 4, 'adjacent': [11, 13], 'rent': 100},
        {'id': 13, 'area': 170, 'households': 4, 'adjacent': [12, 14], 'rent': 100},
        {'id': 14, 'area': 85, 'households': 2, 'adjacent': [13, 15], 'rent': 100},
        {'id': 15, 'area': 360, 'households': 7, 'adjacent': [14, 16], 'rent': 100},
        {'id': 16, 'area': 740, 'households': 8, 'adjacent': [15, 17], 'rent': 100},
        {'id': 17, 'area': 459, 'households': 6, 'adjacent': [16, 18], 'rent': 100},
        {'id': 18, 'area': 222, 'households': 5, 'adjacent': [17, 19], 'rent': 100},
        {'id': 19, 'area': 222, 'households': 6, 'adjacent': [18, 20], 'rent': 100},
        {'id': 20, 'area': 100, 'households': 5, 'adjacent': [19, 21], 'rent': 100},
        {'id': 21, 'area': 215, 'households': 5, 'adjacent': [20, 1], 'rent': 100}
    ]
    df = pd.DataFrame([
        {'id': c['id'], 'area': c['area'], 'households': c['households'],
         'adjacent': str(c['adjacent']), 'rent': c['rent']}
        for c in compounds_data
    ])
    os.makedirs('templates', exist_ok=True)
    df.to_csv('templates/compounds.csv', index=False)
    
    params = {
        'cost_per_household': 50000,
        'alpha': 50,
        'years': 10,
        'target_m': 20,
        'population_size': 100,
        'max_generations': 200
    }
    with open('templates/config.json', 'w') as f:
        json.dump(params, f, indent=4)