def get_moves_for_five():    
    dibujar_5 = [
        # Techo del 5 (de derecha a izquierda, 0.5m)
        {"lineal": 0.2, "angular": 0.0, "duracion": 2.5}, 
        # Giro 90 grados a la izquierda (mirando hacia abajo)
        {"lineal": 0.0, "angular": 0.5, "duracion": 3.14},
        # Mitad superior izquierda (bajando 0.5m)
        {"lineal": 0.2, "angular": 0.0, "duracion": 2.5},
        # Giro 90 grados a la izquierda (mirando hacia la derecha)
        {"lineal": 0.0, "angular": 0.5, "duracion": 3.14},
        # Cintura del 5 (de izquierda a derecha, 0.5m)
        {"lineal": 0.2, "angular": 0.0, "duracion": 2.5},
        # Giro 90 grados a la derecha (mirando hacia abajo)
        {"lineal": 0.0, "angular": -0.5, "duracion": 3.14},
        # Mitad inferior derecha (bajando 0.5m)
        {"lineal": 0.2, "angular": 0.0, "duracion": 2.5},
        # Giro 90 grados a la derecha (mirando hacia la izquierda)
        {"lineal": 0.0, "angular": -0.5, "duracion": 3.14},
        # Base del 5 (de derecha a izquierda, 0.5m)
        {"lineal": 0.2, "angular": 0.0, "duracion": 2.5},
    ]
    return dibujar_5