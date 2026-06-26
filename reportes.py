from conexion import conectar

def listar_estudiantes():

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT alumno_id,
                rut,
                nombre,
                apellido
        FROM alumnos
    """)

    datos = cur.fetchall()

    print("\nLISTADO DE ALUMNOS")

    for d in datos:

        print(
            d[0],
            d[1],
            d[2],
            d[3]
        )

    cur.close()
    conn.close()