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

Cada fase es entregable por sí sola: al terminarla la app debe seguir arrancando y ser testeable. Las dependencias entre fases se indican al final de cada una.

### Fase 1 — Base de datos y estructura

**Objetivo**: tener la estructura modular y una base de datos persistente con datos de prueba, sin tocar la UI actual.

**Tareas**
1.1. Reorganizar el proyecto en el paquete `black_bulls_gamestore/` según el árbol de la sección 3 (`database/`, `models/`, `views/`, `controllers/`, `assets/`, `styles.py`, `main.py`).
1.2. Crear `database/db.py`:
- Conexión SQLite (`sqlite3`) con la ruta `database/black_bulls.db`.
- Función `crear_tablas()` con las tablas mínimas: `usuarios`, `juegos`, `biblioteca`, `carrito` (y `reseñas`, reservada para la Fase 4).
- Función `seed()` que inserta datos de prueba: 1–2 usuarios y ~8–10 juegos con categorías y precios.
- Bloque `if __name__ == "__main__":` que crea tablas + seed y permite correrlo como script.
1.3. Crear `styles.py` con las constantes de la nueva paleta Black Bulls (fondo `#0a0a0a`, panel `#161616`, borde `#2a2a2a`, dorado `#c9a227`, rojo `#8b1e1e`, texto `#f5f5f0`, texto secundario `#9a9a9a`) y las constantes de fuente.

**Criterios de aceptación**
- `python database/db.py` genera `black_bulls.db` con las tablas y el seed cargado (verificable con un `SELECT`).
- El `main.py` actual sigue funcionando sin cambios (la migración a vistas nuevas llega en la Fase 2+).

**Dependencias**: ninguna (es la base de todo lo demás).

### Fase 2 — Autenticación real

**Objetivo**: que login y registro validen contra la base de datos con contraseñas hasheadas y sesión persistente en memoria.

**Tareas**
2.1. Crear `models/usuario.py`: entidad `Usuario` + funciones de acceso a DB (buscar por nombre de usuario, buscar por correo, crear).
2.2. Crear `controllers/auth_controller.py`:
- `registrar(nombre, correo, clave)` con validaciones (campos no vacíos, usuario/correo no repetido, formato básico de correo).
- `login(nombre, clave)` con hash de contraseña (sha256 + salt, vía `hashlib`) y devolución del usuario o error.
2.3. Crear `views/login_view.py`: login validando contra la DB; el error se muestra en un label rojo bajo el campo (nada de popups genéricos).
2.4. Crear `views/registro_view.py`: formulario con validaciones visibles en pantalla; al crearse la cuenta redirige a login o auto-loguea.
2.5. Manejo de sesión: variable compartida `usuario_actual` que el menú y las vistas de la Fase 4 puedan leer.
2.6. `main.py` pasa a arrancar la vista de login; el `TiendaJuegos` original queda reemplazado.

**Criterios de aceptación**
- Crear una cuenta, cerrar sesión y volver a entrar con la misma contraseña funciona.
- Contraseña incorrecta muestra el error en pantalla (label rojo), no un `messagebox` de "en construcción".
- El hash en `black_bulls.db` no es legible (no se guarda la clave en texto plano).

**Dependencias**: Fase 1.

### Fase 3 — Rediseño visual

**Objetivo**: rebranding completo a Black Bulls Gamestore aplicado a las pantallas de la Fase 2 antes de construir el resto.

**Tareas**
3.1. Aplicar `styles.py` a login y registro: fondo negro, acento dorado, títulos en fuente bold, bordes finos en vez de sombras.
3.2. Rediseñar el menú/sidebar: logo Black Bulls (monograma "BB" o silueta de toro), colores dorado/negro, tipografía consistente.
3.3. Resaltar la sección activa en la sidebar (botón con acento dorado al estar seleccionada).

**Criterios de aceptación**
- Login, registro y menú se ven coherentes con la marca (punto de decisión: validar el look completo con el usuario antes de continuar).
- La navegación por sidebar sigue funcionando.

**Dependencias**: Fase 2 (aunque el estilo se puede maquetar en paralelo sobre la Fase 2).

### Fase 4 — Pantallas funcionales

**Objetivo**: que las cinco secciones del menú dejen de ser "en construcción" y lean/escriban datos reales.

**Tareas**
4.1. `views/tienda_view.py`: grid de juegos leído de la tabla `juegos`; filtro por categoría y búsqueda por nombre; botón "Comprar" que inserta en `biblioteca` y cambia su estado a "Ya en tu biblioteca".
4.2. `views/biblioteca_view.py`: JOIN entre `biblioteca` y `juegos` filtrando por `usuario_id`; estado vacío con mensaje "Aún no tenés juegos".
4.3. `views/descubrir_view.py` (reemplaza el banner hardcodeado): destacados leídos desde `juegos`, cada tarjeta con portada, título, precio y botón de compra.
4.4. `views/comunidad_view.py`: reseñas/comentarios persistidos en la tabla `reseñas` (por ahora texto que se guarda y se vuelve a mostrar; sin chat en tiempo real).
4.5. `views/ajustes_view.py`: datos del usuario actual (nombre, correo), cambio de contraseña con validación de la actual, y botón "Cerrar sesión".
4.6. Navegación: un único `views/menu_view.py` que conmuta entre las vistas de sección sin recrear la ventana, manteniendo la sidebar persistente.

**Criterios de aceptación**
- Comprar un juego lo agrega a la biblioteca y el botón refleja el cambio.
- Cada usuario ve únicamente sus juegos comprados.
- No queda ningún `messagebox.showinfo` "en construcción".

**Dependencias**: Fases 1 y 2.

### Fase 5 — Pulido

**Objetivo**: cerrar los detalles de UX y validar el comportamiento con múltiples usuarios.

**Tareas**
5.1. Estados vacíos en todas las vistas (biblioteca sin juegos, tienda sin resultados de búsqueda, comunidad sin reseñas).
5.2. Errores siempre en pantalla (labels rojos) y feedback de botones (hover/active y cambio de texto de estado tras la acción).
5.3. Responsive mínimo: que las fuentes sigan al tamaño del sistema y que las vistas no se rompan al redimensionar.
5.4. Prueba multi-usuario: crear 2–3 cuentas de prueba y confirmar que cada una ve solo su propia biblioteca.
5.5. Revisión final: eliminar código muerto del `main.py` original, confirmar que la DB se crea desde cero en otra máquina y actualizar capturas de pantalla/README si aplica.

**Criterios de aceptación**
- La app se puede probar de principio a fin: registro → login → comprar → biblioteca → cerrar sesión → reingreso.
- Sin excepciones ni pantallas en blanco en ninguno de los flujos anteriores.

**Dependencias**: Fases 1 a 4.

---

## 7. Siguiente paso sugerido

Lo más eficiente es arrancar por la **Fase 1**, porque todo lo demás depende de tener la base de datos lista. Si querés, en el próximo mensaje puedo escribirte directamente el código de `database/db.py` con la creación de tablas y datos de prueba, o si preferís empezar por el rediseño visual del login con la nueva paleta, también podemos ir por ahí primero.
