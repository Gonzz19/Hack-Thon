import heapq
import math
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple
from graph import Graph
from heurísticas import h_safe, h_fuel, h_time, h_combined, h_distance
from costs import cost_fuel,cost_safe,cost_time, combined_cost, cost_distance

Node = Any
NeighborsFn = Callable[[Node], Iterable[Node]]
CostFn = Callable[[Node, Node], float]        # cost_fn(from_node, to_node)
HeuristicFn = Callable[[Node, Node], float]   # h_fn(node, goal)
MinDepthFn = Callable[[Node], float]          # profundidad_minima(node) -> profundidad
Graph = Graph
def min_depth_fn(node: Node, graph) -> float:
    return graph.get_vertex_depth(node) or 0.0



def a_star(
    start: Node,
    goal: Node,
    neighbors_fn: NeighborsFn,
    cost_fn: CostFn,
    h_fn: HeuristicFn,
    graph,
    min_depth_fn: Optional[MinDepthFn] = None,
    ship_draft: Optional[float] = None,
) -> Optional[List[Node]]:
    """
    Implementación A* genérica.

    Parámetros:
    - start: nodo inicial
    - goal: nodo objetivo
    - neighbors_fn: función que dado un nodo devuelve sus vecinos (iterable)
    - cost_fn: función que devuelve el coste de mover de un nodo a otro
    - h_fn: función heurística h(n, goal)
    - min_depth_fn: (opcional) función que devuelve la profundidad mínima en un nodo
    - ship_draft: (opcional) calado del buque; si se proporciona, se usa para filtrar vecinos
                   cuyo profundidad_minima(n) < ship_draft

    Retorna:
    - lista con el camino desde start hasta goal (inclusive) si se encuentra,
      o None si no hay camino.
    """

    # Estructuras de coste y padres
    g: Dict[Node, float] = {}   # coste conocido más barato desde start hasta nodo
    f: Dict[Node, float] = {}   # g + h estimado
    parent: Dict[Node, Optional[Node]] = {}

    def reconstruct_path(p: Dict[Node, Optional[Node]], node: Node) -> List[Node]:
        path: List[Node] = []
        cur = node
        while cur is not None:
            path.append(cur)
            cur = p.get(cur)
        path.reverse()
        return path

    # Inicialización
    g[start] = 0.0
    f[start] = h_fn(start, goal)
    parent[start] = None

    open_heap: List[Tuple[float, Node]] = []
    heapq.heappush(open_heap, (f[start], start))
    visited: set = set()

    while open_heap:
        current_f, current = heapq.heappop(open_heap)

        # Si este elemento es obsoleto (coste distinto del almacenado), saltarlo
        if current in visited:
            continue

        # Si alcanzamos el objetivo, reconstruir camino
        if current == goal:
            return reconstruct_path(parent, goal)

        # Marcar current como visitado
        visited.add(current)

        # Explorar vecinos
        for m in neighbors_fn(current):
            # Filtrado por profundidad mínima (calado)
            if min_depth_fn is not None and ship_draft is not None:
                if min_depth_fn(m, graph) < ship_draft:
                    continue
            e = graph.get_edge_data(current, m)
            if e is None:
                continue
            tentative_g = g.get(current, math.inf) + cost_fn(e)

            if tentative_g < g.get(m, math.inf):
                parent[m] = current
                g[m] = tentative_g
                f[m] = tentative_g + h_fn(m, goal)
                # Añadir/actualizar en open set (permitimos duplicados y los ignoramos al extraer)
                heapq.heappush(open_heap, (f[m], m))

    # Si se vacía open_set sin encontrar goal -> fracaso
    return None


g = Graph()
g.load_data('src/data/asia_india_norte_nodes.csv','src/data/asia_india_norte_edges.csv')
print(g.get_neighbors((5.435416666666669,73.18958333333332)))
# csv_path = 'graph_edges.csv'
# graph = load_graph(csv_path)

start = (5.435416666666669,73.18958333333332)
goal = (5.497916666666669,73.18958333333332)
path = a_star(start=start,
              goal=goal,
              neighbors_fn=g.get_neighbors,
              cost_fn=cost_distance,
              graph=g,
              h_fn=h_distance,
              min_depth_fn=None,
              ship_draft=None
          )

