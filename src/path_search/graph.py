from typing import Optional, Any, Dict, Tuple, List
import csv

VertexKey = Tuple[float, float]

class Graph:
    """
    Graph class (dirigido). Usa (lat, lon) como clave de vértice y guarda 'depth' en metros (float).
    """
    def __init__(self, key_decimals: int = 6):
        self._graph: Dict[VertexKey, Dict[str, Any]] = {}
        self._dec = key_decimals  # redondeo para estabilidad de clave

    def _normalize_key(self, vertex: Tuple[float, float]) -> VertexKey:
        lat, lon = vertex
        return (round(float(lat), self._dec), round(float(lon), self._dec))

    def add_vertex(self, vertex: Tuple[float, float], depth: float) -> None:
        v = self._normalize_key(vertex)
        if v not in self._graph:
            self._graph[v] = {'depth': float(depth), 'neighbors': {}}

    def add_edge(self, vertex1: Tuple[float, float], vertex2: Tuple[float, float], data: Optional[Any]=None) -> None:
        v1 = self._normalize_key(vertex1)
        v2 = self._normalize_key(vertex2)
        if v1 not in self._graph:
            self.add_vertex(v1, 0.0)
        if v2 not in self._graph:
            self.add_vertex(v2, 0.0)
        self._graph[v1]['neighbors'][v2] = data

    def get_neighbors(self, vertex: Tuple[float, float]) -> List[VertexKey]:
        v = self._normalize_key(vertex)
        return list(self._graph.get(v, {}).get('neighbors', {}).keys())

    def get_vertex_depth(self, vertex: Tuple[float, float]) -> Optional[float]:
        v = self._normalize_key(vertex)
        return self._graph.get(v, {}).get('depth')

    def get_edge_data(self, vertex1: Tuple[float, float], vertex2: Tuple[float, float]) -> Optional[Any]:
        v1 = self._normalize_key(vertex1)
        v2 = self._normalize_key(vertex2)
        if self.edge_exists(v1, v2):
            return self._graph[v1]['neighbors'][v2]
        raise ValueError("The edge does not exist")

    def print_graph(self) -> None:
        for vertex, data in self._graph.items():
            print("Vertex:", vertex)
            print("Depth:", data.get('depth'))
            print("Neighbors:", list(data['neighbors'].keys()))
            print("")

    def vertex_exists(self, vertex: Tuple[float, float]) -> bool:
        v = self._normalize_key(vertex)
        return v in self._graph

    def edge_exists(self, vertex1: Tuple[float, float], vertex2: Tuple[float, float]) -> bool:
        v1 = self._normalize_key(vertex1)
        v2 = self._normalize_key(vertex2)
        return v1 in self._graph and v2 in self._graph[v1]['neighbors']

    def load_data(self, vertex_csv: str, edges_csv: str, skip_header: bool = True) -> None:
        # Nodos: columnas esperadas -> latitud, longitud, profundidad, ...
        with open(vertex_csv, newline='', encoding='utf-8') as vf:
            reader = csv.reader(vf)
            if skip_header:
                next(reader, None)
            for row in reader:
                if not row or len(row) < 3:
                    continue
                try:
                    lat = float(row[0])
                    lon = float(row[1])
                    depth = float(row[2]) if row[2] != "" else 0.0
                except ValueError:
                    # si la fila es inválida o es header residual, la salto
                    continue
                self.add_vertex((lat, lon), depth)

        # Aristas: columnas esperadas -> lat_origen, lon_origen, lat_destino, lon_destino, distancia_km (opcional)
        with open(edges_csv, newline='', encoding='utf-8') as ef:
            reader = csv.reader(ef)
            if skip_header:
                next(reader, None)
            for row in reader:
                if not row or len(row) < 4:
                    continue
                try:
                    lat1 = float(row[0]); lon1 = float(row[1])
                    lat2 = float(row[2]); lon2 = float(row[3])
                    dist = float(row[4]) if len(row) > 4 and row[4] != "" else None
                except ValueError:
                    continue
                self.add_edge((lat1, lon1), (lat2, lon2), {'distance': dist})
