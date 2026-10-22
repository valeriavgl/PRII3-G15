def get_initial_moves():
    posicionar = [
        # Giro 3.14 rad (3.14 / 0.5 = 6.28s)
        {"lineal": 0.0, "angular": 0.5, "duracion": 6.28, "levantar_lapiz": True}, 
        # Avance 2.75 m (2.75 / 0.2 = 13.75s)
        {"lineal": 0.2, "angular": 0.0, "duracion": 13.75, "levantar_lapiz": True},
        # Giro -1.57 rad
        {"lineal": 0.0, "angular": -0.5, "duracion": 3.14, "levantar_lapiz": True}, 
        # Avance 2.25 m
        {"lineal": 0.2, "angular": 0.0, "duracion": 11.25, "levantar_lapiz": True},
        # Giro -0.785 rad
        {"lineal": 0.0, "angular": -0.5, "duracion": 1.57, "levantar_lapiz": True},
        # Avance 0.25 m
        {"lineal": 0.2, "angular": 0.0, "duracion": 1.25, "levantar_lapiz": True},
    ]
    return posicionar

def get_moves_for_one():
    dibujar_1 = [
        {"lineal": 0.2, "angular": 0.0, "duracion": 6.25, "levantar_lapiz": False}, 
        {"lineal": 0.0, "angular": -0.5, "duracion": 4.71, "levantar_lapiz": False}, 
        {"lineal": 0.2, "angular": 0.0, "duracion": 15.0, "levantar_lapiz": False}, 
        {"lineal": 0.0, "angular": -0.5, "duracion": 3.14, "levantar_lapiz": False}, 
        {"lineal": 0.2, "angular": 0.0, "duracion": 5.0, "levantar_lapiz": False}, 
        {"lineal": 0.0, "angular": 0.5, "duracion": 6.28, "levantar_lapiz": False}, 
        {"lineal": 0.2, "angular": 0.0, "duracion": 10.0, "levantar_lapiz": False}, 
    ]
    return dibujar_1