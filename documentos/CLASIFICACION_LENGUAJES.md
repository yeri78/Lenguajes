# Clasificación de los lenguajes

Las categorías de tipado y ejecución dependen del contexto (implementación, versión, herramientas); abajo se indica el matiz.

| Criterio | Python (CPython 3) | JavaScript (Node.js / V8) | Java (JDK 17+) |
|---|---|---|---|
| **a. Abstracción** | Alto nivel | Alto nivel | Alto nivel (más cercano a medio que los otros dos por su tipado y modelo de memoria explícito) |
| **b. Ejecución** | Interpretado: se compila a *bytecode* y lo ejecuta la VM de CPython | Interpretado con compilación JIT en el motor V8 | Compilado a *bytecode* y **ejecutado en máquina virtual** (JVM con JIT) |
| **c. Tipos** | Dinámico y **fuerte** (no mezcla `"5" + 5`; admite *type hints* opcionales) | Dinámico y **débil** (coerción implícita: `"5" + 5 === "55"`) | Estático y **fuerte** (verificación al compilar; genéricos con borrado de tipos) |
| **d. Propósito** | General; análisis de datos; automatización; web (Django/Flask) | Desarrollo web (cliente y servidor); automatización de herramientas; servicios (Node) | General; sistemas y servicios empresariales; aplicaciones móviles (Android) |
| **e. Paradigma principal** | Orientado a objetos / imperativo | Orientado a eventos (asíncrono) con funciones de primera clase | Orientado a objetos |
| **Paradigmas secundarios** | Funcional, concurrente | Funcional, imperativo, OO basado en prototipos | Funcional (lambdas, `Predicate`, `Comparator`), concurrente, imperativo |
| **f. Tipo** | Multiparadigma | Multiparadigma, orientado a eventos | Orientado a objetos (con rasgos funcionales y concurrentes) |

## Evidencia en el código de este proyecto

| Paradigma | Python | JavaScript | Java |
|---|---|---|---|
| Orientado a objetos | `@dataclass Conexion`, `class ListaEnlazada`, `class Red` | `class ListaEnlazada`, `class Red`, `class Conexion` (azúcar sobre prototipos) | `record Conexion`, `class ListaEnlazada<T>`, `class Red` |
| Funcional | `sorted(key=lambda …)`, `filtrar`/`transformar` de `ListaEnlazada` | `.filter().map().reduce()` en `estadisticas.js` | `ListaEnlazada.filtrar(...)`, `minimo(Comparator…)`, lambdas |
| Imperativo | Bucle `while` de la búsqueda de ruta, recursión para todas las rutas | Bucle `while` de la búsqueda de ruta | Bucle `while` con `ColaPrioridad` |
| Concurrente | `ThreadPoolExecutor.map` (hilos con GIL) | `Worker` de `worker_threads` + `Promise.all` | `ExecutorService.invokeAll` |
| Orientado a eventos | — | `worker.once('message', …)`, promesas | — |
| Textual (entrada/salida) | CSV con `csv` | CSV con `fs` | CSV con `Files` |

Lenguajes **no** aplicables aquí: *numéricos* (no se usan cálculos científicos especializados) y *lineales/secuenciales* puros
(ninguno lo es, aunque `main` se ejecuta de forma secuencial). *Declarativo* solo parcialmente: SQL/HTML/CSS no se usan; los
pipelines funcionales son declarativos en estilo.
