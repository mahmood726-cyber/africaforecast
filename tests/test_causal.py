"""Tests for causal graph module: domain DAG, graph operations, discovery, persistence."""

import json
import pytest

from engine.causal_graph import (
    build_domain_dag,
    dag_to_adjacency,
    adjacency_to_dag,
    topological_sort,
    is_acyclic,
    get_parents,
    get_children,
    refine_with_discovery,
    save_dag,
    load_dag,
)
from engine.config import INDICATOR_IDS


class TestDomainDag:
    """Tests for the hand-coded domain DAG built from epidemiological theory."""

    @pytest.fixture(autouse=True)
    def dag(self):
        self._dag = build_domain_dag()
        return self._dag

    def test_returns_dict_of_edges(self):
        """build_domain_dag returns a non-empty dict with list values."""
        assert isinstance(self._dag, dict)
        assert len(self._dag) > 0
        for child, parents in self._dag.items():
            assert isinstance(parents, list), f"{child} parents is not a list"
            for edge in parents:
                assert len(edge) == 3, f"Edge {edge} must have (parent, source, sign)"

    def test_edges_have_required_fields(self):
        """Every edge tuple must be (str, str, int) with sign in {-1, 1}."""
        for child, parents in self._dag.items():
            for parent, source, sign in parents:
                assert isinstance(parent, str), f"parent must be str, got {type(parent)}"
                assert isinstance(source, str), f"source must be str, got {type(source)}"
                assert sign in (-1, 1), f"sign must be -1 or 1, got {sign}"

    def test_dag_is_acyclic(self):
        """The domain DAG must have no cycles (required for topological sort)."""
        adj = dag_to_adjacency(self._dag)
        assert is_acyclic(adj), "Domain DAG contains a cycle"

    def test_edge_count_in_range(self):
        """Total edge count should be between 30 and 80 (domain-informed but not over-connected)."""
        total_edges = sum(len(parents) for parents in self._dag.values())
        assert 30 <= total_edges <= 80, (
            f"Edge count {total_edges} out of expected range [30, 80]"
        )

    def test_all_nodes_are_valid_indicators(self):
        """Every node (child or parent) must be a valid indicator ID from config."""
        valid = set(INDICATOR_IDS)
        for child, parents in self._dag.items():
            assert child in valid, f"Child node '{child}' not in INDICATOR_IDS"
            for parent, source, sign in parents:
                assert parent in valid, f"Parent node '{parent}' not in INDICATOR_IDS"


class TestGraphOperations:
    """Tests for adjacency conversion, topological sort, parents/children lookups."""

    @pytest.fixture(autouse=True)
    def setup(self, mini_dag):
        self._dag = mini_dag
        self._adj = dag_to_adjacency(mini_dag)

    def test_adjacency_roundtrip(self):
        """dag -> adjacency -> dag must reproduce the original edge set."""
        dag_rt = adjacency_to_dag(self._adj)
        # Collect all edges (child, parent, source, sign) from original
        original_edges = set()
        for child, parents in self._dag.items():
            for parent, source, sign in parents:
                original_edges.add((child, parent, source, sign))

        # Collect from roundtripped dag
        rt_edges = set()
        for child, parents in dag_rt.items():
            for parent, source, sign in parents:
                rt_edges.add((child, parent, source, sign))

        assert original_edges == rt_edges

    def test_topological_sort_respects_order(self):
        """In topological order, every parent must appear before its child."""
        order = topological_sort(self._dag)
        pos = {node: i for i, node in enumerate(order)}

        for child, parents in self._dag.items():
            if child not in pos:
                continue
            for parent, source, sign in parents:
                if parent not in pos:
                    continue
                assert pos[parent] < pos[child], (
                    f"Parent '{parent}' appears after child '{child}' in topo sort"
                )

    def test_get_parents(self):
        """get_parents returns only the parent IDs (not source/sign)."""
        parents = get_parents(self._dag, "u5_mort")
        assert set(parents) == {"gdp_pc", "physicians"}

    def test_get_children(self):
        """get_children returns all nodes that have the queried node as a parent."""
        # gdp_pc is a parent of u5_mort, life_exp, hiv_inc, mal_mort, physicians, uhc_index
        children = get_children(self._dag, "gdp_pc")
        assert "u5_mort" in children
        assert "life_exp" in children
        assert "hiv_inc" in children
        # gdp_pc is not a child of anything in mini_dag
        parents_of_gdp = get_parents(self._dag, "gdp_pc")
        assert parents_of_gdp == []


class TestCausalDiscovery:
    """Tests for refine_with_discovery (PC algorithm or graceful fallback)."""

    def test_refine_returns_dag_with_provenance(self, mini_dag, synthetic_panel, mini_indicators):
        """refine_with_discovery must return a dict with the correct structure."""
        result = refine_with_discovery(mini_dag, synthetic_panel, mini_indicators)
        assert isinstance(result, dict)
        # Every edge source must be "domain" or "data"
        for child, parents in result.items():
            for parent, source, sign in parents:
                assert source in ("domain", "data"), (
                    f"Unknown edge source '{source}' for ({parent} -> {child})"
                )

    def test_refined_dag_is_acyclic(self, mini_dag, synthetic_panel, mini_indicators):
        """After refinement the DAG must remain acyclic."""
        result = refine_with_discovery(mini_dag, synthetic_panel, mini_indicators)
        adj = dag_to_adjacency(result)
        assert is_acyclic(adj), "Refined DAG contains a cycle"


class TestDagPersistence:
    """Tests for JSON save/load of the DAG."""

    def test_save_load_roundtrip(self, mini_dag, tmp_path):
        """Saving and loading a DAG must reproduce the exact same structure."""
        fpath = str(tmp_path / "dag.json")
        save_dag(mini_dag, fpath)

        # File must exist and be valid JSON
        with open(fpath, "r") as f:
            raw = json.load(f)
        assert isinstance(raw, dict)

        # Loaded DAG must equal original
        loaded = load_dag(fpath)
        assert loaded == mini_dag
