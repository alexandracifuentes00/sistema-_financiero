# Sistema de Gestión Financiera - CFT Tarapacá 🎓💰

Este es un sistema web integral de gestión financiera desarrollado en **Python** con **Flask**, diseñado específicamente para administrar los procesos de estudiantes, carreras, cobros de aranceles, asignación de becas, registro de pagos e historiales de transacciones dentro del CFT Tarapacá.

El sistema también cuenta con un **Módulo de Tótem autoservicio**, permitiendo que los alumnos consulten su estado financiero y beneficios vigentes de forma rápida y segura utilizando solo su RUT.

---

## 🚀 Características Principales

* **Autenticación del Sistema:** Acceso controlado mediante credenciales institucionales seguras para la administración.
* **Gestión de Estudiantes y Carreras:** Registro, edición e indexación de matrículas, aranceles y datos del alumnado.
* **Control de Pagos:** Módulo para procesar abonos a las cuentas corrientes de los alumnos en tiempo real.
* **Gestión de Becas:** Asignación automática de beneficios estatales o institucionales (como la Gratuidad) con cálculo automático de coberturas.
* **Reportes y Morosidad:** Visualización de balances generales, montos recaudados e identificación inmediata de alumnos con saldos pendientes.
* **Módulo Tótem Independiente:** Interfaz pública optimizada con teclado virtual en pantalla para consultas rápidas de los estudiantes.

---

## 🛠️ Tecnologías Utilizadas

* **Backend:** Python 3 con el framework Flask.
* **Base de Datos:** PostgreSQL (Alojado en la plataforma Serverless de alto rendimiento **Neon**).
* **Frontend:** HTML5, CSS3 nativo (estilos corporativos limpios) y JavaScript dinámico.
* **Despliegue y Servidor:** Render con Gunicorn en entorno de producción.

---

## 📦 Requisitos e Instalación Local

Si deseas probar el proyecto localmente, sigue estos pasos:

### 1. Clonar el repositorio
```bash
git clone [https://github.com/alexandracifuentes00/sistema-_financiero.git](https://github.com/alexandracifuentes00/sistema-_financiero.git)
cd sistema-_financiero