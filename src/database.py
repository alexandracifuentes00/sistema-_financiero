import psycopg2

# Configuración de conexión (Ajusta estos valores a tu servidor PostgreSQL)
DB_CONFIG = {
    "host": "localhost",
    "database": "cft_finanzas",
    "user": "tu_usuario",
    "password": "6211"
}

def obtener_conexion():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def inicializar_tablas():
    conn = obtener_conexion()
    if not conn: return
    
    cur = conn.cursor()
    # Creación de tablas según tu diseño
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Carreras (
            carrera_id SERIAL PRIMARY KEY,
            nombre_carrera VARCHAR(100),
            costo_matricula DECIMAL(12,2),
            costo_arancel DECIMAL(12,2)
        );
        
        CREATE TABLE IF NOT EXISTS Alumnos (
            alumno_id SERIAL PRIMARY KEY,
            rut VARCHAR(20) UNIQUE,
            nombre VARCHAR(50),
            apellido VARCHAR(50),
            carrera_id INTEGER REFERENCES Carreras(carrera_id)
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()
    print("Tablas verificadas/creadas correctamente en PostgreSQL.")