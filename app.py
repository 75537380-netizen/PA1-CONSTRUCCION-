"""
app.py
------
Punto de entrada de la aplicacion Flask.
Incluye autenticacion, gestion de tareas, categorias y planificacion con IA.
"""

import os
from datetime import datetime, date
from typing import Optional

import anthropic
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from fpdf import FPDF
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from mysql.connector import Error as MySQLError
from werkzeug.security import generate_password_hash, check_password_hash

import database as db
from models import Tarea, Categoria, HorarioUsuario

load_dotenv()

# ---------------------------------------------------------------------------
# Configuracion de la aplicacion
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.secret_key = "dev-secret-key-ucci-2024"

# Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Inicia sesion para continuar."
login_manager.login_message_category = "warning"

# La credencial se valida al momento de usar la IA para evitar inicializar
# el cliente con un valor vacio, lo que provoca errores de autenticacion.


@login_manager.user_loader
def cargar_usuario(usuario_id: str):
    try:
        return db.obtener_usuario_por_id(int(usuario_id))
    except (MySQLError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Autenticacion
# ---------------------------------------------------------------------------

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        nombre = request.form.get("nombre_usuario", "").strip()
        contrasena = request.form.get("contrasena", "").strip()
        confirmar = request.form.get("confirmar_contrasena", "").strip()

        if not nombre or not contrasena:
            flash("El nombre de usuario y la contrasena son obligatorios.", "warning")
            return render_template("registro.html")

        if len(contrasena) < 6:
            flash("La contrasena debe tener al menos 6 caracteres.", "warning")
            return render_template("registro.html")

        if contrasena != confirmar:
            flash("Las contrasenas no coinciden.", "warning")
            return render_template("registro.html")

        try:
            if db.existe_nombre_usuario(nombre):
                flash("Ese nombre de usuario ya esta en uso.", "warning")
                return render_template("registro.html")

            hash_pw = generate_password_hash(contrasena)
            db.crear_usuario(nombre, hash_pw)
            flash("Cuenta creada exitosamente. Inicia sesion.", "success")
            return redirect(url_for("login"))
        except MySQLError as error:
            flash(f"Error al crear la cuenta: {error}", "danger")

    return render_template("registro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        nombre = request.form.get("nombre_usuario", "").strip()
        contrasena = request.form.get("contrasena", "").strip()

        try:
            usuario = db.obtener_usuario_por_nombre(nombre)
            if usuario and check_password_hash(usuario.contrasena_hash, contrasena):
                login_user(usuario)
                flash(f"Bienvenido, {usuario.nombre_usuario}!", "success")
                return redirect(url_for("index"))
            else:
                flash("Nombre de usuario o contrasena incorrectos.", "danger")
        except MySQLError as error:
            flash(f"Error al iniciar sesion: {error}", "danger")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesion cerrada correctamente.", "info")
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Tareas
# ---------------------------------------------------------------------------

@app.route("/")
@login_required
def index():
    filtro_estado = request.args.get("estado", "").strip().lower() or None
    mostrar_modal_nueva = request.args.get("crear") == "1"
    if filtro_estado not in (None, "pendiente", "completada"):
        filtro_estado = None

    try:
        tareas = db.obtener_todas_las_tareas(current_user.id, filtro_estado)
    except MySQLError as error:
        flash(f"Error al cargar las tareas: {error}", "danger")
        tareas = []

    try:
        horario_usuario = db.obtener_horario_usuario(current_user.id)
    except MySQLError as error:
        flash(f"Error al cargar el horario: {error}", "danger")
        horario_usuario = HorarioUsuario(usuario_id=current_user.id)

    return render_template(
        "index.html",
        tareas=tareas,
        filtro_activo=filtro_estado,
        categorias=_obtener_categorias_usuario(),
        horario_usuario=horario_usuario,
        tarea_modal=Tarea(titulo="", prioridad="media", usuario_id=current_user.id),
        mostrar_modal_nueva=mostrar_modal_nueva,
    )


@app.route("/tarea/nueva", methods=["GET", "POST"])
@login_required
def nueva_tarea():
    categorias = _obtener_categorias_usuario()

    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        descripcion = request.form.get("descripcion", "").strip() or None
        prioridad = request.form.get("prioridad", "media")
        fecha_limite_str = request.form.get("fecha_limite", "").strip() or None
        categoria_id = request.form.get("categoria_id") or None
        if categoria_id:
            categoria_id = int(categoria_id)

        fecha_limite = _parsear_fecha(fecha_limite_str)

        tarea = Tarea(
            titulo=titulo, descripcion=descripcion, prioridad=prioridad,
            fecha_limite=fecha_limite, categoria_id=categoria_id,
            usuario_id=current_user.id,
        )

        if not tarea.es_valida():
            flash("El titulo es obligatorio y la prioridad debe ser baja, media o alta.", "warning")
            return _renderizar_index_con_modal_nueva(
                tarea=tarea,
                categorias=categorias,
                filtro_estado=request.args.get("estado", "").strip().lower() or None,
            )

        try:
            nuevo_id = db.insertar_tarea(tarea)
            flash(f'Tarea "{titulo}" creada exitosamente (ID: {nuevo_id}).', "success")
            return redirect(url_for("index"))
        except (MySQLError, ValueError) as error:
            flash(f"Error al crear la tarea: {error}", "danger")
            return _renderizar_index_con_modal_nueva(
                tarea=tarea,
                categorias=categorias,
                filtro_estado=request.args.get("estado", "").strip().lower() or None,
            )

    if request.args.get("fallback") == "1":
        tarea_vacia = Tarea(titulo="", prioridad="media", usuario_id=current_user.id)
        return render_template("form.html", tarea=tarea_vacia, accion="Crear", categorias=categorias)

    return redirect(url_for("index", crear=1))


@app.route("/tarea/<int:tarea_id>/editar", methods=["GET", "POST"])
@login_required
def editar_tarea(tarea_id: int):
    categorias = _obtener_categorias_usuario()

    try:
        tarea = db.obtener_tarea_por_id(tarea_id, current_user.id)
    except MySQLError as error:
        flash(f"Error al cargar la tarea: {error}", "danger")
        return redirect(url_for("index"))

    if tarea is None:
        flash(f"No se encontro la tarea con ID {tarea_id}.", "warning")
        return redirect(url_for("index"))

    if request.method == "POST":
        tarea.titulo = request.form.get("titulo", "").strip()
        tarea.descripcion = request.form.get("descripcion", "").strip() or None
        tarea.prioridad = request.form.get("prioridad", "media")
        tarea.completada = "completada" in request.form
        fecha_limite_str = request.form.get("fecha_limite", "").strip() or None
        tarea.fecha_limite = _parsear_fecha(fecha_limite_str)
        categoria_id = request.form.get("categoria_id") or None
        tarea.categoria_id = int(categoria_id) if categoria_id else None

        if not tarea.es_valida():
            flash("El titulo es obligatorio y la prioridad debe ser baja, media o alta.", "warning")
            return render_template("form.html", tarea=tarea, accion="Editar", categorias=categorias)

        try:
            modificada = db.actualizar_tarea(tarea)
            if modificada:
                flash(f'Tarea "{tarea.titulo}" actualizada exitosamente.', "success")
            else:
                flash("No se encontro la tarea para actualizar.", "warning")
            return redirect(url_for("index"))
        except (MySQLError, ValueError) as error:
            flash(f"Error al actualizar la tarea: {error}", "danger")
            return render_template("form.html", tarea=tarea, accion="Editar", categorias=categorias)

    return render_template("form.html", tarea=tarea, accion="Editar", categorias=categorias)


@app.route("/tarea/<int:tarea_id>/toggle", methods=["POST"])
@login_required
def toggle_estado(tarea_id: int):
    try:
        tarea = db.obtener_tarea_por_id(tarea_id, current_user.id)
    except MySQLError as error:
        flash(f"Error al recuperar la tarea: {error}", "danger")
        return redirect(url_for("index"))

    if tarea is None:
        flash(f"No se encontro la tarea con ID {tarea_id}.", "warning")
        return redirect(url_for("index"))

    nuevo_estado = not tarea.completada
    try:
        db.cambiar_estado_tarea(tarea_id, current_user.id, nuevo_estado)
        etiqueta = "completada" if nuevo_estado else "pendiente"
        flash(f'Tarea "{tarea.titulo}" marcada como {etiqueta}.', "success")
    except MySQLError as error:
        flash(f"Error al cambiar el estado: {error}", "danger")

    return redirect(url_for("index"))


@app.route("/tarea/<int:tarea_id>/eliminar", methods=["POST"])
@login_required
def eliminar_tarea(tarea_id: int):
    try:
        tarea = db.obtener_tarea_por_id(tarea_id, current_user.id)
        if tarea is None:
            flash(f"No se encontro la tarea con ID {tarea_id}.", "warning")
            return redirect(url_for("index"))

        eliminada = db.eliminar_tarea(tarea_id, current_user.id)
        if eliminada:
            flash(f'Tarea "{tarea.titulo}" eliminada exitosamente.', "success")
        else:
            flash("No se pudo eliminar la tarea.", "warning")
    except MySQLError as error:
        flash(f"Error al eliminar la tarea: {error}", "danger")

    return redirect(url_for("index"))


@app.route("/tareas/reordenar", methods=["POST"])
@login_required
def reordenar_tareas():
    """Recibe lista de IDs en el nuevo orden y actualiza el campo orden."""
    datos = request.get_json(silent=True)
    ids = datos.get("ids", []) if datos else []
    if not ids:
        return jsonify({"ok": False, "error": "Lista vacia"}), 400
    try:
        db.actualizar_orden_tareas(current_user.id, ids)
        return jsonify({"ok": True})
    except MySQLError as error:
        return jsonify({"ok": False, "error": str(error)}), 500


@app.route("/exportar/pdf")
@login_required
def exportar_pdf():
    """Genera y descarga un PDF con las tareas pendientes del usuario."""
    from flask import make_response
    from datetime import date

    try:
        tareas = db.obtener_todas_las_tareas(current_user.id, filtro_estado="pendiente")
    except MySQLError as error:
        flash(f"Error al obtener tareas: {error}", "danger")
        return redirect(url_for("index"))

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Titulo
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 12, "Tareas Pendientes", ln=True)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, f"Usuario: {current_user.nombre_usuario}   |   Fecha: {date.today().strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(4)

    # Linea separadora
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)

    if not tareas:
        pdf.set_font("Helvetica", "I", 11)
        pdf.set_text_color(120, 120, 120)
        pdf.cell(0, 8, "No tienes tareas pendientes.", ln=True)
    else:
        for i, tarea in enumerate(tareas, 1):
            # Indicador de prioridad como cuadrado de color
            prioridad_colores = {"alta": (239, 68, 68), "media": (245, 158, 11), "baja": (34, 197, 94)}
            r, g, b = prioridad_colores.get(tarea.prioridad, (100, 100, 100))
            pdf.set_fill_color(r, g, b)
            pdf.rect(10, pdf.get_y() + 2, 3, 5, "F")

            # Titulo de la tarea
            pdf.set_x(16)
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(30, 30, 30)
            titulo_safe = tarea.titulo.encode("latin-1", "replace").decode("latin-1")
            pdf.cell(0, 8, f"{i}. {titulo_safe}", ln=True)

            # Meta info
            meta_parts = [f"Prioridad: {tarea.prioridad.capitalize()}"]
            if tarea.nombre_categoria:
                cat_safe = tarea.nombre_categoria.encode("latin-1", "replace").decode("latin-1")
                meta_parts.append(f"Categoria: {cat_safe}")
            if tarea.fecha_limite:
                meta_parts.append(f"Limite: {tarea.fecha_limite.strftime('%d/%m/%Y')}")
            if tarea.descripcion:
                desc_safe = tarea.descripcion[:80].encode("latin-1", "replace").decode("latin-1")
                meta_parts.append(f"Nota: {desc_safe}")

            pdf.set_x(16)
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 5, "   ".join(meta_parts), ln=True)
            pdf.ln(3)

    # Footer
    pdf.set_y(-20)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 5, "Sistema de Gestion de Tareas - UCCI", align="C")

    pdf_bytes = pdf.output()
    response = make_response(bytes(pdf_bytes))
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"attachment; filename=tareas_{date.today().strftime('%Y%m%d')}.pdf"
    return response


# ---------------------------------------------------------------------------
# Categorias
# ---------------------------------------------------------------------------

@app.route("/categorias")
@login_required
def categorias():
    try:
        lista_categorias = db.obtener_categorias_usuario(current_user.id)
    except MySQLError as error:
        flash(f"Error al cargar categorias: {error}", "danger")
        lista_categorias = []

    return render_template("categorias.html", categorias=lista_categorias)


@app.route("/categorias/nueva", methods=["POST"])
@login_required
def nueva_categoria():
    nombre = request.form.get("nombre", "").strip()
    color = request.form.get("color", "#6c757d").strip()

    if not nombre:
        flash("El nombre de la categoria es obligatorio.", "warning")
        return redirect(url_for("categorias"))

    try:
        categoria = Categoria(nombre=nombre, color=color, usuario_id=current_user.id)
        db.crear_categoria(categoria)
        flash(f'Categoria "{nombre}" creada exitosamente.', "success")
    except MySQLError as error:
        flash(f"Error al crear categoria: {error}", "danger")

    return redirect(url_for("categorias"))


@app.route("/categorias/<int:categoria_id>/eliminar", methods=["POST"])
@login_required
def eliminar_categoria(categoria_id: int):
    try:
        eliminada = db.eliminar_categoria(categoria_id, current_user.id)
        if eliminada:
            flash("Categoria eliminada. Las tareas asociadas quedan sin categoria.", "success")
        else:
            flash("No se encontro la categoria.", "warning")
    except MySQLError as error:
        flash(f"Error al eliminar categoria: {error}", "danger")

    return redirect(url_for("categorias"))


@app.route("/horario/guardar", methods=["POST"])
@login_required
def guardar_horario():
    horario_base = request.form.get("horario_base", "").strip()
    contexto_horario = request.form.get("contexto_horario", "").strip() or None

    try:
        db.guardar_horario_usuario(current_user.id, horario_base, contexto_horario)
        flash("Horario guardado correctamente.", "success")
    except MySQLError as error:
        flash(f"Error al guardar el horario: {error}", "danger")

    return redirect(url_for("index"))


# ---------------------------------------------------------------------------
# Planificacion con IA
# ---------------------------------------------------------------------------

@app.route("/plan")
@login_required
def plan():
    try:
        tareas_pendientes = db.obtener_tareas_pendientes_para_plan(current_user.id)
    except MySQLError as error:
        flash(f"Error al cargar tareas: {error}", "danger")
        tareas_pendientes = []

    try:
        horario_usuario = db.obtener_horario_usuario(current_user.id)
    except MySQLError as error:
        flash(f"Error al cargar el horario: {error}", "danger")
        horario_usuario = HorarioUsuario(usuario_id=current_user.id)

    return render_template(
        "plan.html",
        tareas=tareas_pendientes,
        plan_generado=session.get("plan_texto"),
        horario_usuario=horario_usuario,
        chat_historial=session.get("plan_chat", []),
    )


@app.route("/plan/generar", methods=["POST"])
@login_required
def generar_plan():
    try:
        tareas = db.obtener_tareas_pendientes_para_plan(current_user.id)
    except MySQLError as error:
        flash(f"Error al obtener tareas: {error}", "danger")
        return redirect(url_for("plan"))

    if not tareas:
        flash("No tienes tareas pendientes para planificar.", "info")
        return redirect(url_for("plan"))

    descripcion_tareas = _construir_descripcion_tareas(tareas)
    try:
        horario_usuario = db.obtener_horario_usuario(current_user.id)
    except MySQLError as error:
        flash(f"Error al obtener el horario: {error}", "danger")
        return redirect(url_for("plan"))

    try:
        cliente_ia = _obtener_cliente_ia()
        hoy = date.today().strftime("%d/%m/%Y")
        contexto_disponibilidad = _construir_contexto_disponibilidad(
            horario_base=horario_usuario.horario_base,
            contexto_horario=horario_usuario.contexto_horario or "",
        )

        prompt = f"""Eres un asistente de productividad. Hoy es {hoy}.

El usuario tiene las siguientes tareas pendientes:
{descripcion_tareas}

Disponibilidad horaria del usuario:
{contexto_disponibilidad}

Genera un plan de trabajo estructurado que incluya:
1. Un resumen breve de la situacion actual
2. Un orden de prioridad recomendado con justificacion
3. Sugerencias de agrupacion por categoria o tipo
4. Estimacion de tiempo por tarea (si es posible inferirla)
5. Si el usuario dio un horario, detecta huecos realistas dentro de ese horario para avanzar tareas
6. Recomendaciones practicas para completar las tareas

Usa formato Markdown con encabezados y listas. Se conciso y practico."""

        respuesta = cliente_ia.messages.create(
            model="claude-opus-4-6",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        plan_texto = respuesta.content[0].text
        session['plan_texto'] = plan_texto
        session['plan_chat'] = [{"role": "assistant", "content": plan_texto}]
        return render_template(
            "plan.html",
            tareas=tareas,
            plan_generado=plan_texto,
            horario_usuario=horario_usuario,
            chat_historial=session.get("plan_chat", []),
        )

    except anthropic.AuthenticationError:
        flash("Error de autenticacion con la IA. Verifica la variable ANTHROPIC_API_KEY.", "danger")
    except anthropic.APIConnectionError:
        flash("No se pudo conectar con la IA. Verifica tu conexion a internet.", "danger")
    except anthropic.RateLimitError:
        flash("Limite de uso de IA alcanzado. Intenta mas tarde.", "warning")
    except anthropic.APIStatusError as error:
        flash(f"Error de la API de IA (codigo {error.status_code}).", "danger")
    except Exception as error:
        flash(f"Error inesperado al generar el plan: {error}", "danger")

    return redirect(url_for("plan"))


@app.route("/plan/chat", methods=["POST"])
@login_required
def chat_plan():
    """Continua la conversacion con Claude sobre el plan generado."""
    mensaje = request.form.get("mensaje", "").strip()
    if not mensaje:
        flash("Escribe un mensaje para continuar.", "warning")
        return redirect(url_for("plan"))

    historial = session.get("plan_chat", [])
    if not historial:
        flash("Primero genera un plan antes de chatear.", "warning")
        return redirect(url_for("plan"))

    historial.append({"role": "user", "content": mensaje})

    try:
        cliente_ia = _obtener_cliente_ia()
        respuesta = cliente_ia.messages.create(
            model="claude-opus-4-6",
            max_tokens=1000,
            system="Eres un asistente de productividad. Ayudas al usuario a refinar su plan de trabajo. Se conciso y practico.",
            messages=historial,
        )
        respuesta_texto = respuesta.content[0].text
        historial.append({"role": "assistant", "content": respuesta_texto})
        session["plan_chat"] = historial
        session.modified = True

    except anthropic.AuthenticationError:
        flash("Error de autenticacion con la IA.", "danger")
        return redirect(url_for("plan"))
    except Exception as error:
        flash(f"Error al chatear con la IA: {error}", "danger")
        return redirect(url_for("plan"))

    try:
        tareas = db.obtener_tareas_pendientes_para_plan(current_user.id)
        horario_usuario = db.obtener_horario_usuario(current_user.id)
    except MySQLError:
        tareas = []
        horario_usuario = HorarioUsuario(usuario_id=current_user.id)

    return render_template(
        "plan.html",
        tareas=tareas,
        plan_generado=session.get("plan_texto"),
        horario_usuario=horario_usuario,
        chat_historial=historial,
    )


# ---------------------------------------------------------------------------
# Funciones auxiliares privadas
# ---------------------------------------------------------------------------

def _obtener_categorias_usuario() -> list:
    """Obtiene las categorias del usuario actual, retorna lista vacia en caso de error."""
    try:
        return db.obtener_categorias_usuario(current_user.id)
    except MySQLError:
        return []


def _parsear_fecha(fecha_str: Optional[str]):
    """Convierte string 'YYYY-MM-DD' a objeto date, o retorna None."""
    if not fecha_str:
        return None
    try:
        return datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except ValueError:
        return None


def _construir_descripcion_tareas(tareas: list) -> str:
    """Formatea la lista de tareas para incluirla en el prompt de IA."""
    hoy = date.today()
    lineas = []
    for i, tarea in enumerate(tareas, 1):
        linea = f"{i}. **{tarea.titulo}** (Prioridad: {tarea.prioridad.upper()})"
        if tarea.nombre_categoria:
            linea += f" - Categoria: {tarea.nombre_categoria}"
        if tarea.fecha_limite:
            dias = (tarea.fecha_limite - hoy).days
            if dias < 0:
                linea += f" - VENCIDA hace {abs(dias)} dias"
            elif dias == 0:
                linea += f" - Vence HOY"
            else:
                linea += f" - Vence en {dias} dias ({tarea.fecha_limite.strftime('%d/%m/%Y')})"
        if tarea.descripcion:
            linea += f"\n   Descripcion: {tarea.descripcion}"
        lineas.append(linea)
    return "\n".join(lineas)


def _construir_contexto_disponibilidad(
    horario_base: str,
    contexto_horario: str,
) -> str:
    """Resume la disponibilidad opcional del usuario para el prompt."""
    partes = []

    if horario_base:
        partes.append(f"- Horario del usuario:\n{horario_base}")

    if contexto_horario:
        partes.append(f"- Contexto adicional sobre energia o rutina: {contexto_horario}")

    if not partes:
        return "- No se proporciono horario. No inventes bloques ni horas exactas."

    partes.append("- Usa este horario para detectar huecos aprovechables sin asumir datos no dados.")
    return "\n".join(partes)


def _renderizar_index_con_modal_nueva(
    tarea: Tarea,
    categorias: list,
    filtro_estado: Optional[str] = None,
):
    """Re-renderiza el inicio manteniendo abierto el modal de nueva tarea."""
    if filtro_estado not in (None, "pendiente", "completada"):
        filtro_estado = None

    try:
        tareas = db.obtener_todas_las_tareas(current_user.id, filtro_estado)
    except MySQLError:
        tareas = []

    try:
        horario_usuario = db.obtener_horario_usuario(current_user.id)
    except MySQLError:
        horario_usuario = HorarioUsuario(usuario_id=current_user.id)

    return render_template(
        "index.html",
        tareas=tareas,
        filtro_activo=filtro_estado,
        categorias=categorias,
        horario_usuario=horario_usuario,
        tarea_modal=tarea,
        mostrar_modal_nueva=True,
    )


def _obtener_cliente_ia() -> anthropic.Anthropic:
    """Crea el cliente de Anthropic solo si hay una credencial valida."""
    api_key = (os.environ.get("ANTHROPIC_API_KEY") or "").strip()

    # Soporte opcional para entornos que usan auth token en lugar de API key.
    auth_token = (os.environ.get("ANTHROPIC_AUTH_TOKEN") or "").strip()

    if api_key:
        return anthropic.Anthropic(api_key=api_key)

    if auth_token:
        return anthropic.Anthropic(auth_token=auth_token)

    raise ValueError(
        "Falta configurar la credencial de Anthropic. "
        "Define ANTHROPIC_API_KEY o ANTHROPIC_AUTH_TOKEN."
    )


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
