"""Módulo de gestión de turnos — TurnosWeb.

Implementa:
  REQ-F02: Agendar turno (especialidad, médico, fecha, hora)
  REQ-F04: Cancelar turno hasta 24hs antes
  REQ-F05: Mostrar turnos disponibles por especialidad

Ingeniería de Software II — Clase 11 (Taller de Trazabilidad)
"""

import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ── Constantes ───────────────────────────────────────────────

HORAS_MINIMAS_CANCELACION = 24  # REQ-F04: 24hs antes

HORARIOS_DISPONIBLES = [
    datetime.time(8, 0), datetime.time(8, 30),
    datetime.time(9, 0), datetime.time(9, 30),
    datetime.time(10, 0), datetime.time(10, 30),
    datetime.time(11, 0), datetime.time(11, 30),
    datetime.time(14, 0), datetime.time(14, 30),
    datetime.time(15, 0), datetime.time(15, 30),
    datetime.time(16, 0), datetime.time(16, 30),
]


class Especialidad(Enum):
    CLINICA_MEDICA = "Clínica Médica"
    PEDIATRIA = "Pediatría"
    CARDIOLOGIA = "Cardiología"
    TRAUMATOLOGIA = "Traumatología"
    DERMATOLOGIA = "Dermatología"


class EstadoTurno(Enum):
    AGENDADO = "Agendado"
    CANCELADO = "Cancelado"
    COMPLETADO = "Completado"
    AUSENTE = "Ausente"


@dataclass
class Medico:
    """Representa un médico del hospital."""
    nombre: str
    matricula: str
    especialidad: Especialidad


@dataclass
class Turno:
    """Representa un turno agendado.

    Trazabilidad:
      - REQ-F02: campos paciente_dni, medico, fecha, hora, especialidad
      - REQ-F04: campo estado + método cancelar()
    """
    turno_id: str
    paciente_dni: str
    medico: Medico
    especialidad: Especialidad
    fecha: datetime.date
    hora: datetime.time
    estado: EstadoTurno = EstadoTurno.AGENDADO
    fecha_creacion: datetime.datetime = field(
        default_factory=datetime.datetime.now
    )

    @property
    def fecha_hora(self) -> datetime.datetime:
        """Combina fecha y hora del turno."""
        return datetime.datetime.combine(self.fecha, self.hora)

    def puede_cancelarse(self) -> bool:
        """Verifica si el turno puede cancelarse (24hs antes).

        Trazabilidad: REQ-F04
        Criterio: si faltan >= 24hs para el turno, se puede cancelar.
        """
        ahora = datetime.datetime.now()
        diferencia = self.fecha_hora - ahora
        return diferencia.total_seconds() >= (
            HORAS_MINIMAS_CANCELACION * 3600
        )


class GestorTurnos:
    """Gestiona la agenda de turnos del hospital.

    Trazabilidad:
      - REQ-F02: agendar_turno()
      - REQ-F04: cancelar_turno()
      - REQ-F05: turnos_disponibles()
    """

    def __init__(self, medicos: list[Medico]):
        self._turnos: list[Turno] = []
        self._medicos = medicos
        self._contador = 0

    def _generar_id(self) -> str:
        """Genera un ID único para el turno."""
        self._contador += 1
        return f"TUR-{self._contador:04d}"

    def agendar_turno(
        self,
        paciente_dni: str,
        especialidad: Especialidad,
        medico_matricula: str,
        fecha: datetime.date,
        hora: datetime.time,
    ) -> Turno:
        """Agenda un nuevo turno.

        Trazabilidad: REQ-F02
        Criterio: paciente registrado + horario disponible → turno agendado.

        Raises:
            ValueError: si el médico no existe, el horario no es válido,
                       o ya hay un turno en ese horario.
        """
        # Buscar médico
        medico = self._buscar_medico(medico_matricula)
        if medico is None:
            raise ValueError(
                f"Médico con matrícula '{medico_matricula}' no encontrado"
            )

        # Verificar que el médico es de la especialidad
        if medico.especialidad != especialidad:
            raise ValueError(
                f"El médico {medico.nombre} no atiende "
                f"{especialidad.value}"
            )

        # Verificar horario válido
        if hora not in HORARIOS_DISPONIBLES:
            raise ValueError(
                f"Horario {hora} no está disponible. "
                f"Horarios válidos: {[h.strftime('%H:%M') for h in HORARIOS_DISPONIBLES]}"
            )

        # Verificar que no hay turno en ese horario para ese médico
        if self._horario_ocupado(medico_matricula, fecha, hora):
            raise ValueError(
                f"El Dr. {medico.nombre} ya tiene un turno el "
                f"{fecha} a las {hora.strftime('%H:%M')}"
            )

        # Verificar que la fecha es futura
        if fecha < datetime.date.today():
            raise ValueError("No se puede agendar un turno en el pasado")

        turno = Turno(
            turno_id=self._generar_id(),
            paciente_dni=paciente_dni,
            medico=medico,
            especialidad=especialidad,
            fecha=fecha,
            hora=hora,
        )
        self._turnos.append(turno)
        return turno

    def cancelar_turno(self, turno_id: str) -> Turno:
        """Cancela un turno existente.

        Trazabilidad: REQ-F04
        Criterio: si faltan >= 24hs, se cancela y se libera el horario.

        Raises:
            ValueError: si el turno no existe, ya está cancelado,
                       o faltan menos de 24hs.
        """
        turno = self._buscar_turno(turno_id)
        if turno is None:
            raise ValueError(f"Turno '{turno_id}' no encontrado")

        if turno.estado == EstadoTurno.CANCELADO:
            raise ValueError(f"El turno '{turno_id}' ya está cancelado")

        if not turno.puede_cancelarse():
            raise ValueError(
                f"No se puede cancelar el turno '{turno_id}': "
                f"faltan menos de {HORAS_MINIMAS_CANCELACION}hs. "
                f"Turno: {turno.fecha} {turno.hora.strftime('%H:%M')}"
            )

        turno.estado = EstadoTurno.CANCELADO
        return turno

    def turnos_disponibles(
        self, especialidad: Especialidad, fecha: datetime.date
    ) -> list[dict]:
        """Muestra horarios disponibles para una especialidad en una fecha.

        Trazabilidad: REQ-F05
        Criterio: al seleccionar especialidad, se muestran solo
        los horarios disponibles de esa especialidad.
        """
        medicos_esp = [
            m for m in self._medicos
            if m.especialidad == especialidad
        ]

        disponibles = []
        for medico in medicos_esp:
            for hora in HORARIOS_DISPONIBLES:
                if not self._horario_ocupado(
                    medico.matricula, fecha, hora
                ):
                    disponibles.append({
                        "medico": medico.nombre,
                        "matricula": medico.matricula,
                        "hora": hora.strftime("%H:%M"),
                        "especialidad": especialidad.value,
                    })

        return disponibles

    def turnos_del_paciente(self, paciente_dni: str) -> list[Turno]:
        """Lista los turnos de un paciente."""
        return [
            t for t in self._turnos
            if t.paciente_dni == paciente_dni
            and t.estado == EstadoTurno.AGENDADO
        ]

    # ── Métodos auxiliares privados ──────────────────────────

    def _buscar_medico(self, matricula: str) -> Optional[Medico]:
        for m in self._medicos:
            if m.matricula == matricula:
                return m
        return None

    def _buscar_turno(self, turno_id: str) -> Optional[Turno]:
        for t in self._turnos:
            if t.turno_id == turno_id:
                return t
        return None

    def _horario_ocupado(
        self, matricula: str, fecha: datetime.date, hora: datetime.time
    ) -> bool:
        return any(
            t.medico.matricula == matricula
            and t.fecha == fecha
            and t.hora == hora
            and t.estado == EstadoTurno.AGENDADO
            for t in self._turnos
        )
