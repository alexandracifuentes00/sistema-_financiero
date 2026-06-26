from conexion import conectar
from datetime import date

def registrar_pago():

    alumno = input("ID Alumno: ")
    monto = float(input("Monto: "))
    metodo = input("Método pago: ")

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO pagos
        (alumno_id,fecha,monto,metodo_pago)
        VALUES(%s,%s,%s,%s)
    """,
    (alumno,date.today(),monto,metodo))

    conn.commit()

    cur.close()
    conn.close()

    print("Pago registrado")