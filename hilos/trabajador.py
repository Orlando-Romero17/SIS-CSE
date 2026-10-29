"""
trabajador.py
Ejecuta funciones pesadas (consultas a MySQL, respaldos, PDF) en un hilo
aparte para que la ventana nunca se congele ni salga "no responde".

Reglas del diseño:
  - Cada hilo usa su propia sesión de base de datos (nunca se comparte).
  - Los hilos NO tocan la interfaz: solo devuelven datos.
  - Los resultados se entregan al hilo principal mediante una señal de Qt.
"""
from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot, Qt


class _Puente(QObject):
    """Objeto que vive en el hilo principal. Recibe los resultados que envían los
    hilos y ejecuta los callbacks de la interfaz de forma segura."""
    listo = Signal(object, object)  # (callback, valor)

    def __init__(self):
        super().__init__()
        # QueuedConnection: el callback se ejecuta en el hilo principal
        self.listo.connect(self._despachar, Qt.QueuedConnection)

    @Slot(object, object)
    def _despachar(self, callback, valor):
        if callback is None:
            return
        try:
            callback(valor)
        except RuntimeError:
            # La ventana ya se cerró antes de terminar la consulta: se ignora
            pass


_puente = None


def _obtener_puente():
    """Crea el puente la primera vez (siempre desde el hilo principal)."""
    global _puente
    if _puente is None:
        _puente = _Puente()
    return _puente


class _Trabajo(QRunnable):
    """Tarea que se ejecuta dentro del pool de hilos de Qt."""

    def __init__(self, funcion, args, kwargs, al_terminar, al_error, puente):
        super().__init__()
        self.funcion = funcion
        self.args = args
        self.kwargs = kwargs
        self.al_terminar = al_terminar
        self.al_error = al_error
        self.puente = puente

    def run(self):
        """Corre en el hilo secundario: ejecuta la función y envía el resultado."""
        try:
            resultado = self.funcion(*self.args, **self.kwargs)
        except Exception as e:
            self.puente.listo.emit(self.al_error, str(e))
        else:
            self.puente.listo.emit(self.al_terminar, resultado)


def ejecutar_en_hilo(funcion, *args, al_terminar=None, al_error=None, **kwargs):
    """Ejecuta funcion(*args, **kwargs) en segundo plano.

    al_terminar(resultado): se llama en el hilo principal si todo salió bien.
    al_error(mensaje):      se llama en el hilo principal si hubo una excepción.
    Debe llamarse siempre desde la interfaz (hilo principal)."""
    if al_error is None:
        al_error = lambda msg: print("Error:", msg)
    trabajo = _Trabajo(funcion, args, kwargs, al_terminar, al_error, _obtener_puente())
    QThreadPool.globalInstance().start(trabajo)