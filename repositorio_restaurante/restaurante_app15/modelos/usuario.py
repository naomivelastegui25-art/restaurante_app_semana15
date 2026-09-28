class Usuario:
    """Persona registrada. Puede comprar y acceder a la aplicación (acceso simulado)."""

    def __init__(self, identificacion: str, nombre: str, contrasena: str) -> None:
        if not str(identificacion).strip():
            raise ValueError("La identificación no puede estar vacía.")
        if not nombre.strip():
            raise ValueError("El nombre no puede estar vacío.")
        if not contrasena:
            raise ValueError("La contraseña no puede estar vacía.")

        self.identificacion: str = str(identificacion).strip()
        self.nombre: str = nombre.strip()
        self.contrasena: str = contrasena

    def convertir_a_diccionario(self) -> dict:
        return {
            "identificacion": self.identificacion,
            "nombre": self.nombre,
            "contrasena": self.contrasena,
        }
