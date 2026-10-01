def get_moves_for_five():    

    dibujar_5 = [
            #espacio para dibujar el número cinco
            {"lineal": 0.5, "angular": 0.0, "duracion": 1.0, "levantar_lapiz": True }, 
            #base del cinco
            {"lineal": 1.0, "angular": 0.0, "duracion": 1.0, "levantar_lapiz": False},
            #Curva del 5
            {"lineal": 2.355, "angular": 3.14, "duracion": 1.0, "levantar_lapiz": False},
            #mitad del 5
            {"lineal": 0.75, "angular": 0.0, "duracion": 1.0, "levantar_lapiz": False},
            #rotacion de -1.57 radianes
            {"lineal": 0.0, "angular": -1.57, "duracion": 1.0, "levantar_lapiz": False},
            #subida 
            {"lineal": 1.5, "angular": 0.0, "duracion": 1.0, "levantar_lapiz": False},
            #rotacion de -1.57 radianes
            {"lineal": 0.0, "angular": -1.57, "duracion": 1.0, "levantar_lapiz": False},
            #techo
            {"lineal": 1.5, "angular": 0.0, "duracion": 1.0, "levantar_lapiz": False},
    ]
    return dibujar_5

