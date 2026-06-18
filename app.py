import os

from flask import Flask, render_template, request, redirect, session, flash
import os
import sqlite3

app = Flask(__name__)
app.secret_key = "hoppets_admin_2025"

UPLOAD_FOLDER = "static/uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def get_productos():

    conn = sqlite3.connect("database/products.db")
    conn.row_factory = sqlite3.Row

    productos = conn.execute(
    """
    SELECT * FROM productos
    WHERE activo = 1
    """
).fetchall()
    conn.close()

    return productos
def get_productos_ocultos():

    conn = sqlite3.connect("database/products.db")
    conn.row_factory = sqlite3.Row

    productos = conn.execute(
        """
        SELECT * FROM productos
        WHERE activo = 0
        """
    ).fetchall()

    conn.close()

    return productos

def total_usuarios():

    conn = sqlite3.connect("database/products.db")

    total = conn.execute(
        "SELECT COUNT(*) FROM usuarios"
    ).fetchone()[0]

    conn.close()

    return total


def total_superadmins():

    conn = sqlite3.connect("database/products.db")

    total = conn.execute(
        """
        SELECT COUNT(*)
        FROM usuarios
        WHERE rol = 'superadmin'
        """
    ).fetchone()[0]

    conn.close()

    return total


def total_editores():

    conn = sqlite3.connect("database/products.db")

    total = conn.execute(
        """
        SELECT COUNT(*)
        FROM usuarios
        WHERE rol = 'editor'
        """
    ).fetchone()[0]

    conn.close()

    return total

def get_usuarios():

    conn = sqlite3.connect("database/products.db")
    conn.row_factory = sqlite3.Row

    usuarios = conn.execute(
    """
    SELECT id, usuario, rol
    FROM usuarios
    ORDER BY usuario
    """
).fetchall()

    conn.close()

    return usuarios

def obtener_rol(usuario):

    conn = sqlite3.connect("database/products.db")
    conn.row_factory = sqlite3.Row

    resultado = conn.execute(
        """
        SELECT rol
        FROM usuarios
        WHERE usuario = ?
        """,
        (usuario,)
    ).fetchone()

    conn.close()

    if resultado:
        return resultado["rol"]

    return None

def crear_usuario(usuario, password):

    conn = sqlite3.connect("database/products.db")

    conn.execute(
        """
        INSERT INTO usuarios
        (usuario, password, rol)
        VALUES (?, ?, ?)
        """,
        (usuario, password, rol)
    )

    conn.commit()
    conn.close()

def eliminar_usuario(id):

    conn = sqlite3.connect("database/products.db")
    conn.row_factory = sqlite3.Row

    usuario = conn.execute(
        """
        SELECT usuario
        FROM usuarios
        WHERE id = ?
        """,
        (id,)
    ).fetchone()

    if not usuario:
        conn.close()
        return

    # No permitir borrar admin
    if usuario["usuario"] == "admin":
        conn.close()
        return

    # No permitir borrarse a sí mismo
    if usuario["usuario"] == session.get("usuario"):
        conn.close()
        return

    conn.execute(
        """
        DELETE FROM usuarios
        WHERE id = ?
        """,
        (id,)
    )

    conn.commit()
    conn.close()

def cambiar_password(id, password):

    conn = sqlite3.connect("database/products.db")

    conn.execute(
        """
        UPDATE usuarios
        SET password = ?
        WHERE id = ?
        """,
        (password, id)
    )

    conn.commit()
    conn.close()

def agregar_producto(nombre, descripcion, precio, imagen):

    conn = sqlite3.connect("database/products.db")

    conn.execute(
        """
        INSERT INTO productos
        (nombre, descripcion, precio, imagen)
        VALUES (?, ?, ?, ?)
        """,
        (nombre, descripcion, precio, imagen)
    )

    conn.commit()
    conn.close()

def eliminar_producto(id):

    conn = sqlite3.connect("database/products.db")

    conn.execute(
    """
    UPDATE productos
    SET activo = 0
    WHERE id = ?
    """,
    (id,)
)

    conn.commit()
    conn.close()

def restaurar_producto(id):

    conn = sqlite3.connect("database/products.db")

    conn.execute(
        """
        UPDATE productos
        SET activo = 1
        WHERE id = ?
        """,
        (id,)
    )

    conn.commit()
    conn.close()

@app.route("/")
def home():

    productos = get_productos()

    return render_template(
        "index.html",
        productos=productos
    )

@app.route("/admin")
def admin():

    if not session.get("usuario"):
        return redirect("/login")

    productos = get_productos()
    total_activos = len(productos)

    productos_ocultos = get_productos_ocultos()
    total_ocultos = len(productos_ocultos)

    total_productos = total_activos + total_ocultos

    total_usuarios_sistema = total_usuarios()
    total_superadmins_sistema = total_superadmins()
    total_editores_sistema = total_editores()

    usuario_actual = session.get("usuario")

    conn = sqlite3.connect("database/products.db")
    conn.row_factory = sqlite3.Row

    usuario_info = conn.execute(
        """
        SELECT rol
        FROM usuarios
        WHERE usuario = ?
        """,
        (usuario_actual,)
    ).fetchone()

    conn.close()

    rol_actual = usuario_info["rol"]

    return render_template(
        "admin.html",
        productos=productos,
        total_activos=total_activos,
        total_ocultos=total_ocultos,
        total_productos=total_productos,
        total_usuarios=total_usuarios_sistema,
        total_superadmins=total_superadmins_sistema,
        total_editores=total_editores_sistema,
        usuario_actual=usuario_actual,
        rol_actual=rol_actual
    )
@app.route("/eliminar/<int:id>")
def eliminar(id):
    if not session.get("usuario"):
        return redirect("/login")

    eliminar_producto(id)

    flash("🗑️ Producto eliminado correctamente", "success")

    return redirect("/admin")

@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):

    if not session.get("usuario"):
        return redirect("/login")

    conn = sqlite3.connect("database/products.db")
    conn.row_factory = sqlite3.Row

    producto = conn.execute(
        "SELECT * FROM productos WHERE id = ?",
        (id,)
    ).fetchone()

    if request.method == "POST":

        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]
        precio = request.form["precio"]

        archivo = request.files["imagen"]

        # Mantener imagen actual por defecto
        nombre_imagen = producto["imagen"]

        # Si el usuario seleccionó una nueva imagen
        if archivo and archivo.filename != "":

            nombre_imagen = archivo.filename

            archivo.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    nombre_imagen
                )
            )

        conn.execute(
            """
            UPDATE productos
            SET nombre = ?,
                descripcion = ?,
                precio = ?,
                imagen = ?
            WHERE id = ?
            """,
            (
                nombre,
                descripcion,
                precio,
                nombre_imagen,
                id
            )
        )

        conn.commit()
        conn.close()

        flash("✏️ Producto actualizado correctamente", "success")

        return redirect("/admin")

    conn.close()

    return render_template(
        "editar.html",
        producto=producto
    )
@app.route("/agregar", methods=["GET", "POST"])
def agregar():

    if not session.get("usuario"):
        return redirect("/login")

    if request.method == "POST":

        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]
        precio = request.form["precio"]

        archivo = request.files["imagen"]

        nombre_imagen = archivo.filename

        archivo.save(
            os.path.join(
                app.config["UPLOAD_FOLDER"],
                nombre_imagen
            )
        )

        agregar_producto(
            nombre,
            descripcion,
            precio,
            nombre_imagen
        )

        flash(
    "✅ Producto agregado correctamente",
    "success"
     )

        return redirect("/admin")

    return render_template("agregar.html")

@app.route("/ocultos")
def ocultos():

    if "usuario" not in session:
        return redirect("/login")

    productos = get_productos_ocultos()

    return render_template(
        "ocultos.html",
        productos=productos
    )

@app.route("/restaurar/<int:id>")
def restaurar(id):

    if "usuario" not in session:
        return redirect("/login")

    restaurar_producto(id)

    flash("♻️ Producto restaurado correctamente", "success")

    return redirect("/admin")

@app.route("/usuarios")
def usuarios():

    if not session.get("usuario"):
        return redirect("/login")

    rol = obtener_rol(session.get("usuario"))

    if rol != "superadmin":
        return redirect("/admin")

    usuarios = get_usuarios()

    return render_template(
        "usuarios.html",
        usuarios=usuarios,
        rol_actual=rol
    )

@app.route("/cambiar_rol/<int:id>")
def cambiar_rol(id):

    if not session.get("usuario"):
        return redirect("/login")

    if obtener_rol(session.get("usuario")) != "superadmin":
        return redirect("/admin")

    conn = sqlite3.connect("database/products.db")
    conn.row_factory = sqlite3.Row

    usuario = conn.execute(
        """
        SELECT *
        FROM usuarios
        WHERE id = ?
        """,
        (id,)
    ).fetchone()

    if usuario["usuario"] == "admin":
        conn.close()
        return redirect("/usuarios")

    nuevo_rol = (
        "editor"
        if usuario["rol"] == "superadmin"
        else "superadmin"
    )

    conn.execute(
        """
        UPDATE usuarios
        SET rol = ?
        WHERE id = ?
        """,
        (nuevo_rol, id)
    )

    conn.commit()
    conn.close()

    flash("🔄 Rol actualizado correctamente", "success")

    return redirect("/usuarios")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        usuario = request.form["usuario"]
        password = request.form["password"]

        conn = sqlite3.connect("database/products.db")
        conn.row_factory = sqlite3.Row

        usuario_db = conn.execute(
            """
            SELECT * FROM usuarios
            WHERE usuario = ?
            AND password = ?
            """,
            (usuario, password)
        ).fetchone()

        conn.close()

        if usuario_db:

            session["usuario"] = usuario_db["usuario"]
            session["rol"] = usuario_db["rol"]

            flash(
                "✅ Bienvenido al panel administrativo",
                "success"
            )

            return redirect("/admin")

        else:

            flash(
                "❌ Usuario o contraseña incorrectos",
                "error"
            )

    return render_template("login.html")

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "✅ Sesión cerrada correctamente",
        "success"
    )

    return redirect("/login")

@app.route("/crear_usuario", methods=["GET", "POST"])
def crear_usuario_web():

    if not session.get("usuario"):
        return redirect("/login")

    rol = obtener_rol(session.get("usuario"))

    if rol != "superadmin":
        return redirect("/admin")

    if request.method == "POST":

        usuario = request.form["usuario"]
        password = request.form["password"]
        rol = request.form["rol"]

        crear_usuario(usuario,password,rol)

        flash("👤 Usuario creado correctamente", "success")

        return redirect("/usuarios")

    return render_template("crear_usuario.html")

@app.route("/password/<int:id>", methods=["GET", "POST"])
def password(id):

    if not session.get("usuario"):
        return redirect("/login")

    rol = obtener_rol(session.get("usuario"))

    if rol != "superadmin":
        return redirect("/admin")

    conn = sqlite3.connect("database/products.db")
    conn.row_factory = sqlite3.Row

    usuario = conn.execute(
        "SELECT * FROM usuarios WHERE id = ?",
        (id,)
    ).fetchone()

    if request.method == "POST":

        nueva_password = request.form["password"]

        cambiar_password(id, nueva_password)

        conn.close()

        flash("🔑 Contraseña actualizada correctamente", "success")

        return redirect("/usuarios")

    conn.close()

    return render_template(
        "password.html",
        usuario=usuario
    )

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )