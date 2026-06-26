import psycopg
import os

def conectar():
    # Obtiene la URL que configuraremos en el servidor
    # Si estás en tu PC local, puedes poner la cadena de conexión directamente como string 
    # solo para probar, pero recuerda borrarla antes de subir a GitHub.
    return psycopg.connect(os.environ.get("DATABASE_URL"))