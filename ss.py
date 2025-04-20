def union_find(vacated, compounds):
    """Union-find to check number of contiguous zones."""
    parent = {v: v for v in vacated}
    id_to_index = {c['id']: i for i, c in enumerate(compounds)}

    def find(u):
        if parent[u] != u:
            parent[u] = find(parent[u])
        return parent[u]

    for i in vacated:
        c = compounds[id_to_index[i]]
        for adj in c['adjacent']:
            if adj in vacated:
                pu = find(i)
                pv = find(adj)
                if pu != pv:
                    parent[pv] = pu

    roots = {find(u) for u in vacated}
    return len(roots)