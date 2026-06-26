from flask import Flask, render_template, request, redirect, session
from conexion import conectar

app = Flask(__name__)
app.secret_key = "clave_secreta"

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

# ================= MÓDULO ESTUDIANTES =================

@app.route("/estudiantes")
def estudiantes():
    try:
        with conectar() as conn:
            with conn.cursor() as cur:
                # 1. Traer estudiantes
                cur.execute("""
                    SELECT a.alumno_id, a.nombre, a.apellido, a.rut, COALESCE(c.nombre_carrera, 'Sin Carrera') 
                    FROM alumnos a
                    LEFT JOIN carreras c ON a.carrera_id = c.carrera_id
                    ORDER BY a.alumno_id DESC
                """)
                estudiantes_data = cur.fetchall()

                # 2. Traer todas las carreras para el menú desplegable
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

    try:
        with conectar() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO alumnos (rut, nombre, apellido, carrera_id) 
                    VALUES (%s, %s, %s, %s)
                """, (rut, nombre, apellido, int(carrera_id)))
        
        return redirect("/estudiantes")

    except Exception as e:
        print(f"Error detectado: {e}")
        return f"<h3>Error al guardar en la Base de Datos: {e}</h3><br><a href='/estudiantes'>Volver a Intentar</a>"
    
@app.route("/editar_estudiante/<int:id>", methods=["GET"])
def editar_estudiante(id):
    try:
        with conectar() as conn:
            with conn.cursor() as cur:
                # 1. Buscar al alumno
                cur.execute("SELECT alumno_id, nombre, apellido, rut, carrera_id FROM alumnos WHERE alumno_id = %s", (id,))
                alumno = cur.fetchone()
                
                # 2. Buscar todas las carreras
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

    try:
        with conectar() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE alumnos 
                    SET nombre = %s, apellido = %s, rut = %s, carrera_id = %s
                    WHERE alumno_id = %s
                """, (nombre, apellido, rut, int(carrera_id), id))
        return redirect("/estudiantes")
    except Exception as e:
        return f"ERROR AL ACTUALIZAR ESTUDIANTE: {e}"

# ================= MÓDULO PAGOS =================

@app.route("/pagos")
def pagos():
    try:
        with conectar() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT p.pago_id, a.rut, a.nombre, p.monto, p.fecha, p.metodo_pago 
                    FROM pagos p
                    JOIN alumnos a ON p.alumno_id = a.alumno_id
                    ORDER BY p.fecha DESC
                """)
                data = cur.fetchall()
        return render_template("pagos.html", pagos=data)
    except Exception as e:
        return f"ERROR EN PAGOS: {e}"

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
                    return f"Error: El RUT {rut} no está registrado en el sistema."
        return redirect("/pagos")
    except Exception as e:
        return f"ERROR AL GUARDAR PAGO: {e}"

# ================= MÓDULO BECAS =================
@app.route("/becas")
def becas():
    try:
        with conectar() as conn:
            with conn.cursor() as cur:
                # 1. Traer el catálogo oficial para el menú desplegable
                cur.execute("SELECT id, nombre_beca, monto FROM catalogo_becas ORDER BY id ASC")
                catalogo_data = cur.fetchall()

                # 2. Traer las becas ya asignadas a los alumnos
                cur.execute("""
                    SELECT b.beca_id, a.rut, a.nombre, a.apellido, b.nombre_beca, b.monto 
                    FROM becas b
                    JOIN alumnos a ON b.alumno_id = a.alumno_id
                    ORDER BY b.beca_id DESC
                """)
                becas_asignadas = cur.fetchall()

                return render_template("becas.html", catalogo=catalogo_data, becas=becas_asignadas)
    except Exception as e:
        return f"Error en el módulo de becas: {e}"
    
@app.route("/guardar_beca", methods=["POST"])
def guardar_beca():
    rut = request.form["rut"].strip()
    id_catalogo = request.form["id_catalogo"] # Recibimos el ID seleccionado del menú desplegable

    try:
        with conectar() as conn:
            with conn.cursor() as cur:
                # Buscar al alumno por su RUT
                cur.execute("SELECT alumno_id FROM alumnos WHERE rut = %s", (rut,))
                alumno = cur.fetchone()

                if alumno:
                    alumno_id = alumno[0]
                    # Insertamos la beca guardando la referencia al catálogo
                    cur.execute("""
                        INSERT INTO becas (alumno_id, id_catalogo, nombre_beca, monto)
                        VALUES (%s, %s, (SELECT nombre_beneficio FROM catalogo_becas WHERE id_catalogo = %s), (SELECT monto_cobertura FROM catalogo_becas WHERE id_catalogo = %s))
                    """, (alumno_id, int(id_catalogo), int(id_catalogo), int(id_catalogo)))
                else:
                    return f"Error: El RUT {rut} no está registrado en el sistema."
        return redirect("/becas")
    except Exception as e:
        return f"ERROR AL GUARDAR LA BECA: {e}"

# ================= REPORTES Y OTROS =================

@app.route("/reportes")
def reportes():
    return render_template("reportes.html")

# 📊 MODIFICADO: Módulo de Morosos Inteligente con Gratuidad Dinámica
# 📊 MODIFICADO: Módulo de Morosos Inteligente con Gratuidad Dinámica Corregido
# 📊 MODIFICADO: Módulo de Morosos Inteligente que detecta Gratuidad al 100%
@app.route("/morosos")
def morosos():
    try:
        with conectar() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        a.nombre AS estudiante,
                        -- 💡 LÓGICA DE DEUDA: Si tiene Gratuidad la deuda es 0, si no, se restan los pagos y el monto de la beca
                        CASE 
                            WHEN EXISTS (SELECT 1 FROM becas WHERE alumno_id = a.alumno_id AND nombre_beca LIKE '%Gratuidad%') THEN 0
                            ELSE (c.costo_arancel 
                                    - COALESCE((SELECT SUM(monto) FROM pagos WHERE alumno_id = a.alumno_id), 0)
                                    - COALESCE((SELECT SUM(monto) FROM becas WHERE alumno_id = a.alumno_id), 0))
                        END AS deuda_pendiente,
                        'Pendiente' AS estado,
                        -- 💡 LÓGICA DE CUOTAS: Si tiene Gratuidad es 0 cuotas, si no, se calcula según el saldo
                        CASE 
                            WHEN EXISTS (SELECT 1 FROM becas WHERE alumno_id = a.alumno_id AND nombre_beca LIKE '%Gratuidad%') THEN 0
                            ELSE CEIL((c.costo_arancel 
                                    - COALESCE((SELECT SUM(monto) FROM pagos WHERE alumno_id = a.alumno_id), 0)
                                    - COALESCE((SELECT SUM(monto) FROM becas WHERE alumno_id = a.alumno_id), 0)) / 150000)
                        END AS cuotas_pendientes
                    FROM alumnos a
                    JOIN carreras c ON a.carrera_id = c.carrera_id
                    -- Filtramos para que SOLO aparezcan los que tienen deuda real mayor a 0
                    WHERE (
                        CASE 
                            WHEN EXISTS (SELECT 1 FROM becas WHERE alumno_id = a.alumno_id AND nombre_beca LIKE '%Gratuidad%') THEN 0
                            ELSE (c.costo_arancel 
                                    - COALESCE((SELECT SUM(monto) FROM pagos WHERE alumno_id = a.alumno_id), 0)
                                    - COALESCE((SELECT SUM(monto) FROM becas WHERE alumno_id = a.alumno_id), 0))
                        END
                    ) > 0
                """)
                data = cur.fetchall()
        return render_template("morosos.html", morosos=data)
    except Exception as e:
        return f"ERROR EN MOROSOS: {e}"

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ================= TÓTEM DE ALUMNOS =================

@app.route("/totem", methods=["GET"])
def totem_inicio():
    return render_template("totem_ingreso.html", error=None)

@app.route("/totem/consulta", methods=["POST"])
def totem_consulta():
    rut_alumno = request.form.get("rut")
    
    if not rut_alumno:
        return render_template("totem_ingreso.html", error="Por favor, ingrese un RUT.")
        
    rut_limpio = rut_alumno.replace(".", "").replace("-", "").replace(" ", "").lower().strip()
        
    try:
        with conectar() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT a.alumno_id, a.nombre, a.apellido, 
                            COALESCE(c.nombre_carrera, 'Carrera no asignada'), 
                            COALESCE(c.costo_arancel, 0)
                    FROM alumnos a
                    LEFT JOIN carreras c ON a.carrera_id = c.carrera_id
                    WHERE TRIM(LOWER(a.rut)) = %s 
                        OR LOWER(REPLACE(REPLACE(REPLACE(TRIM(a.rut), '.', ''), '-', ''), ' ', '')) = %s
                """, (rut_alumno.strip().lower(), rut_limpio))
                
                alumno = cur.fetchone()

                if not alumno:
                    return render_template("totem_ingreso.html", error=f"El RUT {rut_alumno} no coincide en la Base de Datos.")
                    
                alumno_id = alumno[0]
                
                cur.execute("SELECT fecha, monto, metodo_pago FROM pagos WHERE alumno_id = %s ORDER BY fecha DESC", (alumno_id,))
                pagos = cur.fetchall()
                
                cur.execute("SELECT nombre_beca, monto FROM becas WHERE alumno_id = %s", (alumno_id,))
                becas = cur.fetchall()
                
                return render_template("totem_resultado.html", alumno=alumno, rut=rut_alumno, pagos=pagos, becas=becas)
        
    except Exception as e:
        return f"<h3>Error en el Tótem:</h3> <p>{e}</p>"

# ================= CONTROL DE SEGURIDAD PERFECTO =================

@app.before_request
def verificar_sesion():
    # 1. Definimos explícitamente los endpoints que NO necesitan login
    # 'totem' es la pantalla de ingreso, 'totem_consulta' es la que procesa el formulario
    rutas_libres = ['login', 'login_post', 'static', 'totem', 'totem_consulta']
    
    # request.endpoint contiene el nombre de la función que se está ejecutando
    if request.endpoint in rutas_libres:
        return # Si está en la lista, permitimos el acceso libre de inmediato
        
    # 2. Si NO es una ruta libre y el usuario no está en sesión, lo mandamos al login
    if 'usuario' not in session:
        return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)