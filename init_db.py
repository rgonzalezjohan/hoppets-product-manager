import sqlite3

conn = sqlite3.connect("database/products.db")
cursor = conn.cursor()
#cursor.execute("DELETE FROM productos")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    precio INTEGER NOT NULL,
    imagen TEXT NOT NULL,
    activo INTEGER DEFAULT 1
)
""")
try:
    cursor.execute("""
        ALTER TABLE productos
        ADD COLUMN activo INTEGER DEFAULT 1
    """)
except:
    pass

#cursor.execute("""
#INSERT INTO productos (nombre, descripcion, precio, imagen)
#VALUES
#('Bandanas',
 #'Diseños personalizados para perros y gatos',
 #12000,
 #'bandana-love.jpeg')
#""")

#cursor.execute("""
#INSERT INTO productos (nombre, descripcion, precio, imagen)
#VALUES
#('Camas',
 #'Camas cómodas y suaves para mascotas',
 #45000,
 #'cama-sandia.jpeg')
#""")

#cursor.execute("""
#INSERT INTO productos (nombre, descripcion, precio, imagen)
#VALUES
#('Accesorios',
 #'Accesorios únicos personalizados',
 #20000,
 #'gato-cama.jpeg')
#""")

#cursor.execute("""
#INSERT INTO productos (nombre, descripcion, precio, imagen)
#VALUES (
    #'Collares',
    #'Collares personalizados para mascotas',
    #15000,
    #'bandana-love.jpeg'
#)
#""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    rol TEXT DEFAULT 'editor'
)
""")

cursor.execute("""
INSERT OR IGNORE INTO usuarios
(usuario, password, rol)
VALUES
('admin', '123456', 'superadmin')
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS configuracion (
    id INTEGER PRIMARY KEY,
    whatsapp TEXT,
    instagram TEXT,
    correo TEXT
)
""")

try:
    cursor.execute("""
        ALTER TABLE configuracion
        ADD COLUMN facebook TEXT
    """)
except:
    pass

try:
    cursor.execute("""
        ALTER TABLE configuracion
        ADD COLUMN ciudad TEXT
    """)
except:
    pass

try:
    cursor.execute("""
        ALTER TABLE configuracion
        ADD COLUMN mensaje_contacto TEXT
    """)
except:
    pass

cursor.execute("""
INSERT OR IGNORE INTO configuracion
(
    id,
    whatsapp,
    instagram,
    correo,
    facebook,
    ciudad,
    mensaje_contacto
)
VALUES
(
    1,
    '573108998430',
    '@hoppets_col',
    'contacto@hoppets.com',
    'Hoppets Colombia',
    'Cali, Colombia',
    'Accesorios personalizados para mascotas felices 🐾'
)
""")

conn.commit()
conn.close()



print("Base de datos creada correctamente.")