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
@app.route("/becas", methods=["GET"])
def modulo_becas():
    try:
        with conectar() as conn:
            with conn.cursor() as cur:
                # 1. Catálogo oficial de becas (usa la columna id)
                cur.execute("SELECT id, nombre_beca, monto FROM catalogo_becas ORDER BY id ASC")
                becas_catalogo = cur.fetchall()
                
                # 2. Listado de becas asignadas (CORREGIDO: Cambiamos el '1' por 'b.id' para enlazar Editar y Eliminar)
                cur.execute("""
                    SELECT b.id, a.rut, a.nombre, a.apellido, b.nombre_beca, b.monto 
                    FROM becas b
                    JOIN alumnos a ON b.alumno_id = a.alumno_id
                    ORDER BY a.apellido ASC
                """)
                becas_asignadas = cur.fetchall()

        return render_template("becas.html", catalogo=becas_catalogo, becas=becas_asignadas)
        
    except Exception as e:
        return f"<h2>Error en becas:</h2><p>{e}</p><br><a href='/inicio'>Volver al menú</a>"
    
@app.route("/guardar_beca", methods=["POST"])
def guardar_beca_modulo():
    # 1. Recogemos los nombres de campo exactos que envía tu HTML (rut e id_catalogo)
    rut_alumno = request.form.get("rut", "").strip()
    id_catalogo = request.form.get("id_catalogo")
    
    if not rut_alumno or not id_catalogo:
        return "<h2>Error:</h2><p>Faltan datos obligatorios en el formulario.</p><br><a href='/becas'>Volver</a>"
        
    # Limpiamos los puntos del RUT por si el usuario lo escribió con ellos
    rut_limpio = rut_alumno.replace(".", "")
    try:
        with conectar() as conn:
            with conn.cursor() as cur:
                # 2. Buscamos el alumno_id correspondiente a ese RUT
                cur.execute("SELECT alumno_id FROM alumnos WHERE rut = %s", (rut_limpio,))
                alumno = cur.fetchone()
                if not alumno:
                    return f"<h2>Error:</h2><p>El RUT {rut_alumno} no corresponde a ningún alumno registrado.</p><br><a href='/becas'>Volver</a>"                
                alumno_id = alumno[0]                
                
                # 3. Obtenemos el nombre de la beca y el monto desde el catálogo oficial usando el id_catalogo
                cur.execute("SELECT nombre_beca, monto FROM catalogo_becas WHERE id = %s", (id_catalogo,))
                item_catalogo = cur.fetchone()                
                if not item_catalogo:
                    return "<h2>Error:</h2><p>La beca seleccionada no existe en el catálogo.</p><br><a href='/becas'>Volver</a>"                
                nombre_beca = item_catalogo[0]
                monto = item_catalogo[1]                
                
                # 4. Insertamos finalmente en la tabla 'becas' con todos los valores obligatorios llenos
                cur.execute("""
                    INSERT INTO becas (alumno_id, nombre_beca, monto) 
                    VALUES (%s, %s, %s)
                """, (alumno_id, nombre_beca, monto))                
                conn.commit()
                
        return redirect("/becas")        
    except Exception as e:
        return f"<h2>Error al agregar la beca:</h2><p>{e}</p><br><a href='/becas'>Volver a intentar</a>"
    
@app.route("/editar_beca", methods=["POST"])
def editar_beca():
    id_asignacion = request.form.get("id")
    nombre_beca = request.form.get("nombre_beca")
    monto = request.form.get("monto")
    
    try:
        with conectar() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE becas 
                    SET nombre_beca = %s, monto = %s 
                    WHERE id = %s
                """, (nombre_beca, monto, id_asignacion))
                conn.commit()
        return redirect("/becas")
    except Exception as e:
        return f"Error al editar la beca: {e}"

@app.route("/eliminar_beca/<int:id_asignacion>", methods=["GET"])
def eliminar_beca(id_asignacion):
    try:
        with conectar() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM becas WHERE id = %s", (id_asignacion,))
                conn.commit()
        return redirect("/becas")
    except Exception as e:
        return f"Error al eliminar la beca: {e}"

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
# ================= TÓTEM DE ALUMNOS =================

@app.route("/totem", methods=["GET"])
def totem_inicio():
    # CORREGIDO: Cambiado de totem.html a totem_ingreso.html
    return render_template("totem_ingreso.html", error=None)

@app.route("/totem_consulta", methods=["POST"])
def totem_consulta():
    rut_alumno = request.form.get("rut", "").strip()
    
    if not rut_alumno:
        return "Por favor, ingrese un RUT válido."
    
    # 🔥 LA SOLUCIÓN: Quitamos los puntos del RUT antes de ir a Neon
    # Así, si el usuario envía "18.453.221-K", Python buscará "18453221-K"
    rut_busqueda = rut_alumno.replace(".", "")
        
    try:
        with conectar() as conn:
            with conn.cursor() as cur:
                # 1. Buscamos los datos utilizando el RUT sin puntos (rut_busqueda)
                cur.execute("""
                    SELECT a.alumno_id, a.nombre, a.apellido, COALESCE(c.nombre_carrera, 'Sin Carrera'), a.direccion
                    FROM alumnos a
                    LEFT JOIN carreras c ON a.carrera_id = c.carrera_id
                    WHERE a.rut = %s
                """, (rut_busqueda,))
                alumno = cur.fetchone()
                
                if not alumno:
                    # Si no existe, devolvemos el error mostrando el RUT original con puntos para que el usuario vea qué escribió
                    return render_template("totem_ingreso.html", error=f"Estudiante con RUT {rut_alumno} no encontrado.")
                
                # 2. Buscamos sus pagos asociados usando el alumno_id encontrado
                cur.execute("""
                    SELECT fecha, monto, metodo_pago 
                    FROM pagos 
                    WHERE alumno_id = %s 
                    ORDER BY fecha DESC
                """, (alumno[0],))
                pagos = cur.fetchall()
                
                # 3. Buscamos sus becas asociadas usando el alumno_id encontrado
                cur.execute("""
                    SELECT nombre_beca, monto 
                    FROM becas 
                    WHERE alumno_id = %s
                """, (alumno[0],))
                becas = cur.fetchall()
                
                return render_template("totem_resultado.html", alumno=alumno, pagos=pagos, becas=becas)
                
    except Exception as e:
        return render_template("totem_ingreso.html", error=f"Error en la base de datos: {e}")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)