"""Módulo de gestión de pacientes — TurnosWeb.

Implementa:
  REQ-F01: Registro de pacientes con nombre, DNI y fecha de nacimiento
  REQ-NF02: Datos personales almacenados cifrados

Ingeniería de Software II — Clase 11 (Taller de Trazabilidad)
"""

import hashlib
import datetime
from dataclasses import dataclass, field
from typing import Optional


# ── Constante ────────────────────────────────────────────────
EDAD_MINIMA = 0
EDAD_MAXIMA = 120


@dataclass
class Paciente:
    """Representa un paciente registrado en el sistema.

    Trazabilidad:
      - REQ-F01: campos nombre, dni, fecha_nacimiento
      - REQ-NF02: dni_cifrado para almacenamiento seguro
    """
    nombre: str
    dni: str
    fecha_nacimiento: datetime.date
    fecha_registro: datetime.datetime = field(
        default_factory=datetime.datetime.now
    )
    dni_cifrado: str = ""

    def __post_init__(self):
        # REQ-NF02: cifrar el DNI al crear el paciente
        self.dni_cifrado = self._cifrar_dato(self.dni)

    @staticmethod
    def _cifrar_dato(dato: str) -> str:
        """Cifra un dato sensible usando SHA-256.

        Trazabilidad: REQ-NF02
        En producción usaríamos cifrado reversible (AES), pero
        para la demo usamos hash unidireccional.
        """
        return hashlib.sha256(dato.encode()).hexdigest()

    def edad(self) -> int:
        """Calcula la edad del paciente."""
        hoy = datetime.date.today()
        edad = hoy.year - self.fecha_nacimiento.year
        if (hoy.month, hoy.day) < (
            self.fecha_nacimiento.month, self.fecha_nacimiento.day
        ):
            edad -= 1
        return edad


def validar_dni(dni: str) -> bool:
    """Valida que el DNI tenga formato correcto (7-8 dígitos).

    Trazabilidad: REQ-F01 (validación de datos de registro)
    """
    dni_limpio = dni.replace(".", "").strip()
    return dni_limpio.isdigit() and 7 <= len(dni_limpio) <= 8


def validar_fecha_nacimiento(fecha: datetime.date) -> bool:
    """Valida que la fecha de nacimiento sea razonable.

    Trazabilidad: REQ-F01 (validación de datos de registro)
    """
    hoy = datetime.date.today()
    edad = hoy.year - fecha.year
    return EDAD_MINIMA <= edad <= EDAD_MAXIMA and fecha <= hoy


class RegistroPacientes:
    """Gestiona el registro y búsqueda de pacientes.

    Trazabilidad:
      - REQ-F01: registrar_paciente(), buscar_por_dni()
      - REQ-NF02: datos cifrados al persistir
    """

    def __init__(self):
        self._pacientes: list[Paciente] = []

    def registrar_paciente(
        self, nombre: str, dni: str, fecha_nacimiento: datetime.date
    ) -> Paciente:
        """Registra un nuevo paciente.

        Trazabilidad: REQ-F01
        Criterio: nombre/DNI/fecha válidos → confirma registro.

        Raises:
            ValueError: si los datos son inválidos o el DNI ya existe.
        """
        # Validar nombre
        if not nombre or not nombre.strip():
            raise ValueError("El nombre no puede estar vacío")

        # Validar DNI
        if not validar_dni(dni):
            raise ValueError(
                f"DNI inválido: '{dni}'. Debe tener 7-8 dígitos."
            )

        # Validar que no exista
        if self.buscar_por_dni(dni):
            raise ValueError(
                f"Ya existe un paciente con DNI {dni}"
            )

        # Validar fecha
        if not validar_fecha_nacimiento(fecha_nacimiento):
            raise ValueError(
                f"Fecha de nacimiento inválida: {fecha_nacimiento}"
            )

        paciente = Paciente(
            nombre=nombre.strip(),
            dni=dni.replace(".", "").strip(),
            fecha_nacimiento=fecha_nacimiento,
        )
        self._pacientes.append(paciente)
        return paciente

    def buscar_por_dni(self, dni: str) -> Optional[Paciente]:
        """Busca un paciente por DNI.

        Trazabilidad: REQ-F01 (soporte a registro — verificar duplicados)
        """
        dni_limpio = dni.replace(".", "").strip()
        for paciente in self._pacientes:
            if paciente.dni == dni_limpio:
                return paciente
        return None

    def cantidad_registrados(self) -> int:
        """Retorna la cantidad de pacientes registrados."""
        return len(self._pacientes)
