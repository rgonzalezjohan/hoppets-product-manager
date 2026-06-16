import os

from flask import Flask, render_template, request, redirect, session
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

    if not session.get("admin"):
        return redirect("/login")

    productos = get_productos()

    total_activos = len(productos)

    productos_ocultos = get_productos_ocultos()

    total_ocultos = len(productos_ocultos)

    total_productos = total_activos + total_ocultos

    return render_template(
        "admin.html",
        productos=productos,
        total_activos=total_activos,
        total_ocultos=total_ocultos,
        total_productos=total_productos
    )
@app.route("/eliminar/<int:id>")
def eliminar(id):
    if not session.get("admin"):
        return redirect("/login")

    eliminar_producto(id)

    return redirect("/admin")

@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):

    if not session.get("admin"):
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

        return redirect("/admin")

    conn.close()

    return render_template(
        "editar.html",
        producto=producto
    )
@app.route("/agregar", methods=["GET", "POST"])
def agregar():

    if not session.get("admin"):
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

        return redirect("/")

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

    return redirect("/ocultos")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        usuario = request.form["usuario"]
        password = request.form["password"]

        if usuario == "admin" and password == "123456":

            session["usuario"] = usuario

            return redirect("/admin")

    return render_template("login.html")

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)