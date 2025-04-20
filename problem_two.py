import pandas as pd
import numpy as np


def compute_problem_two(compounds, params):
    """Compute marginal cost-effectiveness and feasible sequence."""
    # Validate inputs
    if not compounds or not params:
        raise ValueError("Compounds or params cannot be empty")

    # Compute marginal cost-effectiveness (rho)
    rho = []
    for c in compounds:
        if not all(key in c for key in ['area', 'households', 'rent', 'alpha', 'id', 'adjacent']):
            raise KeyError(f"Missing required keys in compound {c.get('id', 'unknown')}")
        if not isinstance(c['adjacent'], list):
            raise ValueError(f"Adjacent must be a list in compound {c['id']}")
        rho_i = (params['years'] * c['area'] * (c['alpha'] - 1) * c['rent']) / \
                (c['households'] * params['cost_per_household'])
        rho.append(rho_i)

    # Create sorted table
    df = pd.DataFrame({
        'id': [c['id'] for c in compounds],
        'area': [c['area'] for c in compounds],
        'households': [c['households'] for c in compounds],
        'rho': rho
    })
    sorted_df = df.sort_values(by='rho', ascending=False).reset_index(drop=True)

    # Generate feasible sequence
    idx = sorted_df.index.to_list()
    feasible_sequence = []
    vacated = np.zeros(len(compounds), dtype=bool)
    id_to_index = {c['id']: i for i, c in enumerate(compounds)}  # Map ID to index

    for i in idx:
        c = compounds[i]
        # Check if any adjacent compound is vacated
        has_vacated_neighbor = False
        for adj_id in c['adjacent']:
            if adj_id not in id_to_index:
                print(f"Warning: Invalid adjacent ID {adj_id} in compound {c['id']}")
                continue
            adj_index = id_to_index[adj_id]
            if vacated[adj_index]:
                has_vacated_neighbor = True
                break
        if not feasible_sequence or has_vacated_neighbor:
            feasible_sequence.append(c['id'])
            vacated[i] = True

    return sorted_df, feasible_sequence