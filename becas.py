from conexion import conectar

def registrar_beca():

    alumno = input("ID Alumno: ")
    nombre = input("Nombre beca: ")
    monto = float(input("Monto: "))

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO becas
        (alumno_id,nombre_beca,monto)
        VALUES(%s,%s,%s)
    """,
    (alumno,nombre,monto))

    conn.commit()

    cur.close()
    conn.close()

    print("Beca registrada")