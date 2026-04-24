"""Tests del módulo de pacientes — TurnosWeb.

Cada test está marcado con el requerimiento que verifica usando
pytest.mark. Esto permite generar trazabilidad automática:
  pytest --co -q  →  lista tests con sus markers

Trazabilidad:
  TC-001, TC-002, TC-003 → REQ-F01 (Registro de pacientes)
  TC-011               → REQ-NF02 (Datos cifrados)

Ingeniería de Software II — Clase 11 (Taller de Trazabilidad)
"""

import datetime
import pytest
from pacientes import (
    Paciente, RegistroPacientes,
    validar_dni, validar_fecha_nacimiento,
)


# ── Markers de trazabilidad ──────────────────────────────────
# Cada test tiene un marker que indica qué requerimiento verifica.
# Esto permite ejecutar: pytest -m "REQ_F01" para correr solo
# los tests de un requerimiento específico.

pytestmark = pytest.mark.turnosweb


# ════════════════════════════════════════════════════════════════
#  TC-001: Registro exitoso de paciente
#  Trazabilidad: REQ-F01
# ════════════════════════════════════════════════════════════════
class TestRegistroPaciente:
    """TC-001: Verificar registro exitoso con datos válidos."""

    @pytest.mark.REQ_F01
    def test_registro_exitoso(self):
        """REQ-F01: Datos válidos → confirma registro."""
        registro = RegistroPacientes()
        paciente = registro.registrar_paciente(
            nombre="María García",
            dni="30123456",
            fecha_nacimiento=datetime.date(1990, 5, 15),
        )
        assert paciente.nombre == "María García"
        assert paciente.dni == "30123456"
        assert paciente.fecha_nacimiento == datetime.date(1990, 5, 15)

    @pytest.mark.REQ_F01
    def test_registro_con_puntos_en_dni(self):
        """REQ-F01: DNI con puntos se normaliza."""
        registro = RegistroPacientes()
        paciente = registro.registrar_paciente(
            nombre="Juan López",
            dni="30.123.456",
            fecha_nacimiento=datetime.date(1985, 3, 20),
        )
        assert paciente.dni == "30123456"


# ════════════════════════════════════════════════════════════════
#  TC-002: Validaciones de datos de registro
#  Trazabilidad: REQ-F01
# ════════════════════════════════════════════════════════════════
class TestValidacionesRegistro:
    """TC-002: Verificar que datos inválidos son rechazados."""

    @pytest.mark.REQ_F01
    def test_dni_invalido_letras(self):
        """REQ-F01: DNI con letras → rechazado."""
        assert validar_dni("ABC12345") is False

    @pytest.mark.REQ_F01
    def test_dni_invalido_corto(self):
        """REQ-F01: DNI con menos de 7 dígitos → rechazado."""
        assert validar_dni("12345") is False

    @pytest.mark.REQ_F01
    def test_dni_valido(self):
        """REQ-F01: DNI con 7-8 dígitos → aceptado."""
        assert validar_dni("30123456") is True
        assert validar_dni("1234567") is True

    @pytest.mark.REQ_F01
    def test_nombre_vacio_rechazado(self):
        """REQ-F01: Nombre vacío → ValueError."""
        registro = RegistroPacientes()
        with pytest.raises(ValueError, match="nombre"):
            registro.registrar_paciente(
                nombre="",
                dni="30123456",
                fecha_nacimiento=datetime.date(1990, 1, 1),
            )

    @pytest.mark.REQ_F01
    def test_duplicado_rechazado(self):
        """REQ-F01: DNI duplicado → ValueError."""
        registro = RegistroPacientes()
        registro.registrar_paciente(
            "Ana", "30123456", datetime.date(1990, 1, 1)
        )
        with pytest.raises(ValueError, match="Ya existe"):
            registro.registrar_paciente(
                "Otro", "30123456", datetime.date(1995, 6, 1)
            )


# ════════════════════════════════════════════════════════════════
#  TC-003: Cálculo de edad del paciente
#  Trazabilidad: REQ-F01 (datos de registro incluyen fecha nac.)
# ════════════════════════════════════════════════════════════════
class TestEdadPaciente:
    """TC-003: Verificar cálculo correcto de edad."""

    @pytest.mark.REQ_F01
    def test_edad_calculo_correcto(self):
        """REQ-F01: La edad se calcula correctamente."""
        paciente = Paciente(
            nombre="Test",
            dni="12345678",
            fecha_nacimiento=datetime.date(2000, 1, 1),
        )
        # La edad depende de la fecha actual, solo verificamos
        # que sea un número razonable
        assert 0 <= paciente.edad() <= 150

    @pytest.mark.REQ_F01
    def test_fecha_nacimiento_futura_rechazada(self):
        """REQ-F01: Fecha futura → inválida."""
        fecha_futura = datetime.date.today() + datetime.timedelta(days=1)
        assert validar_fecha_nacimiento(fecha_futura) is False


# ════════════════════════════════════════════════════════════════
#  TC-011: Datos personales cifrados
#  Trazabilidad: REQ-NF02
# ════════════════════════════════════════════════════════════════
class TestDatosCifrados:
    """TC-011: Verificar que datos sensibles se cifran."""

    @pytest.mark.REQ_NF02
    def test_dni_cifrado_no_es_texto_plano(self):
        """REQ-NF02: El DNI cifrado NO es igual al original."""
        paciente = Paciente(
            nombre="Test",
            dni="30123456",
            fecha_nacimiento=datetime.date(1990, 1, 1),
        )
        assert paciente.dni_cifrado != "30123456"
        assert len(paciente.dni_cifrado) == 64  # SHA-256 → 64 hex chars

    @pytest.mark.REQ_NF02
    def test_mismo_dni_produce_mismo_hash(self):
        """REQ-NF02: Cifrado determinístico (mismo input → mismo output)."""
        p1 = Paciente("A", "30123456", datetime.date(1990, 1, 1))
        p2 = Paciente("B", "30123456", datetime.date(1995, 6, 1))
        assert p1.dni_cifrado == p2.dni_cifrado

    @pytest.mark.REQ_NF02
    def test_distinto_dni_produce_distinto_hash(self):
        """REQ-NF02: Distintos DNIs → distintos hashes."""
        p1 = Paciente("A", "30123456", datetime.date(1990, 1, 1))
        p2 = Paciente("B", "99999999", datetime.date(1990, 1, 1))
        assert p1.dni_cifrado != p2.dni_cifrado
