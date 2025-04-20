from pymoo.config import Config

Config.warnings['not_compiled'] = False

import numpy as np
import time
import traceback
import ast
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize


# Built-in union_find to avoid utils.py dependency
def union_find(vacated_ids, compounds):
    """Simple union-find to count connected components."""
    try:
        if not vacated_ids:
            return 0
        parent = {v: v for v in vacated_ids}

        def find(u):
            if parent[u] != u:
                parent[u] = find(parent[u])
            return parent[u]

        id_to_index = {c['id']: i for i, c in enumerate(compounds)}
        for i in vacated_ids:
            for adj in compounds[id_to_index[i]]['adjacent']:
                if adj in vacated_ids:
                    pu = find(i)
                    pv = find(adj)
                    if pu != pv:
                        parent[pv] = pu

        return len(set(find(cid) for cid in vacated_ids))
    except Exception as e:
        print(f"Error in union_find: {e}")
        raise


class UrbanRenewalProblem(ElementwiseProblem):
    def __init__(self, compounds, params):
        self.compounds = compounds
        self.params = params
        self.id_to_index = {c['id']: i for i, c in enumerate(compounds)}  # Cache ID to index
        super().__init__(
            n_var=len(compounds),
            n_obj=3,
            n_ieq_constr=len(compounds),
            n_eq_constr=1,
            xl=np.zeros(len(compounds)),
            xu=np.ones(len(compounds)),
            vtype=int
        )

    def _evaluate(self, x, out, *args, **kwargs):
        try:
            # Objectives
            total_vacated = np.sum(x)
            total_cost = np.sum(
                x * np.array([c['households'] * self.params['cost_per_household'] for c in self.compounds]))
            total_rent_gain = np.sum(
                x * np.array([c['area'] * (c['alpha'] - 1) * c['rent'] * self.params['years'] for c in self.compounds]))
            m = total_rent_gain / total_cost if total_cost > 1e-6 else 0
            m = min(m, 1e6)  # Limit m to prevent overflow

            out["F"] = [-total_vacated, total_cost, -m]

            # Inequality constraints: x_i <= sum(x_j for j in adjacent)
            c = np.zeros(len(self.compounds))
            for i in range(len(self.compounds)):
                if x[i]:
                    try:
                        adj_indices = [self.id_to_index[adj] for adj in self.compounds[i]['adjacent']]
                        c[i] = x[i] - np.sum(x[adj_indices])
                    except KeyError as e:
                        raise ValueError(f"Invalid adjacent ID: {e}")

            # Equality constraint: single contiguous zone
            vacated = [c['id'] for i, c in enumerate(self.compounds) if x[i]]
            zones = union_find(vacated, self.compounds) if vacated else 0
            ceq = zones - 1 if vacated else 0

            out["G"] = c
            out["H"] = [ceq]
        except Exception as e:
            print(f"Error in _evaluate: {e}")
            raise


def compute_cluster_groups(vacated_ids, compounds, id_to_index):
    start_time = time.time()
    try:
        parent = {v: v for v in vacated_ids}

        def find(u):
            if parent[u] != u:
                parent[u] = find(parent[u])
            return parent[u]

        for i in vacated_ids:
            try:
                for adj in compounds[id_to_index[i]]['adjacent']:
                    if adj in vacated_ids:
                        pu = find(i)
                        pv = find(adj)
                        if pu != pv:
                            parent[pv] = pu
            except KeyError as e:
                raise ValueError(f"Invalid adjacent ID in cluster groups: {e}")

        cluster_groups = {}
        for cid in vacated_ids:
            root = find(cid)
            if root not in cluster_groups:
                cluster_groups[root] = []
            cluster_groups[root].append(cid)

        print(f"Cluster groups time: {time.time() - start_time:.2f} seconds")
        return cluster_groups
    except Exception as e:
        print(f"Error in compute_cluster_groups: {e}")
        raise


def compute_problem_three(compounds, params):
    """Run NSGA-II and find inflection point."""
    start_time = time.time()

    # Validate compounds data
    try:
        print(f"Validating compounds: {compounds[:2]}")  # Log first two compounds
        for c in compounds:
            if isinstance(c['adjacent'], str):
                try:
                    c['adjacent'] = ast.literal_eval(c['adjacent'])
                except Exception as e:
                    raise ValueError(f"Failed to parse adjacent for compound {c['id']}: {c['adjacent']}, error: {e}")
            if not isinstance(c['adjacent'], list):
                raise ValueError(f"Invalid adjacent format for compound {c['id']}: {c['adjacent']}")
            for adj in c['adjacent']:
                if adj not in [comp['id'] for comp in compounds]:
                    raise ValueError(f"Invalid adjacent ID {adj} in compound {c['id']}")
    except Exception as e:
        print(f"Data validation error: {e}")
        raise

    try:
        print(f"Params: {params}")  # Log parameters
        problem = UrbanRenewalProblem(compounds, params)
        algorithm = NSGA2(pop_size=params.get('population_size', 20))  # Reduced to 20
        res = minimize(
            problem,
            algorithm,
            ('n_gen', params.get('max_generations', 50)),  # Reduced to 50
            seed=1,
            verbose=True
        )

        print(f"NSGA-II time: {time.time() - start_time:.2f} seconds")

        if res.X is None:
            raise ValueError("No feasible solutions found. Check constraints or parameters.")

        start_time = time.time()
        X = res.X
        F = res.F

        # Precompute arrays for efficiency
        households_arr = np.array([c['households'] for c in compounds])
        area_arr = np.array([c['area'] for c in compounds])
        rent_arr = np.array([c['rent'] for c in compounds])
        alpha_arr = np.array([c['alpha'] for c in compounds])

        # Vectorized computation of households and cost-effectiveness
        households = np.sum(X * households_arr, axis=1)
        cost_effectiveness = np.where(F[:, 1] > 1e-6, -F[:, 2], 0)

        print(f"Households and cost-effectiveness time: {time.time() - start_time:.2f} seconds")

        start_time = time.time()
        # Sort by households
        sort_idx = np.argsort(households)
        households_sorted = households[sort_idx]
        solutions_sorted = X[sort_idx]
        m_sorted = cost_effectiveness[sort_idx]

        # Find inflection point with numerical stability
        valid_idx = np.where((m_sorted >= params.get('target_m', 20)) & (m_sorted < 1e6))[0]
        if valid_idx.size > 0:
            inflection_idx = valid_idx[np.argmax(m_sorted[valid_idx])]
            max_m = m_sorted[inflection_idx]
        else:
            inflection_idx = np.argmax(m_sorted)
            max_m = m_sorted[inflection_idx]

        best_solution = solutions_sorted[inflection_idx]
        best_households = households_sorted[inflection_idx]

        print(f"Inflection point time: {time.time() - start_time:.2f} seconds")

        start_time = time.time()
        # Economic metrics (vectorized)
        total_cost = np.sum(best_solution * households_arr * params['cost_per_household'])
        total_area = np.sum(best_solution * area_arr)
        total_rent_gain = np.sum(best_solution * area_arr * (alpha_arr - 1) * rent_arr * params['years'])
        total_income = np.sum(best_solution * area_arr * alpha_arr * rent_arr * params['years'])
        profit = total_income - total_cost

        # Compute cluster groups with cached index
        vacated_ids = [c['id'] for i, c in enumerate(compounds) if best_solution[i]]
        id_to_index = {c['id']: i for i, c in enumerate(compounds)}
        cluster_groups = compute_cluster_groups(vacated_ids, compounds, id_to_index)

        print(f"Economic metrics time: {time.time() - start_time:.2f} seconds")

        results = {
            'm': max_m,
            'vacated_compounds': int(np.sum(best_solution)),
            'households': int(best_households),
            'cost': total_cost,
            'area': total_area,
            'income': total_income,
            'profit': profit,
            'vacated_ids': vacated_ids,
            'cluster_groups': cluster_groups
        }

        print(f"Results: {results}")
        return best_solution, results, F
    except Exception as e:
        print(f"Error in compute_problem_three: {e}")
        traceback.print_exc()
        raise