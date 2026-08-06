# Plan de Mejora — Black Bulls Gamestore

## 1. Diagnóstico del código actual

- Todo vive en una sola clase y un solo archivo: interfaz, lógica y "datos" mezclados.
- El login no valida nada, solo cambia de pantalla.
- No hay persistencia: cerrar la app borra cualquier estado.
- Los botones del menú (Descubrir, Tienda, Biblioteca, Comunidad, Ajustes) todos llaman a un mismo `messagebox` de "en construcción".
- No hay modelo de datos: ni usuarios, ni juegos, ni carrito, ni biblioteca.
- El diseño es decente pero genérico (paleta púrpura estándar de "dark UI").

Para que esto sea un proyecto real, hay que resolver **arquitectura + datos + diseño** juntos, no solo maquillar pantallas.

---

## 2. Identidad de marca: Black Bulls Gamestore

Un rediseño coherente con el nombre. En vez del púrpura genérico, algo con carácter "toro / arena / poder":

**Paleta propuesta**
- Fondo principal: `#0a0a0a` (negro casi puro)
- Panel/tarjetas: `#161616` con borde sutil `#2a2a2a`
- Acento primario: `#c9a227` (dorado/ámbar, "cuernos de toro")
- Acento secundario / alertas: `#8b1e1e` (rojo sangre oscuro, usado con moderación)
- Texto principal: `#f5f5f0` (blanco hueso, no blanco puro)
- Texto secundario: `#9a9a9a`

**Tipografía**
- Títulos: una fuente condensada/bold tipo "Bebas Neue" o "Segoe UI Black" (ya usás Black, mantenerlo pero solo en títulos, no en botones)
- Cuerpo: Segoe UI regular/semibold

**Logo e ícono**
- Silueta minimalista de cabeza de toro en dorado sobre negro, o solo un monograma "BB" geométrico si no querés ilustración.

**Principio de diseño**: menos gradientes decorativos, más contraste duro (negro/dorado), bordes finos en vez de sombras, iconografía simple (usar una librería de íconos tipo Feather/Lucide en vez de emojis o texto plano).

---

## 3. Arquitectura técnica (el cambio más importante)

Separar en módulos en vez de una clase gigante:

```
black_bulls_gamestore/
├── main.py                  # solo arranca la app
├── database/
│   └── db.py                 # conexión y queries a SQLite
│   └── black_bulls.db
├── models/
│   ├── usuario.py
│   ├── juego.py
│   └── biblioteca.py
├── views/
│   ├── login_view.py
│   ├── registro_view.py
│   ├── menu_view.py
│   ├── tienda_view.py
│   ├── biblioteca_view.py
│   ├── comunidad_view.py
│   └── ajustes_view.py
├── controllers/
│   └── auth_controller.py    # lógica de login/registro
├── assets/
│   ├── logo.png
│   └── juegos/ (portadas)
└── styles.py                 # colores, fuentes, constantes de diseño
```

**Persistencia recomendada: SQLite** (vía `sqlite3`, ya viene con Python, no requiere instalar nada). Con esto sí podés tener usuarios reales, contraseñas, juegos comprados, etc. Nada de esto sobrevive hoy porque no hay ninguna base de datos ni archivo detrás.

**Tablas mínimas necesarias**
- `usuarios (id, nombre_usuario, password_hash, correo, fecha_registro)`
- `juegos (id, titulo, descripcion, precio, categoria, portada_path)`
- `biblioteca (id, usuario_id, juego_id, fecha_compra)`
- `carrito (id, usuario_id, juego_id)` (opcional, o manejarlo en memoria mientras la sesión está activa)

---

## 4. Pantalla por pantalla: qué debe hacer cada una

### Login
- Validar contra la tabla `usuarios` (nombre + hash de contraseña, usar `hashlib` o `bcrypt`).
- Mostrar error visual si las credenciales fallan (no un popup genérico: un label rojo bajo el campo).
- Link/botón "Crear cuenta" que lleve a Registro.
- Guardar el usuario autenticado en una variable de sesión (`self.usuario_actual`) que todas las demás pantallas puedan leer.

### Registro (pantalla nueva, no existe hoy)
- Formulario: usuario, correo, contraseña, confirmar contraseña.
- Validaciones: usuario no repetido, contraseñas coinciden, campos no vacíos.
- Al crear cuenta, redirige a login o auto-loguea.

### Descubrir
- Grid de juegos destacados leídos desde la tabla `juegos` (no hardcodeados en el código).
- Cada tarjeta con portada, título, precio y botón "Ver más" o "Comprar".

### Tienda
- Listado completo de juegos con filtro por categoría/búsqueda por nombre.
- Botón "Comprar" que inserta una fila en `biblioteca` para el usuario actual (simulación de compra, sin pasarela real).
- Confirmación visual de compra (no solo un messagebox: idealmente un cambio de estado del botón a "Ya en tu biblioteca").

### Biblioteca
- Lista de juegos que el usuario actual ya "compró" (JOIN entre `biblioteca` y `juegos` filtrando por `usuario_id`).
- Si está vacía, mostrar un estado vacío con mensaje ("Aún no tenés juegos") en vez de pantalla en blanco.

### Comunidad
- Puede empezar simple: lista estática de "anuncios" o "eventos" leídos de una tabla `anuncios`, o un espacio de reseñas donde el usuario deja comentarios guardados en SQLite.
- No tiene que ser un chat en tiempo real — con que persista texto ya es funcional y honesto.

### Ajustes
- Mostrar datos del usuario actual (nombre, correo).
- Botón para cambiar contraseña (con validación de la actual).
- Botón "Cerrar sesión" (ya existe, se mantiene).

---

## 5. Mejoras de UX que hoy faltan

- Loading/feedback: ningún botón da feedback visual al hacer clic (aparte del hover). Agregar un pequeño cambio de estado o ícono.
- Manejo de errores visible en pantalla, no solo `messagebox.showinfo`.
- Navegación persistente: la sidebar debería indicar en qué sección estás (resaltar el botón activo).
- Responsive mínimo: al menos evitar que se rompa si el usuario cambia el tamaño de fuente del sistema.

---

## 6. Plan de implementación por fases

**Fase 1 — Base de datos y estructura**
1. Crear `database/db.py` con la conexión SQLite y creación de tablas.
2. Reorganizar el proyecto en los módulos de la sección 3.
3. Insertar datos de prueba (usuarios y juegos) para poder probar sin registro manual.

**Fase 2 — Autenticación real**
4. Implementar registro funcional.
5. Implementar login validando contra la base de datos con hash de contraseña.
6. Manejo de sesión (`usuario_actual`) compartido entre vistas.

**Fase 3 — Rediseño visual**
7. Crear `styles.py` con la nueva paleta e implementar el rebranding a Black Bulls Gamestore (logo, tipografía, colores).
8. Aplicar el nuevo estilo a login y menú antes de tocar el resto, para validar el look completo primero.

**Fase 4 — Pantallas funcionales**
9. Tienda (listado + compra).
10. Biblioteca (listado de comprados).
11. Descubrir (destacados).
12. Comunidad y Ajustes.

**Fase 5 — Pulido**
13. Estados vacíos, mensajes de error en pantalla, feedback de botones.
14. Pruebas con 2-3 usuarios de prueba distintos para confirmar que cada uno ve solo su propia biblioteca.

---

## 7. Siguiente paso sugerido

Lo más eficiente es arrancar por la **Fase 1**, porque todo lo demás depende de tener la base de datos lista. Si querés, en el próximo mensaje puedo escribirte directamente el código de `database/db.py` con la creación de tablas y datos de prueba, o si preferís empezar por el rediseño visual del login con la nueva paleta, también podemos ir por ahí primero.
