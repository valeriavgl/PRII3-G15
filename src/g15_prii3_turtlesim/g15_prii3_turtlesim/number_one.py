def get_initial_moves():
    posicionar = [
        #rotarcion de la tortuga 3.14 radiantes
        {"lineal":0.0, "angular": 3.14, "duracion": 1.0, "levantar_lapiz": True}, 
        #posicionar la tortuga para el IV cuadrante, siguiendo el eje X
        {"lineal":2.75, "angular": 0.0, "duracion": 1.0, "levantar_lapiz": True },
        #rotacion de la tortuga -1.57 radianes
        {"lineal":0.0, "angular":-1.57, "duracion": 1.0, "levantar_lapiz": True }, 
        #subir la tortuga siguiendo el eje Y
        {"lineal":2.25, "angular":0.0, "duracion": 1.0, "levantar_lapiz": True },
        #rotacion de la tortuga -0.785 radianes
        {"lineal":0.0, "angular":-0.785, "duracion": 1.0, "levantar_lapiz": True},
        #subir la tortuga inclinada
        {"lineal":0.25, "angular":0.0, "duracion": 1.0, "levantar_lapiz": True},
    ]

    return posicionar


def get_moves_for_one():
	dibujar_1 = [
		{"lineal":1.25, "angular": 0.0, "duracion": 1.0, "levantar_lapiz": False }, #DIagonal
		{"lineal":0.0, "angular": -2.355, "duracion": 1.0, "levantar_lapiz": False }, #APuntar hacia Bajo
		{"lineal":3.0, "angular": 0.0, "duracion": 1.0, "levantar_lapiz": False }, #Palo 
		{"lineal":0.0, "angular": -1.57, "duracion": 1.0, "levantar_lapiz": False }, #Posicionar izq
		{"lineal":1.0, "angular": 0.0, "duracion": 1.0, "levantar_lapiz": False }, #B_mitadIzq
		{"lineal":0.0, "angular": 3.14, "duracion": 1.0, "levantar_lapiz": False }, #POsicionar der
		{"lineal":2.0, "angular": 0.0, "duracion": 1.0, "levantar_lapiz": False }, #B_MitadDer
	]
	return dibujar_1