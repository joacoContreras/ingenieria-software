"""Módulo de notificaciones — TurnosWeb.

Implementa:
  REQ-F03: Enviar confirmación del turno al paciente
  REQ-N02: Recordatorios automáticos para reducir ausentismo

Ingeniería de Software II — Clase 11 (Taller de Trazabilidad)
"""

import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class TipoNotificacion(Enum):
    CONFIRMACION = "Confirmación de turno"
    RECORDATORIO = "Recordatorio de turno"
    CANCELACION = "Cancelación de turno"


@dataclass
class Notificacion:
    """Representa una notificación enviada.

    Trazabilidad:
      - REQ-F03: tipo CONFIRMACION
      - REQ-N02: tipo RECORDATORIO
    """
    destinatario_dni: str
    tipo: TipoNotificacion
    mensaje: str
    canal: str  # "email" o "sms"
    enviada: bool = False
    fecha_envio: Optional[datetime.datetime] = None
    fecha_creacion: datetime.datetime = field(
        default_factory=datetime.datetime.now
    )


class ServicioNotificaciones:
    """Gestiona el envío de notificaciones a pacientes.

    Trazabilidad:
      - REQ-F03: enviar_confirmacion()
      - REQ-N02: programar_recordatorio()
    """

    def __init__(self):
        self._notificaciones: list[Notificacion] = []
        self._recordatorios_programados: list[dict] = []

    def enviar_confirmacion(
        self,
        paciente_dni: str,
        medico_nombre: str,
        especialidad: str,
        fecha: datetime.date,
        hora: str,
        canal: str = "email",
    ) -> Notificacion:
        """Envía confirmación de turno al paciente.

        Trazabilidad: REQ-F03
        Criterio: al agendar turno, paciente recibe mensaje
        con fecha, hora y médico.
        """
        mensaje = (
            f"Turno confirmado:\n"
            f"  Médico: Dr/a. {medico_nombre}\n"
            f"  Especialidad: {especialidad}\n"
            f"  Fecha: {fecha.strftime('%d/%m/%Y')}\n"
            f"  Hora: {hora}\n"
            f"  Hospital Provincial de Córdoba\n\n"
            f"Para cancelar, ingrese al sistema con al menos "
            f"24hs de anticipación."
        )

        notificacion = Notificacion(
            destinatario_dni=paciente_dni,
            tipo=TipoNotificacion.CONFIRMACION,
            mensaje=mensaje,
            canal=canal,
        )

        # Simular envío (en producción: integración con servicio SMTP/SMS)
        notificacion.enviada = True
        notificacion.fecha_envio = datetime.datetime.now()

        self._notificaciones.append(notificacion)
        return notificacion

    def programar_recordatorio(
        self,
        paciente_dni: str,
        turno_fecha: datetime.date,
        turno_hora: str,
        medico_nombre: str,
        horas_antes: int = 24,
    ) -> dict:
        """Programa un recordatorio automático antes del turno.

        Trazabilidad: REQ-N02
        Objetivo de negocio: reducir ausentismo en 30%.
        Envía recordatorio 24hs antes del turno.
        """
        turno_datetime = datetime.datetime.combine(
            turno_fecha,
            datetime.datetime.strptime(turno_hora, "%H:%M").time()
        )
        envio_programado = turno_datetime - datetime.timedelta(
            hours=horas_antes
        )

        recordatorio = {
            "paciente_dni": paciente_dni,
            "fecha_envio": envio_programado,
            "mensaje": (
                f"Recordatorio: tiene turno mañana a las {turno_hora} "
                f"con Dr/a. {medico_nombre} en Hospital Provincial."
            ),
            "enviado": False,
        }

        self._recordatorios_programados.append(recordatorio)
        return recordatorio

    def enviar_cancelacion(
        self,
        paciente_dni: str,
        turno_fecha: datetime.date,
        turno_hora: str,
    ) -> Notificacion:
        """Envía notificación de cancelación.

        Trazabilidad: complementa REQ-F04 (cancelación de turnos).
        """
        mensaje = (
            f"Su turno del {turno_fecha.strftime('%d/%m/%Y')} "
            f"a las {turno_hora} ha sido cancelado exitosamente."
        )

        notificacion = Notificacion(
            destinatario_dni=paciente_dni,
            tipo=TipoNotificacion.CANCELACION,
            mensaje=mensaje,
            canal="email",
        )
        notificacion.enviada = True
        notificacion.fecha_envio = datetime.datetime.now()

        self._notificaciones.append(notificacion)
        return notificacion

    def notificaciones_enviadas(self) -> int:
        """Retorna cantidad de notificaciones enviadas."""
        return sum(1 for n in self._notificaciones if n.enviada)

    def recordatorios_pendientes(self) -> list[dict]:
        """Retorna recordatorios aún no enviados."""
        return [
            r for r in self._recordatorios_programados
            if not r["enviado"]
        ]
