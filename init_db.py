import sqlite3

conn = sqlite3.connect("database/products.db")
cursor = conn.cursor()
cursor.execute("DELETE FROM productos")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    precio INTEGER NOT NULL,
    imagen TEXT NOT NULL
)
""")

cursor.execute("""
INSERT INTO productos (nombre, descripcion, precio, imagen)
VALUES
('Bandanas',
 'Diseños personalizados para perros y gatos',
 12000,
 'bandana-love.jpeg')
""")

cursor.execute("""
INSERT INTO productos (nombre, descripcion, precio, imagen)
VALUES
('Camas',
 'Camas cómodas y suaves para mascotas',
 45000,
 'cama-sandia.jpeg')
""")

cursor.execute("""
INSERT INTO productos (nombre, descripcion, precio, imagen)
VALUES
('Accesorios',
 'Accesorios únicos personalizados',
 20000,
 'gato-cama.jpeg')
""")

cursor.execute("""
INSERT INTO productos (nombre, descripcion, precio, imagen)
VALUES (
    'Collares',
    'Collares personalizados para mascotas',
    15000,
    'bandana-love.jpeg'
)
""")


conn.commit()
conn.close()

print("Base de datos creada correctamente.")