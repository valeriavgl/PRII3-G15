# def get_initial_moves():
#     posicionar = [
#         # Giro 3.14 rad (3.14 / 0.5 = 6.28s)
#         {"lineal": 0.0, "angular": 0.5, "duracion": 6.28, "levantar_lapiz": True}, 
#         # Avance 2.75 m (2.75 / 0.2 = 13.75s)
#         {"lineal": 0.2, "angular": 0.0, "duracion": 13.75, "levantar_lapiz": True},
#         # Giro -1.57 rad
#         {"lineal": 0.0, "angular": -0.5, "duracion": 3.14, "levantar_lapiz": True}, 
#         # Avance 2.25 m
#         {"lineal": 0.2, "angular": 0.0, "duracion": 11.25, "levantar_lapiz": True},
#         # Giro -0.785 rad
#         {"lineal": 0.0, "angular": -0.5, "duracion": 1.57, "levantar_lapiz": True},
#         # Avance 0.25 m
#         {"lineal": 0.2, "angular": 0.0, "duracion": 1.25, "levantar_lapiz": True},
#     ]
#     return posicionar

def get_moves_for_one():
    dibujar_1 = [
        # --- POSICIONAMIENTO INICIAL ---
        # Avanza 0.5m para salir del punto de aparición
        {"lineal": 0.2, "angular": 0.0, "duracion": 2.5}, 
        # Gira 90 grados a la izquierda para mirar hacia arriba
        {"lineal": 0.0, "angular": 0.91, "duracion": 1.73},
        # Pausa de 1 segundo (velocidad 0) antes de empezar
        {"lineal": 0.0, "angular": 0.0, "duracion": 1.0},
        # --- DIBUJO DEL "1" ---
        # Dibuja el palo vertical del "1" de abajo hacia arriba (1 metro)
        {"lineal": 0.2, "angular": 0.0, "duracion": 5.0}, 
        # Posicionarse para empezar el "5"
        # Giro 90 grados a la derecha
        {"lineal": 0.0, "angular": -0.91, "duracion": 1.73}, 
        # Avanza 1 metro hacia la derecha (espacio entre el 1 y el 5)
        {"lineal": 0.2, "angular": 0.0, "duracion": 5.0}, 
        # Giro 180 grados para empezar el cinco de derecha a izquierda
        {"lineal": 0.0, "angular": -0.91, "duracion": 3.45},
    ]
    return dibujar_1