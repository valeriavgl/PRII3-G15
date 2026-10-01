def get_moves_for_one():
	"Lista de movimientos para dibujar el numero uno"
	return [
	        {"lineal":0.0, "angular": 3.1416, "duracion": 1.0, "levantar_lapiz": True},  #posicionar tortuga
		{"lineal":2.0, "angular": 0.0, "duracion": 1.5, "levantar_lapiz": True },   #Empezar Arriba
		{"lineal":0.0, "angular":-2.356, "duracion": 1.0, "levantar_lapiz": True }, #Posicion en 45


		#DIbujar 
		{"lineal":2.0, "angular": 0.0, "duracion": 0.75, "levantar_lapiz": False }, #DIagonal
		{"lineal":0.0, "angular": -2.356, "duracion": 1.0, "levantar_lapiz": False }, #APuntar hacia Bajo
		{"lineal":2.0, "angular": 0.0, "duracion": 2.5, "levantar_lapiz": False }, #Palo 
		{"lineal":0.0, "angular": -1.5708, "duracion": 1.0, "levantar_lapiz": False }, #Posicionar izq
		{"lineal":2.0, "angular": 0.0, "duracion": 0.5, "levantar_lapiz": False }, #B_mitadIzq
		{"lineal":0.0, "angular": 3.1416, "duracion": 1.0, "levantar_lapiz": False }, #POsicionar der
		{"lineal":2.0, "angular": 0.0, "duracion": 1.0, "levantar_lapiz": False }, #B_MitadDer
	]
