package transporte;

// Responsable: Integrante 1 (modelos y validación)

public class Vehiculo {
    private final String id;
    private final String tipo;
    private final int capacidad;
    private final String conductor;
    private String estado;

    public Vehiculo(String id, String tipo, int capacidad, String estado) {
        this(id, tipo, capacidad, estado, "Sin conductor");
    }

    public Vehiculo(String id, String tipo, int capacidad, String estado, String conductor) {
        this.id = id;
        this.tipo = tipo;
        this.capacidad = capacidad;
        this.estado = estado;
        this.conductor = conductor;
    }

    public static Vehiculo desdeFila(Fila fila) {
        return new Vehiculo(Validacion.requerirTexto(fila, "id"), Validacion.requerirTexto(fila, "tipo"),
                Validacion.requerirEntero(fila, "capacidad"),
                Validacion.requerirOpcion(fila, "estado", Constantes::esEstadoVehiculo, "DISPONIBLE, OCUPADO"),
                fila.obtenerOpcional("conductor", "Sin conductor"));
    }

    public String id() { return id; }
    public String tipo() { return tipo; }
    public int capacidad() { return capacidad; }
    public String conductor() { return conductor; }
    public String estado() { return estado; }
    public boolean disponible() { return "DISPONIBLE".equals(estado); }
    public void ocupar() { estado = "OCUPADO"; }
    public void liberar() { estado = "DISPONIBLE"; }
}