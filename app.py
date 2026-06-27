from flask import Flask, render_template, request, redirect, session, url_for
import psycopg
import os

app = Flask(__name__)
app.secret_key = "clave_secreta"

# Función de conexión original a Neon
def conectar():
    DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://usuario:password@endpoint/dbname?sslmode=require")
    return psycopg.connect(DATABASE_URL)

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_post():
    usuario = request.form["usuario"]
    password = request.form["password"]

    if usuario == "admin" and password == "1234":
        session["usuario"] = usuario
        return redirect("/inicio")

    return "Login incorrecto"              
    
@app.route("/inicio")
def inicio():
    return render_template("index.html")

# ================= MÓDULO ESTUDIANTES (CON DIRECCIÓN) =================

@app.route("/estudiantes")
def estudiantes():
    try:
        with conectar() as conn:
            with conn.cursor() as cur:
                # Trae los alumnos incluyendo la columna direccion (est[5])
                cur.execute("""
                    SELECT a.alumno_id, a.nombre, a.apellido, a.rut, COALESCE(c.nombre_carrera, 'Sin Carrera'), a.direccion 
                    FROM alumnos a
                    LEFT JOIN carreras c ON a.carrera_id = c.carrera_id
                    ORDER BY a.alumno_id DESC
                """)
                estudiantes_data = cur.fetchall()

                cur.execute("SELECT carrera_id, nombre_carrera FROM carreras ORDER BY nombre_carrera")
                carreras_data = cur.fetchall()

        return render_template("estudiantes.html", estudiantes=estudiantes_data, carreras=carreras_data)
    except Exception as e:
        return f"ERROR AL CARGAR ESTUDIANTES: {e}"

@app.route("/guardar_estudiante", methods=["POST"])
def guardar_estudiante():
    rut = request.form["rut"].strip()
    nombre = request.form["nombre"]
    apellido = request.form["apellido"]
    carrera_id = request.form["carrera_id"]
    direccion = request.form["direccion"].strip() # Captura la dirección

    try:
        with conectar() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO alumnos (rut, nombre, apellido, carrera_id, direccion) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (rut, nombre, apellido, int(carrera_id), direccion))
        return redirect("/estudiantes")
    except Exception as e:
        return f"<h3>Error al guardar estudiante: {e}</h3><br><a href='/estudiantes'>Volver</a>"
    
@app.route("/editar_estudiante/<int:id>", methods=["GET"])
def editar_estudiante(id):
    try:
        with conectar() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT alumno_id, nombre, apellido, rut, carrera_id, direccion FROM alumnos WHERE alumno_id = %s", (id,))
                alumno = cur.fetchone()
                
                cur.execute("SELECT carrera_id, nombre_carrera FROM carreras ORDER BY nombre_carrera")
                carreras_data = cur.fetchall()
        
        if alumno:
            return render_template("editar_estudiante.html", alumno=alumno, carreras=carreras_data)
        return "Estudiante no encontrado."
    except Exception as e:
        return f"ERROR AL CARGAR EDICIÓN: {e}"

@app.route("/actualizar_estudiante/<int:id>", methods=["POST"])
def actualizar_estudiante(id):
    nombre = request.form["nombre"]
    apellido = request.form["apellido"]
    rut = request.form["rut"].strip()
    carrera_id = request.form.get("carrera_id", 1)
    direccion = request.form["direccion"].strip() # Captura la dirección editada

    try:
        with conectar() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE alumnos 
                    SET nombre = %s, apellido = %s, rut = %s, carrera_id = %s, direccion = %s
                    WHERE alumno_id = %s
                """, (nombre, apellido, rut, int(carrera_id), direccion, id))
        return redirect("/estudiantes")
    except Exception as e:
        return f"ERROR AL ACTUALIZAR ESTUDIANTE: {e}"

# ================= MÓDULO PAGOS (TUS RUTAS ORIGINALES EXACTAS) =================

@app.route("/pagos")
def pagos():
    try:
        with conectar() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT p.pago_id, a.rut, a.nombre, a.apellido, p.fecha, p.monto, p.metodo_pago
                    FROM pagos p
                    JOIN alumnos a ON p.alumno_id = a.alumno_id
                    ORDER BY p.fecha DESC
                """)
                pagos_data = cur.fetchall()
                return render_template("pagos.html", pagos=pagos_data)
    except Exception as e:
        return f"Error al cargar pagos: {e}"

@app.route("/guardar_pago", methods=["POST"])
def guardar_pago():
    rut = request.form["rut"].strip()
    monto = request.form["monto"]
    fecha = request.form["fecha"]
    metodo_pago = request.form.get("metodo_pago", "Transferencia")

    try:
        with conectar() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT alumno_id FROM alumnos WHERE rut = %s", (rut,))
                alumno = cur.fetchone()

                if alumno:
                    alumno_id = alumno[0]
                    cur.execute("""
                        INSERT INTO pagos (alumno_id, monto, fecha, metodo_pago)
                        VALUES (%s, %s, %s, %s)
                    """, (alumno_id, monto, fecha, metodo_pago))
                else:
                    return f"Error: El RUT {rut} no está registrado."
        return redirect("/pagos")
    except Exception as e:
        return f"ERROR AL GUARDAR PAGO: {e}"

@app.route("/editar_pago/<int:id>")
def editar_pago(id):
    try:
        with conectar() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT p.pago_id, a.rut, p.monto, p.fecha, p.metodo_pago 
                    FROM pagos p 
                    JOIN alumnos a ON p.alumno_id = a.alumno_id 
                    WHERE p.pago_id = %s
                """, (id,))
                pago = cur.fetchone()
                if pago:
                    return render_template("editar_pago.html", pago=pago)
                return "Pago no encontrado."
    except Exception as e:
        return f"ERROR: {e}"

@app.route("/actualizar_pago/<int:id>", methods=["POST"])
def actualizar_pago(id):
    monto = request.form["monto"]
    fecha = request.form["fecha"]
    metodo_pago = request.form["metodo_pago"]
    try:
        with conectar() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE pagos SET monto = %s, fecha = %s, metodo_pago = %s WHERE pago_id = %s
                """, (monto, fecha, metodo_pago, id))
        return redirect("/pagos")
    except Exception as e:
        return f"ERROR: {e}"

# ================= MÓDULO BECAS (TU LÓGICA ORIGINAL) =================

@app.route("/becas")
def becas():
    try:
        with conectar() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, nombre_beneficio, monto_cobertura FROM catalogo_becas ORDER BY id ASC")
                catalogo_data = cur.fetchall()

                cur.execute("""
                    SELECT b.beca_id, a.rut, a.nombre, a.apellido, b.nombre_beca, b.monto 
                    FROM becas b
                    JOIN alumnos a ON b.alumno_id = a.alumno_id
                    ORDER BY b.beca_id DESC
                """)
                becas_asignadas = cur.fetchall()
                return render_template("becas.html", catalogo=catalogo_data, becas=becas_asignadas)
    except Exception as e:
        return f"Error en becas: {e}"
    
@app.route("/guardar_beca", methods=["POST"])
def guardar_beca():
    rut = request.form["rut"].strip()
    id_catalogo = request.form["id_catalogo"]
    try:
        with conectar() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT alumno_id FROM alumnos WHERE rut = %s", (rut,))
                alumno = cur.fetchone()
                if alumno:
                    alumno_id = alumno[0]
                    cur.execute("""
                        INSERT INTO becas (alumno_id, id_catalogo, nombre_beca, monto)
                        VALUES (%s, %s, (SELECT nombre_beneficio FROM catalogo_becas WHERE id = %s), (SELECT monto_cobertura FROM catalogo_becas WHERE id = %s))
                    """, (alumno_id, int(id_catalogo), int(id_catalogo), int(id_catalogo)))
                else:
                    return f"Error: El RUT {rut} no existe."
        return redirect("/becas")
    except Exception as e:
        return f"ERROR: {e}"

# ================= REPORTES Y TÓTEM ORIGINALES =================

@app.route("/morosos")
def morosos():
    try:
        with conectar() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT a.nombre, 
                            (c.costo_arancel - COALESCE((SELECT SUM(monto) FROM pagos WHERE alumno_id = a.alumno_id), 0)) AS deuda
                    FROM alumnos a
                    JOIN carreras c ON a.carrera_id = c.carrera_id
                """)
                data = cur.fetchall()
        return render_template("morosos.html", morosos=data)
    except Exception as e:
        return f"ERROR: {e}"

@app.route("/totem", methods=["GET"])
def totem_inicio():
    # Corregido: Ahora apunta a tu archivo real totem_ingreso.html
    return render_template("totem_ingreso.html", error=None)

@app.route("/totem_consulta", methods=["POST"])
def totem_consulta():
    rut_alumno = request.form.get("rut", "").strip()
    
    if not rut_alumno:
        return "Por favor, ingrese un RUT válido."
        
    try:
        with conectar() as conn:
            with conn.cursor() as cur:
                # 1. Buscamos los datos básicos del alumno y su carrera
                cur.execute("""
                    SELECT a.alumno_id, a.nombre, a.apellido, COALESCE(c.nombre_carrera, 'Sin Carrera'), a.direccion
                    FROM alumnos a
                    LEFT JOIN carreras c ON a.carrera_id = c.carrera_id
                    WHERE a.rut = %s
                """, (rut_alumno,))
                alumno = cur.fetchone()
                
                if not alumno:
                    # En caso de no encontrarlo, volvemos a mostrar la pantalla de ingreso con el error
                    return render_template("totem_ingreso.html", error=f"Estudiante con RUT {rut_alumno} no encontrado.")
                
                # 2. Buscamos sus pagos
                cur.execute("""
                    SELECT fecha, monto, metodo_pago 
                    FROM pagos 
                    WHERE alumno_id = %s 
                    ORDER BY fecha DESC
                """, (alumno[0],))
                pagos = cur.fetchall()
                
                # 3. Buscamos sus becas
                cur.execute("""
                    SELECT nombre_beca, monto 
                    FROM becas 
                    WHERE alumno_id = %s
                """, (alumno[0],))
                becas = cur.fetchall()
                
                # Corregido: Ahora envía los datos a tu archivo real totem_resultado.html
                return render_template("totem_resultado.html", alumno=alumno, pagos=pagos, becas=becas)
                
    except Exception as e:
        return f"<h3>Error interno en el Tótem:</h3><p>{e}</p><br><a href='/totem'>Volver</a>"

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)