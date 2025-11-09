
import math
  

def cost_distance(edge):
    """
    calcula el costo de la distancia
    distancian
    Returns:
        float: coste estimado de distancia
    """

    dist = edge['distance']
    return dist 



def cost_fuel(edge,w_wind,w_waves):
    """
    calcula el costo del combustible
    distancian
    w_wind: peso del viento 
    w_waves: peso de las olas (float)
    dist: distancia recorrida (float)
    Returns:
        float: coste estimado de combustible
    """

    edge_atr = edge.attributes_list()
    dist = edge_atr[4]
    wind_sp = edge_atr[3]
    wave_size = edge_atr[2]
    return  dist*((1+w_wind)*wind_sp+ w_waves*wave_size)


def cost_safe(
    edge,
    w_risk: float = 1.0,
    w_wind: float = 1.0,
    w_waves: float = 1.0,
) -> float:
    """
    Calcula un coste asociado a la seguridad combinando riesgo, viento y olas.

    Parámetros:
    - risk: valor de riesgo en la posición (float)
    - wind_sp: intensidad del viento (float)
    - wave_size: tamaño de las olas (float)
    - w_risk: peso para el término de riesgo (float, por defecto 1.0)
    - w_wind: peso para el término de viento (float, por defecto 1.0)
    - w_waves: peso para el término de olas (float, por defecto 1.0)

    Retorna:
    - coste de seguridad combinado (float)
    """

    edge_atr = edge.attributes_list()
    risk = edge_atr[1]
    wind_sp = edge_atr[3]
    wave_size = edge_atr[2]
    return w_risk * risk + w_wind * wind_sp + w_waves * wave_size

def cost_time(
    edge,
    wind_sp: float,
    wind_factor: float = 0.0,
    nominal_sp: float = 1.0, # a cambiar por velocidad nominal
) -> float:
    """
    Calcula el tiempo estimado para recorrer una distancia teniendo en cuenta
    la velocidad nominal y el efecto del viento.

    Parámetros:
    - dist: distancia recorrida (float)
    - nominal_sp: velocidad nominal (float)
    - wind_sp: intensidad del viento (float) (normalizada o en la misma escala que wind_factor)
    - wind_factor: factor que reduce la velocidad por efecto del viento (float, por defecto 0.0)

    Retorna:
    - tiempo estimado (float) o math.inf si la velocidad efectiva es cero o negativa
    """
    edge_atr = edge.attributes_list()
    wind_sp = edge_atr[3]
    dist = edge_atr[4]

    effective_speed = nominal_sp * (1.0 - wind_factor * wind_sp)
    if effective_speed <= 0.0:
        return math.inf
    return dist / effective_speed

def combined_cost( 
    edge,
    w_fuel: float = 1.0,
    w_time: float = 1.0,
    w_safe: float = 1.0,
    wind_factor: float = 0.0,
    nominal_sp: float = 1.0,
) -> float:
    """
    Calcula un coste combinado ponderado de combustible, tiempo y seguridad.

    Parámetros:
    - w_fuel: peso del coste de combustible (float, por defecto 1.0)
    - w_time: peso del coste de tiempo (float, por defecto 1.0)
    - w_safe: peso del coste de seguridad (float, por defecto 1.0)
    - wind_factor: factor que reduce la velocidad por efecto del viento (float, por defecto 0.0)
    - nominal_sp: velocidad nominal (float)

    Retorna:
    - coste combinado ponderado (float)
    """

    fuel_cost = cost_fuel(edge, w_wind=1.0, w_waves=1.0)
    time_cost = cost_time(edge, wind_sp=edge.attributes_list()[3], wind_factor=wind_factor, nominal_sp=nominal_sp)
    safe_cost = cost_safe(edge, w_risk=1.0, w_wind=1.0, w_waves=1.0)

    return w_fuel * fuel_cost + w_time * time_cost + w_safe * safe_cost