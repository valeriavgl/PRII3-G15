def get_moves_for_five():    
    dibujar_5 = [
        # Avance 0.5 m (0.5 / 0.2 = 2.5s)
        {"lineal": 0.2, "angular": 0.0, "duracion": 2.5, "levantar_lapiz": True}, 
        # Avance 1.0 m
        {"lineal": 0.2, "angular": 0.0, "duracion": 5.0, "levantar_lapiz": False},
        # Curva: combinamos velocidad lineal y angular al mismo tiempo
        {"lineal": 0.2, "angular": 0.26, "duracion": 12.0, "levantar_lapiz": False},
        # Avance 0.75 m
        {"lineal": 0.2, "angular": 0.0, "duracion": 3.75, "levantar_lapiz": False},
        # Giro -1.57 rad
        {"lineal": 0.0, "angular": -0.5, "duracion": 3.14, "levantar_lapiz": False},
        # Avance 1.5 m
        {"lineal": 0.2, "angular": 0.0, "duracion": 7.5, "levantar_lapiz": False},
        # Giro -1.57 rad
        {"lineal": 0.0, "angular": -0.5, "duracion": 3.14, "levantar_lapiz": False},
        # Avance 1.5 m
        {"lineal": 0.2, "angular": 0.0, "duracion": 7.5, "levantar_lapiz": False},
    ]
    return dibujar_5