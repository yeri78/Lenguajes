package transporte;

// Responsable: Integrante 3 (red, rutas y estadísticas)

/**
 Red de transporte guardada en 2  listas enlazadas: ubicaciones y conexiones. 
 conexión se guarda una sola vez y se puede recorrer en ambos sentidos.
 */
public class Red {
    private final ListaEnlazada<Ubicacion> ubicaciones = new ListaEnlazada<>();
    private ListaEnlazada<Conexion> conexiones = new ListaEnlazada<>();

    public void registrarUbicacion(Ubicacion ubicacion) {
        if (existe(ubicacion.id())) {
            throw new DatosInvalidosException("Ubicacion duplicada: " + ubicacion.id());
        }
        ubicaciones.agregarFinal(ubicacion);
    }

    public void registrarConexion(Conexion conexion) {
        validarUbicacion(conexion.origen());
        validarUbicacion(conexion.destino());
        if (buscarConexion(conexion.origen(), conexion.destino()) != null) {
            throw new DatosInvalidosException("Conexión duplicada: " + conexion.origen() + "-" + conexion.destino());
        }
        conexiones.agregarFinal(conexion);
    }

    public boolean existe(String id) {
        return ubicaciones.contiene(u -> u.id().equals(id));
    }

    public void validarUbicacion(String id) {
        if (!existe(id)) {
            throw new DatosInvalidosException("Ubicación desconocida: " + id);
        }
    }

    /** Conexión entre a y b orientada de a hacia b, o null si no existe. */
    public Conexion buscarConexion(String a, String b) {
        for (Conexion c : conexiones) {
            if (c.origen().equals(a) && c.destino().equals(b)) {
                return c;
            }
            if (c.origen().equals(b) && c.destino().equals(a)) {
                return c.invertida();
            }
        }
        return null;
    }

    /** Conexiones que salen de la ubicación, todas orientadas desde ella. */
    public ListaEnlazada<Conexion> vecinos(String id) {
        ListaEnlazada<Conexion> salientes = new ListaEnlazada<>();
        for (Conexion c : conexiones) {
            if (c.origen().equals(id)) {
                salientes.agregarFinal(c);
            } else if (c.destino().equals(id)) {
                salientes.agregarFinal(c.invertida());
            }
        }
        return salientes;
    }

    /** Cambia el nivel de tráfico de un tramo (en ambos sentidos). */
    public void cambiarTrafico(String a, String b, String nuevoTrafico) {
        if (!Constantes.esTrafico(nuevoTrafico)) {
            throw new DatosInvalidosException("Trafico invalido: " + nuevoTrafico + ". Opciones: BAJO, MEDIO, ALTO");
        }
        if (buscarConexion(a, b) == null) {
            throw new DatosInvalidosException("No existe conexion entre " + a + " y " + b);
        }
        conexiones = conexiones.transformar(c -> unen(c, a, b)
                ? new Conexion(c.origen(), c.destino(), c.distanciaKm(), nuevoTrafico, c.peaje()) : c);
    }

    private static boolean unen(Conexion c, String a, String b) {
        return (c.origen().equals(a) && c.destino().equals(b)) || (c.origen().equals(b) && c.destino().equals(a));
    }

    public ListaEnlazada<Ubicacion> ubicaciones() {
        return ubicaciones;
    }

    public ListaEnlazada<Conexion> conexiones() {
        return conexiones;
    }
}