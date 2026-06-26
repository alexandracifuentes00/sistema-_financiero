from conexion import conectar

conn = conectar()
cur = conn.cursor()

cur.execute("""

CREATE TABLE IF NOT EXISTS carreras(
    carrera_id SERIAL PRIMARY KEY,
    nombre_carrera VARCHAR(100),
    costo_matricula DECIMAL(10,2),
    costo_arancel DECIMAL(10,2)
);

CREATE TABLE IF NOT EXISTS alumnos(
    alumno_id SERIAL PRIMARY KEY,
    rut VARCHAR(15) UNIQUE,
    nombre VARCHAR(100),
    apellido VARCHAR(100),
    carrera_id INT,
    FOREIGN KEY(carrera_id)
    REFERENCES carreras(carrera_id)
);

CREATE TABLE IF NOT EXISTS pagos(
    pago_id SERIAL PRIMARY KEY,
    alumno_id INT,
    fecha DATE,
    monto DECIMAL(10,2),
    metodo_pago VARCHAR(50),
    FOREIGN KEY(alumno_id)
    REFERENCES alumnos(alumno_id)
);

CREATE TABLE IF NOT EXISTS becas(
    beca_id SERIAL PRIMARY KEY,
    alumno_id INT,
    nombre_beca VARCHAR(100),
    monto DECIMAL(10,2),
    FOREIGN KEY(alumno_id)
    REFERENCES alumnos(alumno_id)
);

""")

conn.commit()

cur.close()
conn.close()

print("Base de datos creada")