from conexion import conectar

def registrar_carrera():

    nombre = input("Nombre carrera: ")
    matricula = float(input("Costo matrícula: "))
    arancel = float(input("Costo arancel: "))

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO carreras
        (nombre_carrera,costo_matricula,costo_arancel)
        VALUES(%s,%s,%s)
    """,
    (nombre,matricula,arancel))

    conn.commit()

    cur.close()
    conn.close()

    print("Carrera registrada")