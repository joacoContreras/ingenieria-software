"""Tests del módulo de notificaciones — TurnosWeb.

Trazabilidad:
  TC-006 → REQ-F03 (Confirmación de turno)
    TC-007/TC-008 → REQ-N02 (Recordatorios automáticos)

Ingeniería de Software II — Clase 11 (Taller de Trazabilidad)
"""

import datetime
import pytest
from notificaciones import (
    ServicioNotificaciones, TipoNotificacion,
)


# ════════════════════════════════════════════════════════════════
#  TC-006: Confirmación de turno enviada
#  Trazabilidad: REQ-F03
# ════════════════════════════════════════════════════════════════
class TestConfirmacionTurno:
    """TC-006: Verificar envío de confirmación al agendar."""

    @pytest.mark.REQ_F03
    def test_enviar_confirmacion_exitosa(self):
        """REQ-F03: Al agendar turno, paciente recibe confirmación."""
        servicio = ServicioNotificaciones()
        notif = servicio.enviar_confirmacion(
            paciente_dni="30123456",
            medico_nombre="Dra. Fernández",
            especialidad="Clínica Médica",
            fecha=datetime.date(2026, 5, 15),
            hora="09:00",
        )
        assert notif.enviada is True
        assert notif.tipo == TipoNotificacion.CONFIRMACION
        assert "Dra. Fernández" in notif.mensaje
        assert "09:00" in notif.mensaje

    @pytest.mark.REQ_F03
    def test_confirmacion_contiene_datos_turno(self):
        """REQ-F03: El mensaje incluye fecha, hora y médico."""
        servicio = ServicioNotificaciones()
        notif = servicio.enviar_confirmacion(
            paciente_dni="30123456",
            medico_nombre="Dr. González",
            especialidad="Cardiología",
            fecha=datetime.date(2026, 6, 20),
            hora="14:30",
        )
        assert "Dr. González" in notif.mensaje
        assert "Cardiología" in notif.mensaje
        assert "14:30" in notif.mensaje
        assert "20/06/2026" in notif.mensaje

    @pytest.mark.REQ_F03
    def test_contador_notificaciones(self):
        """REQ-F03: Se cuenta correctamente la cantidad de envíos."""
        servicio = ServicioNotificaciones()
        servicio.enviar_confirmacion(
            "30123456", "Dra. Fernández", "Clínica",
            datetime.date(2026, 5, 15), "09:00",
        )
        servicio.enviar_confirmacion(
            "99999999", "Dr. González", "Cardio",
            datetime.date(2026, 5, 16), "10:00",
        )
        assert servicio.notificaciones_enviadas() == 2


# ════════════════════════════════════════════════════════════════
#  TC-007/TC-008: Recordatorios automáticos
#  Trazabilidad: REQ-N02
# ════════════════════════════════════════════════════════════════
class TestRecordatorioAutomatico:
    """Tests para REQ-N02: Recordatorios para reducir ausentismo."""

    @pytest.mark.REQ_N02
    def test_programar_recordatorio_crea_notificacion(self):
        """REQ-N02: Al programar un recordatorio se registra correctamente."""
        servicio = ServicioNotificaciones()
        recordatorio = servicio.programar_recordatorio(
            paciente_dni="30123456",
            turno_fecha=datetime.date(2026, 6, 20),
            turno_hora="09:00",
            medico_nombre="Dra. Fernández",
        )

        assert recordatorio["paciente_dni"] == "30123456"
        assert recordatorio["enviado"] is False
        assert "Recordatorio" in recordatorio["mensaje"]
        assert "09:00" in recordatorio["mensaje"]
        assert "Dra. Fernández" in recordatorio["mensaje"]
        assert recordatorio in servicio.recordatorios_pendientes()

    @pytest.mark.REQ_N02
    def test_recordatorio_se_programa_antes_del_turno(self):
        """REQ-N02: El recordatorio se programa con anticipación al turno."""
        servicio = ServicioNotificaciones()
        turno_fecha = datetime.date(2026, 6, 20)
        turno_hora = "09:00"

        recordatorio = servicio.programar_recordatorio(
            paciente_dni="30123456",
            turno_fecha=turno_fecha,
            turno_hora=turno_hora,
            medico_nombre="Dra. Fernández",
        )

        turno_dt = datetime.datetime.combine(
            turno_fecha,
            datetime.datetime.strptime(turno_hora, "%H:%M").time(),
        )
        assert recordatorio["fecha_envio"] < turno_dt
        assert recordatorio["fecha_envio"] == (
            turno_dt - datetime.timedelta(hours=24)
        )

    @pytest.mark.REQ_N02
    def test_recordatorios_pendientes_excluye_enviados(self):
        """REQ-N02: Solo se listan como pendientes los no enviados."""
        servicio = ServicioNotificaciones()
        pendiente = servicio.programar_recordatorio(
            paciente_dni="30123456",
            turno_fecha=datetime.date(2026, 6, 20),
            turno_hora="09:00",
            medico_nombre="Dra. Fernández",
        )
        enviado = servicio.programar_recordatorio(
            paciente_dni="30999888",
            turno_fecha=datetime.date(2026, 6, 21),
            turno_hora="10:30",
            medico_nombre="Dr. Suárez",
        )

        enviado["enviado"] = True
        pendientes = servicio.recordatorios_pendientes()

        assert pendiente in pendientes
        assert enviado not in pendientes
