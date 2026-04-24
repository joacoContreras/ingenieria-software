#!/usr/bin/env python3
"""Análisis de Impacto — Simulación de cambio de requerimiento.

Simula qué pasa cuando el cliente cambia REQ-F04:
  ANTES: "Cancelar turno hasta 24hs antes"
  DESPUÉS: "Cancelar turno hasta 12hs antes"

El script muestra:
  1. Qué requerimiento cambia
  2. Qué archivos de código se impactan
  3. Qué tests se deben actualizar
  4. Estimación del esfuerzo

Ingeniería de Software II — Clase 11 (Taller de Trazabilidad)
"""

import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))

# ── Definición del cambio ────────────────────────────────────

CAMBIO = {
    "req_id": "REQ-F04",
    "titulo": "Cambio en regla de cancelación de turnos",
    "solicitante": "Director del Hospital",
    "fecha": "2026-05-20",
    "antes": "Permitir cancelar un turno hasta 24hs antes",
    "despues": "Permitir cancelar un turno hasta 12hs antes",
    "justificacion": (
        "Los pacientes se quejan de que 24hs es muy restrictivo. "
        "El director quiere dar más flexibilidad."
    ),
}


def buscar_impacto_en_archivo(archivo, patron):
    """Busca líneas impactadas por el cambio."""
    impactos = []
    nombre = os.path.basename(archivo)
    with open(archivo, "r", encoding="utf-8") as f:
        for num, linea in enumerate(f, 1):
            if re.search(patron, linea, re.IGNORECASE):
                impactos.append({
                    "archivo": nombre,
                    "linea": num,
                    "contenido": linea.strip(),
                })
    return impactos


def ejecutar_analisis():
    """Ejecuta el análisis de impacto completo."""
    print("=" * 80)
    print("  ANÁLISIS DE IMPACTO — Cambio de Requerimiento")
    print("=" * 80)
    print()

    # ── 1. Descripción del cambio ────────────────────────────
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  1. DESCRIPCIÓN DEL CAMBIO                             ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"  Requerimiento:  {CAMBIO['req_id']}")
    print(f"  Solicitante:    {CAMBIO['solicitante']}")
    print(f"  Fecha:          {CAMBIO['fecha']}")
    print(f"  ANTES:          {CAMBIO['antes']}")
    print(f"  DESPUÉS:        {CAMBIO['despues']}")
    print(f"  Justificación:  {CAMBIO['justificacion']}")
    print()

    # ── 2. Archivos de código impactados ─────────────────────
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  2. CÓDIGO FUENTE IMPACTADO                            ║")
    print("╚══════════════════════════════════════════════════════════╝")

    archivos_codigo = [
        os.path.join(BASE, "turnos.py"),
        os.path.join(BASE, "pacientes.py"),
        os.path.join(BASE, "notificaciones.py"),
        os.path.join(BASE, "requisitos.py"),
    ]

    # Buscar referencias a REQ-F04, 24hs, HORAS_MINIMAS_CANCELACION
    patrones = [r"REQ[-_]F04", r"24", r"HORAS_MINIMAS_CANCELACION"]
    total_impactos_codigo = 0

    for archivo in archivos_codigo:
        for patron in patrones:
            impactos = buscar_impacto_en_archivo(archivo, patron)
            for imp in impactos:
                print(f"  📄 {imp['archivo']}:{imp['linea']}  →  "
                      f"{imp['contenido'][:60]}")
                total_impactos_codigo += 1

    print(f"\n  Total líneas impactadas en código: {total_impactos_codigo}")
    print()

    # ── 3. Tests impactados ──────────────────────────────────
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  3. TESTS IMPACTADOS                                   ║")
    print("╚══════════════════════════════════════════════════════════╝")

    archivos_tests = [
        os.path.join(BASE, "tests", "test_turnos.py"),
        os.path.join(BASE, "tests", "test_pacientes.py"),
        os.path.join(BASE, "tests", "test_notificaciones.py"),
    ]

    total_impactos_tests = 0
    for archivo in archivos_tests:
        for patron in [r"REQ[-_]F04", r"24", r"cancelar", r"cancelacion"]:
            impactos = buscar_impacto_en_archivo(archivo, patron)
            for imp in impactos:
                print(f"  🧪 {imp['archivo']}:{imp['linea']}  →  "
                      f"{imp['contenido'][:60]}")
                total_impactos_tests += 1

    print(f"\n  Total líneas impactadas en tests: {total_impactos_tests}")
    print()

    # ── 4. Plan de acción ────────────────────────────────────
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  4. PLAN DE ACCIÓN                                     ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    print("  Cambios necesarios:")
    print()
    print("  📄 turnos.py:")
    print("     • Cambiar HORAS_MINIMAS_CANCELACION de 24 a 12")
    print("     • Verificar que puede_cancelarse() usa la constante")
    print("     • Actualizar mensaje de error en cancelar_turno()")
    print()
    print("  📄 requisitos.py:")
    print("     • Actualizar descripción de REQ-F04")
    print("     • Actualizar criterio de aceptación")
    print()
    print("  📄 notificaciones.py:")
    print("     • Actualizar texto de confirmación que dice '24hs'")
    print()
    print("  🧪 tests/test_turnos.py:")
    print("     • Actualizar TC-009: constante esperada → 12")
    print("     • Agregar test para el nuevo límite de 12hs")
    print("     • Verificar TC-007 y TC-008 con el nuevo umbral")
    print()

    # ── 5. Estimación ────────────────────────────────────────
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  5. ESTIMACIÓN DE ESFUERZO                             ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    print("  Archivos a modificar:    4 (turnos.py, requisitos.py, "
          "notificaciones.py, test_turnos.py)")
    print(f"  Líneas impactadas:       ~{total_impactos_codigo + total_impactos_tests}")
    print("  Esfuerzo estimado:       2 horas (desarrollo + testing)")
    print("  Riesgo:                  BAJO (cambio de constante aislado)")
    print()
    print("  ✅ CONCLUSIÓN: Gracias a la trazabilidad, el cambio es")
    print("     acotado y predecible. Sin trazabilidad, habría que")
    print("     buscar manualmente en todo el proyecto.")
    print()
    print("=" * 80)


if __name__ == "__main__":
    ejecutar_analisis()
