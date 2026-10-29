#def get_initial_moves():
#    posicionar = [
#        #rotarcion de la tortuga 3.14 radiantes
#        {"lineal":0.0, "angular": 3.14, "duracion": 1.0, "levantar_lapiz": True}, 
#        #posicionar la tortuga para el IV cuadrante, siguiendo el eje X
#        {"lineal":2.75, "angular": 0.0, "duracion": 1.0, "levantar_lapiz": True },
#        #rotacion de la tortuga -1.57 radianes
#        {"lineal":0.0, "angular":-1.57, "duracion": 1.0, "levantar_lapiz": True }, 
#        #subir la tortuga siguiendo el eje Y
#        {"lineal":2.25, "angular":0.0, "duracion": 1.0, "levantar_lapiz": True },
#        #rotacion de la tortuga -0.785 radianes
#        {"lineal":0.0, "angular":-0.785, "duracion": 1.0, "levantar_lapiz": True},
#        #subir la tortuga inclinada
#        {"lineal":0.25, "angular":0.0, "duracion": 1.0, "levantar_lapiz": True},
#    ]
#
#    return posicionar

def get_moves_for_one():
    dibujar_1 = [
        # Dibuja el palo vertical del "1" de abajo hacia arriba (1 metro)
        {"lineal": 0.2, "angular": 0.0, "duracion": 5.0}, 
        
        # Posicionarse para empezar el "5"
        # Giro 90 grados a la derecha
        {"lineal": 0.0, "angular": -0.5, "duracion": 3.14}, 
        # Avanza 1 metro hacia la derecha (espacio entre el 1 y el 5)
        {"lineal": 0.2, "angular": 0.0, "duracion": 5.0}, 
        # Giro 180 grados para empezar el cinco de derecha a izquierda
        {"lineal": 0.0, "angular": -0.5, "duracion": 6.28},
    ]
    return dibujar_1