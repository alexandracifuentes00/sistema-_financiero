from conexion import conectar

def registrar_estudiante():

    rut = input("Rut: ")
    nombre = input("Nombre: ")
    apellido = input("Apellido: ")
    carrera = input("ID Carrera: ")

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO alumnos
        (rut,nombre,apellido,carrera_id)
        VALUES(%s,%s,%s,%s)
    """,
    (rut,nombre,apellido,carrera))

    conn.commit()

    cur.close()
    conn.close()

    print("Alumno registrado")