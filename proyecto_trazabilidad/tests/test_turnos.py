"""Tests del módulo de turnos — TurnosWeb.

Trazabilidad:
  TC-004, TC-005  → REQ-F02 (Agendar turno)
  TC-007 a TC-009 → REQ-F04 (Cancelar turno 24hs antes)
  TC-010          → REQ-F05 (Turnos disponibles por especialidad)

Ingeniería de Software II — Clase 11 (Taller de Trazabilidad)
"""

import datetime
import pytest
from turnos import (
    GestorTurnos, Medico, Especialidad, EstadoTurno,
    HORAS_MINIMAS_CANCELACION,
)


# ── Fixtures ─────────────────────────────────────────────────

@pytest.fixture
def medicos():
    """Lista de médicos de prueba."""
    return [
        Medico("Dra. Fernández", "MP-1234", Especialidad.CLINICA_MEDICA),
        Medico("Dr. González", "MP-5678", Especialidad.CARDIOLOGIA),
        Medico("Dra. Ruiz", "MP-9012", Especialidad.PEDIATRIA),
    ]


@pytest.fixture
def gestor(medicos):
    """Gestor de turnos con médicos precargados."""
    return GestorTurnos(medicos)


@pytest.fixture
def fecha_futura():
    """Una fecha 7 días en el futuro (siempre cancelable)."""
    return datetime.date.today() + datetime.timedelta(days=7)


# ════════════════════════════════════════════════════════════════
#  TC-004: Agendar turno exitoso
#  Trazabilidad: REQ-F02
# ════════════════════════════════════════════════════════════════
class TestAgendarTurno:
    """TC-004: Verificar que se agenda un turno correctamente."""

    @pytest.mark.REQ_F02
    def test_agendar_turno_exitoso(self, gestor, fecha_futura):
        """REQ-F02: Paciente + horario disponible → turno agendado."""
        turno = gestor.agendar_turno(
            paciente_dni="30123456",
            especialidad=Especialidad.CLINICA_MEDICA,
            medico_matricula="MP-1234",
            fecha=fecha_futura,
            hora=datetime.time(9, 0),
        )
        assert turno.paciente_dni == "30123456"
        assert turno.especialidad == Especialidad.CLINICA_MEDICA
        assert turno.estado == EstadoTurno.AGENDADO
        assert turno.turno_id.startswith("TUR-")

    @pytest.mark.REQ_F02
    def test_agendar_turno_aparece_en_agenda(self, gestor, fecha_futura):
        """REQ-F02: Turno agendado aparece en la lista del paciente."""
        gestor.agendar_turno(
            "30123456", Especialidad.CLINICA_MEDICA,
            "MP-1234", fecha_futura, datetime.time(9, 0),
        )
        turnos = gestor.turnos_del_paciente("30123456")
        assert len(turnos) == 1


# ════════════════════════════════════════════════════════════════
#  TC-005: Validaciones al agendar turno
#  Trazabilidad: REQ-F02
# ════════════════════════════════════════════════════════════════
class TestValidacionesAgendar:
    """TC-005: Verificar rechazos de turnos inválidos."""

    @pytest.mark.REQ_F02
    def test_horario_duplicado_rechazado(self, gestor, fecha_futura):
        """REQ-F02: No se puede agendar dos turnos en el mismo horario."""
        gestor.agendar_turno(
            "30123456", Especialidad.CLINICA_MEDICA,
            "MP-1234", fecha_futura, datetime.time(9, 0),
        )
        with pytest.raises(ValueError, match="ya tiene un turno"):
            gestor.agendar_turno(
                "99999999", Especialidad.CLINICA_MEDICA,
                "MP-1234", fecha_futura, datetime.time(9, 0),
            )

    @pytest.mark.REQ_F02
    def test_medico_inexistente_rechazado(self, gestor, fecha_futura):
        """REQ-F02: Médico que no existe → rechazado."""
        with pytest.raises(ValueError, match="no encontrado"):
            gestor.agendar_turno(
                "30123456", Especialidad.CLINICA_MEDICA,
                "MP-0000", fecha_futura, datetime.time(9, 0),
            )

    @pytest.mark.REQ_F02
    def test_especialidad_incorrecta_rechazada(self, gestor, fecha_futura):
        """REQ-F02: Médico de otra especialidad → rechazado."""
        with pytest.raises(ValueError, match="no atiende"):
            gestor.agendar_turno(
                "30123456", Especialidad.CARDIOLOGIA,
                "MP-1234", fecha_futura, datetime.time(9, 0),
            )

    @pytest.mark.REQ_F02
    def test_fecha_pasada_rechazada(self, gestor):
        """REQ-F02: Fecha en el pasado → rechazado."""
        ayer = datetime.date.today() - datetime.timedelta(days=1)
        with pytest.raises(ValueError, match="pasado"):
            gestor.agendar_turno(
                "30123456", Especialidad.CLINICA_MEDICA,
                "MP-1234", ayer, datetime.time(9, 0),
            )


# ════════════════════════════════════════════════════════════════
#  TC-007: Cancelación exitosa de turno
#  Trazabilidad: REQ-F04
# ════════════════════════════════════════════════════════════════
class TestCancelarTurno:
    """TC-007: Verificar cancelación exitosa (>= 24hs antes)."""

    @pytest.mark.REQ_F04
    def test_cancelar_turno_exitoso(self, gestor, fecha_futura):
        """REQ-F04: Turno a 7 días → se puede cancelar."""
        turno = gestor.agendar_turno(
            "30123456", Especialidad.CLINICA_MEDICA,
            "MP-1234", fecha_futura, datetime.time(9, 0),
        )
        cancelado = gestor.cancelar_turno(turno.turno_id)
        assert cancelado.estado == EstadoTurno.CANCELADO

    @pytest.mark.REQ_F04
    def test_cancelar_libera_horario(self, gestor, fecha_futura):
        """REQ-F04: Al cancelar, el horario queda disponible."""
        turno = gestor.agendar_turno(
            "30123456", Especialidad.CLINICA_MEDICA,
            "MP-1234", fecha_futura, datetime.time(9, 0),
        )
        gestor.cancelar_turno(turno.turno_id)

        # El horario debe estar disponible de nuevo
        disponibles = gestor.turnos_disponibles(
            Especialidad.CLINICA_MEDICA, fecha_futura
        )
        horas_disponibles = [d["hora"] for d in disponibles]
        assert "09:00" in horas_disponibles


# ════════════════════════════════════════════════════════════════
#  TC-008: Cancelación rechazada (menos de 24hs)
#  Trazabilidad: REQ-F04
# ════════════════════════════════════════════════════════════════
class TestCancelacionRechazada:
    """TC-008: Turno < 24hs → no se puede cancelar."""

    @pytest.mark.REQ_F04
    def test_cancelar_turno_ya_cancelado(self, gestor, fecha_futura):
        """REQ-F04: Turno ya cancelado → error."""
        turno = gestor.agendar_turno(
            "30123456", Especialidad.CLINICA_MEDICA,
            "MP-1234", fecha_futura, datetime.time(9, 0),
        )
        gestor.cancelar_turno(turno.turno_id)
        with pytest.raises(ValueError, match="ya está cancelado"):
            gestor.cancelar_turno(turno.turno_id)


# ════════════════════════════════════════════════════════════════
#  TC-009: Verificar regla de 24hs
#  Trazabilidad: REQ-F04
# ════════════════════════════════════════════════════════════════
class TestRegla24Horas:
    """TC-009: Verificar lógica de la regla de 24hs."""

    @pytest.mark.REQ_F04
    def test_puede_cancelarse_turno_lejano(self, gestor, fecha_futura):
        """REQ-F04: Turno a 7 días → puede_cancelarse() = True."""
        turno = gestor.agendar_turno(
            "30123456", Especialidad.CLINICA_MEDICA,
            "MP-1234", fecha_futura, datetime.time(9, 0),
        )
        assert turno.puede_cancelarse() is True

    @pytest.mark.REQ_F04
    def test_constante_horas_cancelacion(self):
        """REQ-F04: La constante de cancelación es 24hs."""
        assert HORAS_MINIMAS_CANCELACION == 24


# ════════════════════════════════════════════════════════════════
#  TC-010: Turnos disponibles por especialidad
#  Trazabilidad: REQ-F05
# ════════════════════════════════════════════════════════════════
class TestTurnosDisponibles:
    """TC-010: Verificar filtrado por especialidad."""

    @pytest.mark.REQ_F05
    def test_disponibles_solo_de_especialidad(self, gestor, fecha_futura):
        """REQ-F05: Solo se muestran horarios de la especialidad."""
        disponibles = gestor.turnos_disponibles(
            Especialidad.CLINICA_MEDICA, fecha_futura
        )
        for d in disponibles:
            assert d["especialidad"] == "Clínica Médica"

    @pytest.mark.REQ_F05
    def test_turno_agendado_no_aparece(self, gestor, fecha_futura):
        """REQ-F05: Horario ocupado no aparece como disponible."""
        gestor.agendar_turno(
            "30123456", Especialidad.CLINICA_MEDICA,
            "MP-1234", fecha_futura, datetime.time(9, 0),
        )
        disponibles = gestor.turnos_disponibles(
            Especialidad.CLINICA_MEDICA, fecha_futura
        )
        horas = [d["hora"] for d in disponibles
                 if d["matricula"] == "MP-1234"]
        assert "09:00" not in horas
