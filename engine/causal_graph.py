"""
Causal graph module for AfricaForecast.

Builds a domain-informed DAG of African health indicator relationships
based on WHO SDG 3 linkage maps, Lancet Commission pathways, and
epidemiological transition theory.

Optionally refines the DAG using the PC causal-discovery algorithm
(causal-learn library). Falls back gracefully when causal-learn is absent.

DAG format (parent-list form):
  {child_id: [(parent_id, source, sign), ...]}
  - source: "domain" (hand-coded) or "data" (discovered)
  - sign: +1 (positive causal effect) or -1 (negative causal effect)

Adjacency form (for algorithms):
  {parent_id: {child_id: (source, sign)}}
"""

from __future__ import annotations

import json
from collections import deque
from typing import Dict, List, Tuple

from engine.config import INDICATOR_IDS

# Type aliases
DagType = Dict[str, List[Tuple[str, str, int]]]
AdjType = Dict[str, Dict[str, Tuple[str, int]]]


# ---------------------------------------------------------------------------
# 1. Domain DAG
# ---------------------------------------------------------------------------

def build_domain_dag() -> DagType:
    """
    Return a domain-coded DAG based on WHO SDG 3 linkage maps,
    Lancet Commission pathways, and epidemiological transition theory.

    Every edge (parent → child) is grounded in peer-reviewed evidence:
      - WHO SDG 3: https://www.who.int/data/gho/data/themes/topics/sdg-target-3
      - Lancet Countdown on Climate & Health
      - GBD/IHME risk factor pathways
      - Demographic transition / health transition literature

    Returns
    -------
    dict: {child_id: [(parent_id, "domain", sign), ...]}
    """
    # Build as a list of (parent, child, sign) triples, then pivot.
    # sign = +1: increasing parent increases child
    # sign = -1: increasing parent decreases child

    raw_edges: List[Tuple[str, str, int]] = [

        # ---- Economic drivers → health financing ----
        # Higher GDP per capita enables more health spending
        ("gdp_pc", "che_gdp",    +1),   # richer countries spend more % on health
        ("gdp_pc", "che_pc",     +1),   # GDP drives absolute health spending
        ("gdp_pc", "gghe",       +1),   # GDP → government health expenditure
        # Better governance → more govt health investment
        ("governance", "gghe",   +1),
        # Foreign aid supplements domestic spending (negative association — flows to poor)
        ("dah", "ext_he",        +1),   # higher aid → higher external health expenditure share

        # ---- Health financing → workforce & infrastructure ----
        # More health spending per capita → more physicians and nurses
        ("che_pc",   "physicians", +1),
        ("che_pc",   "nurses",     +1),
        ("che_pc",   "beds",       +1),
        ("che_pc",   "medicines",  +1),
        ("gghe",     "physicians", +1),
        # Education → health workforce pipeline
        ("schooling", "physicians", +1),
        # GDP drives education → workforce
        ("gdp_pc",   "schooling",  +1),

        # ---- Workforce → service coverage ----
        ("physicians", "uhc_index", +1),
        ("nurses",     "uhc_index", +1),
        ("physicians", "dtp3",      +1),   # stronger health system → better immunisation
        ("physicians", "sba",       +1),   # physician density → skilled birth attendance
        ("nurses",     "sba",       +1),
        # Financing also directly drives coverage
        ("che_pc",   "uhc_index",  +1),

        # ---- WASH → child & maternal outcomes ----
        # Clean water/sanitation reduce under-5 and neonatal mortality
        ("water",      "u5_mort",   -1),
        ("sanitation", "u5_mort",   -1),
        ("water",      "neo_mort",  -1),
        ("water",      "diarrhea_mort", -1),

        # ---- Coverage → mortality (child / maternal) ----
        ("dtp3",       "u5_mort",   -1),
        ("dtp3",       "lri_mort",  -1),   # immunisation reduces resp-infection mortality
        ("sba",        "mat_mort",  -1),
        ("sba",        "neo_mort",  -1),
        ("uhc_index",  "u5_mort",   -1),
        ("uhc_index",  "mat_mort",  -1),
        ("uhc_index",  "neo_mort",  -1),
        ("uhc_index",  "infant_mort", -1),

        # ---- Socioeconomic → child mortality ----
        ("gdp_pc",   "u5_mort",    -1),
        ("gdp_pc",   "neo_mort",   -1),
        ("gdp_pc",   "mat_mort",   -1),
        ("gdp_pc",   "infant_mort",-1),
        ("fem_edu",  "u5_mort",    -1),   # female education → child survival
        ("fem_edu",  "mat_mort",   -1),
        ("fem_edu",  "fertility",  -1),   # higher education → lower fertility

        # ---- Infectious disease: HIV ----
        # Education and wealth reduce HIV incidence
        ("schooling", "hiv_inc",   -1),
        ("gdp_pc",    "hiv_inc",   -1),
        ("uhc_index", "hiv_inc",   -1),
        # HIV incidence → HIV prevalence (lagged stock effect, same direction)
        ("hiv_inc",   "hiv_prev",  +1),

        # ---- Infectious disease: Malaria ----
        ("gdp_pc",    "mal_inc",   -1),
        ("uhc_index", "mal_inc",   -1),
        ("mal_inc",   "mal_mort",  +1),

        # ---- Infectious disease: TB ----
        ("gdp_pc",    "tb_inc",    -1),
        ("uhc_index", "tb_inc",    -1),
        ("tb_inc",    "tb_mort",   +1),

        # ---- NCD / epidemiological transition ----
        # Urban, obesity, tobacco → NCD burden
        ("urban",     "obesity",   +1),   # urban environments promote obesity
        ("urban",     "hypertension", +1),
        ("obesity",   "diabetes",  +1),
        ("obesity",   "hypertension", +1),
        ("tobacco",   "ncd_mort",  +1),
        ("tobacco",   "cancer_dalys", +1),
        ("hypertension", "cvd_dalys", +1),
        ("diabetes",  "cvd_dalys", +1),
        ("diabetes",  "ncd_mort",  +1),
        # GDP has a complex NCD relationship: more wealth → less tobacco use in Africa
        ("gdp_pc",    "tobacco",   -1),

        # ---- Financing → financial protection ----
        # More government health expenditure → less out-of-pocket burden
        ("gghe",    "oop_share",   -1),
        ("che_gdp", "oop_share",   -1),

        # ---- Aggregate outcome: life expectancy ----
        ("u5_mort",   "life_exp",  -1),
        ("adult_mort","life_exp",  -1),
        ("ncd_mort",  "life_exp",  -1),
        ("hiv_prev",  "life_exp",  -1),
        ("gdp_pc",    "life_exp",  +1),
        ("uhc_index", "life_exp",  +1),

        # ---- Aggregate outcome: HALE (healthy life expectancy) ----
        # HALE is downstream of life_exp + disease burden
        ("life_exp",  "hale",      +1),
        ("dalys_all", "hale",      -1),

        # ---- All-cause DALYs ----
        ("u5_mort",      "dalys_all",  +1),
        ("ncd_mort",     "dalys_all",  +1),
        ("mal_mort",     "dalys_all",  +1),
        ("lri_mort",     "dalys_all",  +1),
        ("mental_dalys", "dalys_all",  +1),
        ("cvd_dalys",    "dalys_all",  +1),
        ("cancer_dalys", "dalys_all",  +1),

        # ---- Crude death rate / adult mortality ----
        ("u5_mort",    "crude_death", +1),
        ("adult_mort", "crude_death", +1),
        ("ncd_mort",   "adult_mort",  +1),
        ("hiv_prev",   "adult_mort",  +1),

        # ---- Conflict / fragility → health system degradation ----
        ("conflict",  "uhc_index",   -1),
        ("fragility", "gghe",        -1),
    ]

    # Validate all nodes are valid indicator IDs
    valid = set(INDICATOR_IDS)
    bad = [(p, c) for p, c, _ in raw_edges if p not in valid or c not in valid]
    if bad:
        raise ValueError(f"Invalid indicator IDs in domain DAG edges: {bad}")

    # Pivot to child-keyed parent list
    dag: DagType = {}
    seen: set = set()
    for parent, child, sign in raw_edges:
        key = (parent, child)
        if key in seen:
            continue  # deduplicate
        seen.add(key)
        dag.setdefault(child, []).append((parent, "domain", sign))

    return dag


# ---------------------------------------------------------------------------
# 2. Conversion utilities
# ---------------------------------------------------------------------------

def dag_to_adjacency(dag: DagType) -> AdjType:
    """
    Convert parent-list DAG to adjacency form.

    Parameters
    ----------
    dag : {child: [(parent, source, sign), ...]}

    Returns
    -------
    adj : {parent: {child: (source, sign)}}
    """
    adj: AdjType = {}
    for child, parents in dag.items():
        for parent, source, sign in parents:
            adj.setdefault(parent, {})[child] = (source, sign)
    return adj


def adjacency_to_dag(adj: AdjType) -> DagType:
    """
    Convert adjacency form back to parent-list DAG.

    Parameters
    ----------
    adj : {parent: {child: (source, sign)}}

    Returns
    -------
    dag : {child: [(parent, source, sign), ...]}
    """
    dag: DagType = {}
    for parent, children in adj.items():
        for child, (source, sign) in children.items():
            dag.setdefault(child, []).append((parent, source, sign))
    return dag


# ---------------------------------------------------------------------------
# 3. Graph algorithms
# ---------------------------------------------------------------------------

def _collect_all_nodes(dag: DagType) -> set:
    """Return set of all node IDs (children + parents) in DAG."""
    nodes: set = set()
    for child, parents in dag.items():
        nodes.add(child)
        for parent, _, _ in parents:
            nodes.add(parent)
    return nodes


def is_acyclic(adj: AdjType) -> bool:
    """
    Test whether the directed graph (in adjacency form) is acyclic.

    Uses Kahn's algorithm (topological sort via in-degree reduction).

    Parameters
    ----------
    adj : {parent: {child: (source, sign)}}

    Returns
    -------
    bool: True if acyclic (DAG), False if cycle detected.
    """
    # Build in-degree map and collect all nodes
    all_nodes: set = set(adj.keys())
    for children in adj.values():
        all_nodes.update(children.keys())

    in_deg: Dict[str, int] = {n: 0 for n in all_nodes}
    for parent in adj:
        for child in adj[parent]:
            in_deg[child] = in_deg.get(child, 0) + 1

    queue = deque(n for n in all_nodes if in_deg[n] == 0)
    visited = 0
    while queue:
        node = queue.popleft()
        visited += 1
        for child in adj.get(node, {}):
            in_deg[child] -= 1
            if in_deg[child] == 0:
                queue.append(child)

    return visited == len(all_nodes)


def topological_sort(dag: DagType) -> List[str]:
    """
    Return nodes in topological order (parents before children).

    Deterministic: ties broken by alphabetical order.
    Includes all nodes — children and any parents not listed as children.

    Parameters
    ----------
    dag : {child: [(parent, source, sign), ...]}

    Returns
    -------
    List[str]: nodes in topological order
    """
    # Collect all nodes
    all_nodes = _collect_all_nodes(dag)

    # Build in-degree map using DAG edges
    in_deg: Dict[str, int] = {n: 0 for n in all_nodes}
    children_of: Dict[str, List[str]] = {n: [] for n in all_nodes}

    for child, parents in dag.items():
        for parent, _, _ in parents:
            in_deg[child] = in_deg.get(child, 0) + 1
            children_of.setdefault(parent, []).append(child)

    # Use a sorted list as a deterministic priority queue
    ready = sorted(n for n in all_nodes if in_deg[n] == 0)
    order: List[str] = []

    while ready:
        node = ready.pop(0)
        order.append(node)
        # Release children; insert into sorted position
        newly_ready = []
        for child in children_of.get(node, []):
            in_deg[child] -= 1
            if in_deg[child] == 0:
                newly_ready.append(child)
        if newly_ready:
            ready = sorted(ready + newly_ready)

    if len(order) != len(all_nodes):
        raise ValueError("Graph contains a cycle; topological sort is undefined.")

    return order


def get_parents(dag: DagType, node: str) -> List[str]:
    """
    Return list of parent IDs for the given node.

    Parameters
    ----------
    dag   : parent-list DAG
    node  : child node ID to query

    Returns
    -------
    List[str]: parent IDs (empty list if node has no parents or is not in DAG)
    """
    return [parent for parent, _, _ in dag.get(node, [])]


def get_children(dag: DagType, node: str) -> List[str]:
    """
    Return list of child IDs for the given node.

    Parameters
    ----------
    dag   : parent-list DAG
    node  : parent node ID to query

    Returns
    -------
    List[str]: child IDs (empty list if node has no children)
    """
    children = []
    for child, parents in dag.items():
        for parent, _, _ in parents:
            if parent == node:
                children.append(child)
                break
    return children


# ---------------------------------------------------------------------------
# 4. Causal discovery refinement
# ---------------------------------------------------------------------------

def refine_with_discovery(
    dag: DagType,
    panel,
    indicator_ids: List[str],
    alpha: float = 0.05,
) -> DagType:
    """
    Optionally refine the domain DAG with data-driven causal discovery.

    Attempts to import `causal_learn` and run the PC algorithm on the
    provided panel data. Falls back to domain-only DAG if causal_learn
    is unavailable or the panel is too small.

    Rules:
    - All domain edges are preserved unchanged.
    - Data edges are added only where PC agrees at FDR < alpha.
    - If the merged DAG would contain a cycle, all data edges are dropped.

    Parameters
    ----------
    dag           : domain DAG {child: [(parent, source, sign), ...]}
    panel         : pd.DataFrame with columns = indicator_ids (plus 'iso3', 'year')
    indicator_ids : list of indicator column names to use
    alpha         : significance threshold for PC edge retention

    Returns
    -------
    DagType: refined DAG (same structure, edges tagged "domain" or "data")
    """
    import copy
    refined = copy.deepcopy(dag)

    try:
        from causal_learn.search.ConstraintBased.PC import pc  # type: ignore
        from causal_learn.utils.cit import fisherz  # type: ignore
        import numpy as np

        # Extract numeric matrix; drop rows with any NaN in the indicator columns
        avail = [c for c in indicator_ids if c in panel.columns]
        if len(avail) < 3:
            return refined  # too few variables for PC

        data_mat = panel[avail].dropna().values.astype(float)
        if data_mat.shape[0] < 30:
            return refined  # too few observations

        # Run PC
        cg = pc(data_mat, alpha=alpha, indep_test=fisherz)
        # cg.G.graph is a (d x d) matrix: 1 means i→j, -1 means i—j (undirected)
        G = cg.G.graph  # numpy array shape (d, d)
        d = len(avail)
        data_edges: List[Tuple[str, str, int]] = []
        for i in range(d):
            for j in range(d):
                if G[i, j] == 1 and G[j, i] == -1:
                    # Directed edge i → j
                    parent_id = avail[i]
                    child_id = avail[j]
                    # Determine sign from data correlation direction
                    corr = float(np.corrcoef(data_mat[:, i], data_mat[:, j])[0, 1])
                    sign = 1 if corr >= 0 else -1
                    data_edges.append((parent_id, child_id, sign))

        # Add data edges that don't duplicate domain edges
        domain_pairs: set = set()
        for child, parents in dag.items():
            for parent, _, _ in parents:
                domain_pairs.add((parent, child))

        candidate_refined = copy.deepcopy(dag)
        added = []
        for parent, child, sign in data_edges:
            if (parent, child) not in domain_pairs:
                candidate_refined.setdefault(child, []).append(
                    (parent, "data", sign)
                )
                added.append((parent, child, sign))

        # Check acyclicity; if broken, discard all data additions
        if added:
            adj_candidate = dag_to_adjacency(candidate_refined)
            if is_acyclic(adj_candidate):
                refined = candidate_refined
            # else: keep domain-only refined (already a deep copy)

    except (ImportError, Exception):
        # causal_learn not installed, or runtime error → domain-only DAG
        pass

    return refined


# ---------------------------------------------------------------------------
# 5. Persistence
# ---------------------------------------------------------------------------

def save_dag(dag: DagType, filepath: str) -> None:
    """
    Serialise the DAG to a JSON file.

    Format: {child: [[parent, source, sign], ...]}

    Parameters
    ----------
    dag      : parent-list DAG to save
    filepath : destination file path
    """
    # Convert tuples to lists for JSON serialisation
    serialisable = {
        child: [[p, s, sgn] for p, s, sgn in parents]
        for child, parents in dag.items()
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(serialisable, f, indent=2, sort_keys=True)


def load_dag(filepath: str) -> DagType:
    """
    Load a DAG previously saved by ``save_dag``.

    Parameters
    ----------
    filepath : path to JSON file

    Returns
    -------
    DagType: parent-list DAG with tuples restored
    """
    with open(filepath, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return {
        child: [(p, s, int(sgn)) for p, s, sgn in parents]
        for child, parents in raw.items()
    }
