"""
Utility to load a grid-based maritime graph from a CSV file.

The CSV is expected to have the following header fields:

    from_x, from_y, to_x, to_y, depth_min, risk_index, wave_size, wind_speed

Each row describes a directed edge from `(from_x, from_y)` to `(to_x, to_y)`
with the associated attributes.

This module exposes a single function, `load_graph`, which returns a
dictionary-based adjacency structure suitable for pathfinding algorithms.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from typing import Dict, List, Tuple, Iterable
import math

@dataclass
class Edge:
    """Represents a directed edge in the graph with attributes."""
    to: Tuple[float, float]
    depth_min: float
    distance: float
    def attributes_list(self) -> List[float]:
        """Devuelve una lista con los atributos:
        depth_min, risk_index, wave_size, wind_speed, distance."""
        return [
            self.depth_min,
            self.distance,
        ]


def load_graph(csv_path: str) -> Dict[Tuple[int, int], List[Edge]]:
    """
    Load a graph from a CSV file into an adjacency dictionary.

    Parameters
    ----------
    csv_path : str
        Path to the CSV file containing edge definitions.

    Returns
    -------
    Dict[Tuple[int, int], List[Edge]]
        A dictionary mapping each node (x, y) to a list of outgoing edges.
    """
    adjacency: Dict[Tuple[float, float], List[Edge]] = {}

    # Open with utf-8-sig to tolerate an optional BOM and skip empty lines
    with open(csv_path, newline='', encoding='utf-8-sig') as csvfile:
        # Filter out empty/blank lines which can confuse DictReader's header detection
        filtered_lines = (line for line in csvfile if line.strip())
        reader = csv.DictReader(filtered_lines)

        # Basic validation of expected columns to provide a clearer error if missing
        expected = [
            'from_x', 'from_y', 'to_x', 'to_y','distance', 'depth_min'
        ]
        if reader.fieldnames is None:
            raise ValueError(f"No CSV header found in {csv_path}")
        fieldnames = [fn.strip() for fn in reader.fieldnames]
        missing = [f for f in expected if f not in fieldnames]
        if missing:
            raise KeyError(f"CSV is missing expected columns: {missing}. Found: {fieldnames}")

        for row in reader:
            # Convert fields to proper types, defensively handling extra whitespace
            try:
                from_x = int(row['from_x'].strip())
                from_y = int(row['from_y'].strip())
                to_x = int(row['to_x'].strip())
                to_y = int(row['to_y'].strip())

                depth_min = float(row['depth_min'].strip())
                distance = float(row['distance'].strip())

            except Exception as exc:
                raise ValueError(f"Error parsing CSV row {row}: {exc}") from exc

            from_node = (from_x, from_y)
            edge = Edge(
                to=(to_x, to_y),
                depth_min=depth_min,
                distance=distance,
            )
            adjacency.setdefault(from_node, []).append(edge)

    return adjacency


def print_graph_summary(graph: Dict[Tuple[float, float], List[Edge]]) -> None:
    """
    Print a brief summary of the graph structure.

    Parameters
    ----------
    graph : Dict[Tuple[int, int], List[Edge]]
        The adjacency dictionary representing the graph.
    """
    num_nodes = len(graph)
    num_edges = sum(len(edges) for edges in graph.values())
    print(f"Graph contains {num_nodes} nodes and {num_edges} directed edges.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Load and summarize a maritime graph.")
    parser.add_argument('csv_path', help="Path to the CSV file with edges")
    args = parser.parse_args()

    G = load_graph(args.csv_path)
    print_graph_summary(G)


