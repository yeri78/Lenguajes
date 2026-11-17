package transporte;

import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.FlowLayout;
import java.awt.GridLayout;
import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JComboBox;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JSpinner;
import javax.swing.JTabbedPane;
import javax.swing.JTable;
import javax.swing.JTextArea;
import javax.swing.SpinnerNumberModel;
import javax.swing.SwingUtilities;
import javax.swing.UIManager;
import javax.swing.table.DefaultTableModel;

// Responsable: Integrante 4 (asignación, datos y CLI)

/**
 * Ventana gráfica (Swing) del sistema de transporte.
 * Se abre con: java -cp out transporte.Ventana (desde la carpeta java/).
 * Solo dibuja y pide datos; la lógica está en VentanaLogica (listas enlazadas y reglas del proyecto).
 */
public class Ventana {
    private static final String[] PRIORIDADES = {"CRITICA", "ALTA", "MEDIA", "BAJA"};
    private static final String[] TRAFICOS = {"BAJO", "MEDIO", "ALTO"};

    private final VentanaLogica logica = new VentanaLogica();
    private final JPanel raiz = new JPanel(new BorderLayout());

    private final JComboBox<String> comboOrigen = new JComboBox<>();
    private final JComboBox<String> comboDestino = new JComboBox<>();
    private final DefaultTableModel modeloRutas = modelo("N°", "Ruta", "Km", "Tiempo", "Costo", "Destaca");
    private final JTable tablaRutas = new JTable(modeloRutas);
    private final JSpinner pasajeros = new JSpinner(new SpinnerNumberModel(1, 1, 100, 1));
    private final JComboBox<String> prioridad = new JComboBox<>(PRIORIDADES);
    private final JTextArea resultadoViaje = new JTextArea(7, 40);

    private final DefaultTableModel modeloDisponibles = modelo("Id", "Tipo", "Cap.", "Conductor");
    private final DefaultTableModel modeloOcupados = modelo("Id", "Tipo", "Cap.", "Conductor");
    private final JTable tablaOcupados = new JTable(modeloOcupados);

    private final DefaultTableModel modeloConexiones = modelo("Desde", "Hasta", "Km", "Tráfico", "Peaje");
    private final JTable tablaConexiones = new JTable(modeloConexiones);
    private final JComboBox<String> comboTrafico = new JComboBox<>(TRAFICOS);

    private final DefaultTableModel modeloSolicitudes =
            modelo("Solicitud", "Prioridad", "Estado", "Vehículo", "Cumple SLA", "Ruta");
    private final JTextArea resumenTexto = new JTextArea(8, 40);

    public Ventana() {
        JTabbedPane pestanas = new JTabbedPane();
        pestanas.addTab("Consultar y asignar viaje", panelViaje());
        pestanas.addTab("Vehículos", panelVehiculos());
        pestanas.addTab("Red y tráfico", panelRed());
        pestanas.addTab("Procesar solicitudes", panelProcesar());
        raiz.add(pestanas, BorderLayout.CENTER);
    }

    /** Contenido de la ventana (se separa del JFrame para poder probarlo sin pantalla). */
    public JPanel panel() {
        return raiz;
    }

    private static DefaultTableModel modelo(String... columnas) {
        return new DefaultTableModel(columnas, 0) {
            @Override
            public boolean isCellEditable(int fila, int columna) {
                return false;
            }
        };
    }

    private static void ancho(JTable tabla, int columna, int ancho) {
        tabla.getColumnModel().getColumn(columna).setPreferredWidth(ancho);
    }

    private void aviso(String mensaje) {
        JOptionPane.showMessageDialog(raiz, mensaje, "Dato inválido", JOptionPane.WARNING_MESSAGE);
    }

    private static JPanel marco() {
        JPanel panel = new JPanel(new BorderLayout(0, 6));
        panel.setBorder(BorderFactory.createEmptyBorder(8, 8, 8, 8));
        return panel;
    }

    // ---------------- Pestaña 1: viaje ----------------

    void buscar() {
        modeloRutas.setRowCount(0);
        resultadoViaje.setText("");
        try {
            ListaEnlazada<String[]> filas = logica.buscarRutas(
                    VentanaLogica.idDe(comboOrigen.getSelectedItem()), VentanaLogica.idDe(comboDestino.getSelectedItem()));
            if (filas.estaVacia()) {
                resultadoViaje.setText("No hay ruta entre esas dos ubicaciones.");
                return;
            }
            filas.forEach(f -> modeloRutas.addRow(f));
            resultadoViaje.setText("Elige una ruta de la tabla, indica pasajeros y prioridad, y pulsa «Asignar viaje».");
        } catch (DatosInvalidosException ex) {
            aviso(ex.getMessage());
        }
    }

    void asignarViaje() {
        int fila = tablaRutas.getSelectedRow();
        if (fila < 0) {
            aviso("Selecciona una ruta de la tabla");
            return;
        }
        try {
            resultadoViaje.setText(logica.asignar(fila + 1, String.valueOf(pasajeros.getValue()),
                    String.valueOf(prioridad.getSelectedItem())));
            refrescarVehiculos();
        } catch (DatosInvalidosException ex) {
            aviso(ex.getMessage());
        }
    }

    private JPanel panelViaje() {
        logica.etiquetasUbicaciones().forEach(e -> {
            comboOrigen.addItem(e);
            comboDestino.addItem(e);
        });
        comboDestino.setSelectedIndex(Math.min(1, comboDestino.getItemCount() - 1));

        JButton botonBuscar = new JButton("Buscar rutas");
        botonBuscar.addActionListener(e -> buscar());
        JPanel arriba = new JPanel(new FlowLayout(FlowLayout.LEFT));
        arriba.add(new JLabel("Origen:"));
        arriba.add(comboOrigen);
        arriba.add(new JLabel("Destino:"));
        arriba.add(comboDestino);
        arriba.add(botonBuscar);

        ancho(tablaRutas, 0, 40);
        ancho(tablaRutas, 1, 420);
        ancho(tablaRutas, 2, 70);
        ancho(tablaRutas, 3, 90);
        ancho(tablaRutas, 4, 80);
        ancho(tablaRutas, 5, 220);

        JButton botonAsignar = new JButton("Asignar viaje");
        botonAsignar.addActionListener(e -> asignarViaje());
        prioridad.setSelectedItem("MEDIA");
        JPanel filaPasajeros = new JPanel(new FlowLayout(FlowLayout.LEFT));
        filaPasajeros.add(new JLabel("Pasajeros:"));
        filaPasajeros.add(pasajeros);
        filaPasajeros.add(new JLabel("Prioridad:"));
        filaPasajeros.add(prioridad);
        filaPasajeros.add(botonAsignar);

        resultadoViaje.setEditable(false);
        resultadoViaje.setLineWrap(true);
        resultadoViaje.setWrapStyleWord(true);
        JPanel abajo = new JPanel(new BorderLayout());
        abajo.add(filaPasajeros, BorderLayout.NORTH);
        abajo.add(new JScrollPane(resultadoViaje), BorderLayout.CENTER);

        JPanel panel = marco();
        panel.add(arriba, BorderLayout.NORTH);
        panel.add(new JScrollPane(tablaRutas), BorderLayout.CENTER);
        panel.add(abajo, BorderLayout.SOUTH);
        return panel;
    }

    // ---------------- Pestaña 2: vehículos ----------------

    private void refrescarVehiculos() {
        modeloDisponibles.setRowCount(0);
        modeloOcupados.setRowCount(0);
        logica.flota().disponibles().forEach(v -> modeloDisponibles.addRow(
                new Object[]{v.id(), v.tipo(), v.capacidad(), v.conductor()}));
        logica.flota().ocupados().forEach(v -> modeloOcupados.addRow(
                new Object[]{v.id(), v.tipo(), v.capacidad(), v.conductor()}));
    }

    void finalizarSeleccionado() {
        int fila = tablaOcupados.getSelectedRow();
        if (fila < 0) {
            aviso("Selecciona un vehículo en la lista de ocupados");
            return;
        }
        try {
            logica.finalizarViaje(String.valueOf(modeloOcupados.getValueAt(fila, 0)));
            refrescarVehiculos();
        } catch (DatosInvalidosException ex) {
            aviso(ex.getMessage());
        }
    }

    private JPanel panelVehiculos() {
        JButton actualizar = new JButton("Actualizar");
        actualizar.addActionListener(e -> refrescarVehiculos());
        JButton finalizar = new JButton("Finalizar viaje del seleccionado");
        finalizar.addActionListener(e -> finalizarSeleccionado());

        JPanel izquierda = new JPanel(new BorderLayout(0, 6));
        izquierda.setBorder(BorderFactory.createTitledBorder("Disponibles"));
        izquierda.add(new JScrollPane(new JTable(modeloDisponibles)), BorderLayout.CENTER);
        izquierda.add(actualizar, BorderLayout.SOUTH);
        JPanel derecha = new JPanel(new BorderLayout(0, 6));
        derecha.setBorder(BorderFactory.createTitledBorder("Ocupados"));
        derecha.add(new JScrollPane(tablaOcupados), BorderLayout.CENTER);
        derecha.add(finalizar, BorderLayout.SOUTH);

        JPanel panel = new JPanel(new GridLayout(1, 2, 8, 0));
        panel.setBorder(BorderFactory.createEmptyBorder(8, 8, 8, 8));
        panel.add(izquierda);
        panel.add(derecha);
        refrescarVehiculos();
        return panel;
    }

    // ---------------- Pestaña 3: red y tráfico ----------------

    private void refrescarRed() {
        modeloConexiones.setRowCount(0);
        logica.red().conexiones().forEach(c -> modeloConexiones.addRow(new Object[]{
                logica.nombre(c.origen()), logica.nombre(c.destino()), Datos.f2(c.distanciaKm()),
                c.trafico(), "$" + Datos.f2(c.peaje())}));
    }

    void aplicarTrafico() {
        int fila = tablaConexiones.getSelectedRow();
        if (fila < 0) {
            aviso("Selecciona un tramo de la tabla");
            return;
        }
        Conexion c = logica.red().conexiones().obtener(fila);
        try {
            logica.cambiarTrafico(c.origen(), c.destino(), String.valueOf(comboTrafico.getSelectedItem()));
            refrescarRed();
            tablaConexiones.setRowSelectionInterval(fila, fila);
        } catch (DatosInvalidosException ex) {
            aviso(ex.getMessage());
        }
    }

    private JPanel panelRed() {
        comboTrafico.setSelectedItem("ALTO");
        JButton aplicar = new JButton("Aplicar");
        aplicar.addActionListener(e -> aplicarTrafico());
        JPanel abajo = new JPanel(new FlowLayout(FlowLayout.LEFT));
        abajo.add(new JLabel("Nuevo tráfico del tramo seleccionado:"));
        abajo.add(comboTrafico);
        abajo.add(aplicar);
        abajo.add(new JLabel("(luego vuelve a «Buscar rutas» para ver el efecto)"));

        JPanel panel = marco();
        panel.add(new JScrollPane(tablaConexiones), BorderLayout.CENTER);
        panel.add(abajo, BorderLayout.SOUTH);
        refrescarRed();
        return panel;
    }

    // ---------------- Pestaña 4: procesar solicitudes ----------------

    void procesarTodo() {
        try {
            VentanaLogica.Procesado procesado = logica.procesarSolicitudes();
            modeloSolicitudes.setRowCount(0);
            procesado.filas().forEach(f -> modeloSolicitudes.addRow(f));
            resumenTexto.setText(procesado.resumen());
        } catch (DatosInvalidosException ex) {
            aviso(ex.getMessage());
        }
    }

    private JPanel panelProcesar() {
        JButton procesar = new JButton("Procesar todas las solicitudes (en paralelo)");
        procesar.addActionListener(e -> procesarTodo());
        JTable tabla = new JTable(modeloSolicitudes);
        ancho(tabla, 5, 380);
        resumenTexto.setEditable(false);
        JPanel arriba = new JPanel(new FlowLayout(FlowLayout.LEFT));
        arriba.add(procesar);

        JPanel panel = marco();
        panel.add(arriba, BorderLayout.NORTH);
        panel.add(new JScrollPane(tabla), BorderLayout.CENTER);
        panel.add(new JScrollPane(resumenTexto), BorderLayout.SOUTH);
        return panel;
    }

    public static void main(String[] args) {
        try {
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception ignorada) {
            // Si no hay aspecto del sistema se usa el de Java.
        }
        SwingUtilities.invokeLater(() -> {
            try {
                JFrame ventana = new JFrame("Sistema de transporte (Java)");
                ventana.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
                ventana.setContentPane(new Ventana().panel());
                ventana.setSize(980, 640);
                ventana.setMinimumSize(new Dimension(820, 540));
                ventana.setLocationRelativeTo(null);
                ventana.setVisible(true);
            } catch (DatosInvalidosException e) {
                JOptionPane.showMessageDialog(null, e.getMessage(), "Error de datos", JOptionPane.ERROR_MESSAGE);
                System.exit(2);
            }
        });
    }
}
