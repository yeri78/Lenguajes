# Guía de trabajo en equipo (4 personas × 3 lenguajes)

Cada integrante debe hacer **commits en los tres lenguajes**. Propuesta: cada persona es dueña de un bloque de módulos
y lo implementa/revisa en Python, JavaScript y Java (3 commits mínimos por persona).

| Integrante | Bloque | Python | JavaScript | Java |
|---|---|---|---|---|
| A | Modelos y validación | `validacion.py`, `modelos.py` | `validacion.js`, `modelos.js` | `Validacion`, `Constantes`, `Conexion`, `Vehiculo`, `Solicitud`… |
| B | Grafo y rutas | `grafo.py`, `rutas.py` | `grafo.js`, `rutas.js` | `Grafo`, `Rutas` |
| C | Asignación y estadísticas | `asignacion.py`, `estadisticas.py` | `asignacion.js`, `estadisticas.js` | `Asignacion`, `Estadisticas` |
| D | Datos, concurrencia, CLI, visualización | `datos.py`, `concurrencia.py`, `servicio.py`, `main.py` | `datos.js`, `concurrencia.js`, `trabajador.js`, `main.js` | `Datos`, `Concurrencia`, `Servicio`, `Main` |

Todos: pruebas de su bloque en cada lenguaje y su parte del README/documentación.

## Flujo con Git

```bash
git clone <URL-del-repositorio>
git checkout -b feature/<nombre>-<bloque>        # ej. feature/ana-modelos
# ... trabajar ...
git add python/transporte/modelos.py
git commit -m "feat(python): agrega modelos y validación"
git add javascript/src/modelos.js javascript/src/validacion.js
git commit -m "feat(javascript): agrega modelos y validación"
git add java/src/transporte/Conexion.java java/src/transporte/Validacion.java
git commit -m "feat(java): agrega modelos y validación"
git push -u origin feature/<nombre>-<bloque>
# Abrir Pull Request y pedir revisión a otro integrante
```
