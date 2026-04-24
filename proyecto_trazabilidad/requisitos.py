"""Definición de requerimientos del sistema TurnosWeb.

Cada requerimiento tiene: ID, tipo, descripción, prioridad, fuente y criterio.
Este archivo actúa como la "fuente de verdad" de los requerimientos.

Usado en: Ingeniería de Software II — Clase 11 (Taller de Trazabilidad)
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class TipoReq(Enum):
    FUNCIONAL = "Funcional"
    NO_FUNCIONAL = "No Funcional"
    NEGOCIO = "Negocio"


class Prioridad(Enum):
    ALTA = "Alta"
    MEDIA = "Media"
    BAJA = "Baja"


class EstadoReq(Enum):
    PROPUESTO = "Propuesto"
    APROBADO = "Aprobado"
    IMPLEMENTADO = "Implementado"
    VERIFICADO = "Verificado"
    DIFERIDO = "Diferido"


@dataclass
class Requerimiento:
    """Representa un requerimiento del sistema."""
    req_id: str
    tipo: TipoReq
    descripcion: str
    prioridad: Prioridad
    fuente: str
    criterio_aceptacion: str
    estado: EstadoReq
    modulo: Optional[str] = None        # Módulo que lo implementa
    test_cases: Optional[list] = None   # IDs de tests asociados


# ════════════════════════════════════════════════════════════════
#  CATÁLOGO DE REQUERIMIENTOS — Sistema TurnosWeb
#  Hospital Provincial de Córdoba
# ════════════════════════════════════════════════════════════════

REQUERIMIENTOS = {
    "REQ-F01": Requerimiento(
        req_id="REQ-F01",
        tipo=TipoReq.FUNCIONAL,
        descripcion="El sistema debe permitir a pacientes registrarse con nombre, DNI y fecha de nacimiento",
        prioridad=Prioridad.ALTA,
        fuente="Entrevista Dir. Hospital, 10/03/2026",
        criterio_aceptacion="Dado un paciente nuevo, al ingresar nombre/DNI/fecha válidos, el sistema confirma el registro",
        estado=EstadoReq.VERIFICADO,
        modulo="pacientes",
        test_cases=["TC-001", "TC-002", "TC-003"],
    ),
    "REQ-F02": Requerimiento(
        req_id="REQ-F02",
        tipo=TipoReq.FUNCIONAL,
        descripcion="El sistema debe permitir agendar turno eligiendo especialidad, médico, fecha y hora",
        prioridad=Prioridad.ALTA,
        fuente="Entrevista Dir. Hospital, 10/03/2026",
        criterio_aceptacion="Dado un paciente registrado y un horario disponible, el turno se agenda y aparece en la agenda del médico",
        estado=EstadoReq.VERIFICADO,
        modulo="turnos",
        test_cases=["TC-004", "TC-005"],
    ),
    "REQ-F03": Requerimiento(
        req_id="REQ-F03",
        tipo=TipoReq.FUNCIONAL,
        descripcion="El sistema debe enviar confirmación del turno al paciente (email o SMS)",
        prioridad=Prioridad.MEDIA,
        fuente="Entrevista Recepción, 12/03/2026",
        criterio_aceptacion="Al agendar un turno, el paciente recibe un mensaje con fecha, hora y médico",
        estado=EstadoReq.IMPLEMENTADO,
        modulo="notificaciones",
        test_cases=["TC-006"],
    ),
    "REQ-F04": Requerimiento(
        req_id="REQ-F04",
        tipo=TipoReq.FUNCIONAL,
        descripcion="El sistema debe permitir cancelar un turno hasta 24hs antes de la hora programada",
        prioridad=Prioridad.ALTA,
        fuente="Resolución Interna 42/2026, Dir. Hospital",
        criterio_aceptacion="Dado un turno a las 14:00 del jueves, si se cancela a las 13:00 del miércoles, el sistema confirma cancelación y libera el horario",
        estado=EstadoReq.VERIFICADO,
        modulo="turnos",
        test_cases=["TC-007", "TC-008", "TC-009"],
    ),
    "REQ-F05": Requerimiento(
        req_id="REQ-F05",
        tipo=TipoReq.FUNCIONAL,
        descripcion="El sistema debe mostrar turnos disponibles filtrados por especialidad",
        prioridad=Prioridad.MEDIA,
        fuente="Entrevista Recepción, 12/03/2026",
        criterio_aceptacion="Al seleccionar una especialidad, se muestran solo los horarios disponibles de esa especialidad",
        estado=EstadoReq.IMPLEMENTADO,
        modulo="turnos",
        test_cases=["TC-010"],
    ),
    "REQ-F06": Requerimiento(
        req_id="REQ-F06",
        tipo=TipoReq.FUNCIONAL,
        descripcion="El sistema debe generar un reporte diario de turnos por médico",
        prioridad=Prioridad.BAJA,
        fuente="Entrevista Jefe de Guardia, 15/03/2026",
        criterio_aceptacion="Al solicitar el reporte, se genera un listado con paciente, hora y especialidad para cada médico",
        estado=EstadoReq.PROPUESTO,  # ← ¡GAP! No implementado aún
        modulo=None,
        test_cases=None,
    ),
    "REQ-NF01": Requerimiento(
        req_id="REQ-NF01",
        tipo=TipoReq.NO_FUNCIONAL,
        descripcion="El tiempo de carga de cualquier pantalla no debe superar 3 segundos en horario pico",
        prioridad=Prioridad.ALTA,
        fuente="Licitación Pública LP-2026-001, cláusula 7.2",
        criterio_aceptacion="Bajo carga de 500 usuarios simultáneos, ninguna pantalla supera 3s de tiempo de respuesta",
        estado=EstadoReq.DIFERIDO,
        modulo=None,
        test_cases=None,
    ),
    "REQ-NF02": Requerimiento(
        req_id="REQ-NF02",
        tipo=TipoReq.NO_FUNCIONAL,
        descripcion="Los datos personales (DNI, nombre) deben almacenarse cifrados en la base de datos",
        prioridad=Prioridad.ALTA,
        fuente="Ley 25.326 Protección de Datos Personales",
        criterio_aceptacion="Al consultar la BD directamente, los campos nombre y DNI no son legibles en texto plano",
        estado=EstadoReq.IMPLEMENTADO,
        modulo="pacientes",
        test_cases=["TC-011"],
    ),
    "REQ-N01": Requerimiento(
        req_id="REQ-N01",
        tipo=TipoReq.NEGOCIO,
        descripcion="Reducir en 60% los turnos agendados por teléfono",
        prioridad=Prioridad.ALTA,
        fuente="Plan Estratégico Hospital 2026",
        criterio_aceptacion="A los 6 meses de implementación, el 60% de los turnos se agendan por el sistema web",
        estado=EstadoReq.APROBADO,
        modulo=None,
        test_cases=None,
    ),
    "REQ-N02": Requerimiento(
        req_id="REQ-N02",
        tipo=TipoReq.NEGOCIO,
        descripcion="Disminuir el ausentismo a turnos en un 30% mediante recordatorios automáticos",
        prioridad=Prioridad.MEDIA,
        fuente="Plan Estratégico Hospital 2026",
        criterio_aceptacion="A los 6 meses, la tasa de ausentismo baja de 35% a menos de 25%",
        estado=EstadoReq.APROBADO,
        modulo="notificaciones",
        test_cases=None,
    ),
}


def mostrar_catalogo():
    """Muestra el catálogo de requerimientos formateado."""
    print("=" * 80)
    print("  CATÁLOGO DE REQUERIMIENTOS — TurnosWeb Hospital Provincial")
    print("=" * 80)
    for req_id, req in REQUERIMIENTOS.items():
        print(f"\n  {req_id} [{req.tipo.value}] — Prioridad: {req.prioridad.value}")
        print(f"  {req.descripcion}")
        print(f"  Fuente: {req.fuente}")
        print(f"  Estado: {req.estado.value}")
        if req.modulo:
            print(f"  Módulo: {req.modulo}")
        if req.test_cases:
            print(f"  Tests: {', '.join(req.test_cases)}")
        else:
            print(f"  Tests: ⚠️  SIN TESTS ASOCIADOS")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    mostrar_catalogo()
