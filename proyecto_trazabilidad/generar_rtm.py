#!/usr/bin/env python3
"""Genera la Matriz de Trazabilidad de Requerimientos (RTM) automáticamente.

Lee los archivos del proyecto y construye la RTM cruzando:
  - Requerimientos (requisitos.py)
  - Código fuente (pacientes.py, turnos.py, notificaciones.py)
  - Tests (tests/*.py)

Demuestra cómo una "fábrica de software" puede automatizar la trazabilidad.

Ingeniería de Software II — Clase 11 (Taller de Trazabilidad)
"""

import os
import re
from requisitos import REQUERIMIENTOS

BASE = os.path.dirname(os.path.abspath(__file__))

# Archivos de código fuente a analizar
ARCHIVOS_CODIGO = [
    os.path.join(BASE, "pacientes.py"),
    os.path.join(BASE, "turnos.py"),
    os.path.join(BASE, "notificaciones.py"),
]

# Archivos de tests
ARCHIVOS_TESTS = [
    os.path.join(BASE, "tests", "test_pacientes.py"),
    os.path.join(BASE, "tests", "test_turnos.py"),
    os.path.join(BASE, "tests", "test_notificaciones.py"),
]


def buscar_referencias(archivos, patron):
    """Busca un patrón en una lista de archivos y retorna las coincidencias."""
    resultados = []
    for archivo in archivos:
        nombre = os.path.basename(archivo)
        with open(archivo, "r", encoding="utf-8") as f:
            for num_linea, linea in enumerate(f, 1):
                if re.search(patron, linea, re.IGNORECASE):
                    resultados.append(f"{nombre}:{num_linea}")
    return resultados


def buscar_tests_por_marker(archivos, req_id):
    """Busca tests marcados con un requerimiento específico."""
    # Buscar @pytest.mark.REQ_F01 (con guión bajo en vez de guión)
    marker = req_id.replace("-", "_")
    tests = []
    for archivo in archivos:
        nombre = os.path.basename(archivo)
        with open(archivo, "r", encoding="utf-8") as f:
            lineas = f.readlines()
        for i, linea in enumerate(lineas):
            if f"mark.{marker}" in linea:
                # Buscar el nombre del test en la siguiente línea def
                for j in range(i + 1, min(i + 5, len(lineas))):
                    if "def test_" in lineas[j]:
                        nombre_test = re.search(
                            r"def (test_\w+)", lineas[j]
                        )
                        if nombre_test:
                            tests.append(
                                f"{nombre}::{nombre_test.group(1)}"
                            )
                        break
    return tests


def generar_rtm():
    """Genera y muestra la Matriz de Trazabilidad completa."""
    print("=" * 100)
    print("  MATRIZ DE TRAZABILIDAD DE REQUERIMIENTOS (RTM)")
    print("  Sistema TurnosWeb — Hospital Provincial de Córdoba")
    print("=" * 100)
    print()

    # Encabezado
    print(f"{'REQ-ID':<10} {'Tipo':<15} {'Estado':<14} "
          f"{'Módulo':<15} {'Código':<30} {'Tests':<5} {'Gaps'}")
    print("─" * 100)

    gaps_encontrados = []
    total_reqs = len(REQUERIMIENTOS)
    reqs_con_codigo = 0
    reqs_con_tests = 0

    for req_id, req in REQUERIMIENTOS.items():
        # Buscar referencias en código
        patron_codigo = req_id.replace("-", "[-_]")
        refs_codigo = buscar_referencias(ARCHIVOS_CODIGO, patron_codigo)

        # Buscar tests asociados
        tests = buscar_tests_por_marker(ARCHIVOS_TESTS, req_id)

        # Determinar módulo
        modulo = req.modulo or "—"

        # Contar métricas
        tiene_codigo = len(refs_codigo) > 0 or req.modulo is not None
        tiene_tests = len(tests) > 0

        if tiene_codigo:
            reqs_con_codigo += 1
        if tiene_tests:
            reqs_con_tests += 1

        # Detectar gaps
        gap_msg = ""
        if not tiene_codigo and req.tipo.value == "Funcional":
            gap_msg = "⚠️  SIN CÓDIGO"
            gaps_encontrados.append(
                f"{req_id}: No tiene implementación en código"
            )
        if not tiene_tests:
            if gap_msg:
                gap_msg += " | "
            gap_msg += "⚠️  SIN TESTS"
            gaps_encontrados.append(
                f"{req_id}: No tiene tests asociados"
            )

        # Formatear código (primeras 2 refs)
        codigo_str = ", ".join(refs_codigo[:2]) if refs_codigo else "—"

        print(f"{req_id:<10} {req.tipo.value:<15} {req.estado.value:<14} "
              f"{modulo:<15} {codigo_str:<30} {len(tests):<5} {gap_msg}")

    # Resumen
    print()
    print("=" * 100)
    print("  MÉTRICAS DE TRAZABILIDAD")
    print("=" * 100)
    print(f"  Total de requerimientos:        {total_reqs}")
    print(f"  Con código asociado:            {reqs_con_codigo} "
          f"({100*reqs_con_codigo//total_reqs}%)")
    print(f"  Con tests asociados:            {reqs_con_tests} "
          f"({100*reqs_con_tests//total_reqs}%)")
    print(f"  Cobertura de trazabilidad:      "
          f"{100*reqs_con_tests//total_reqs}%")
    print()

    if gaps_encontrados:
        print("  ⚠️  GAPS DETECTADOS:")
        for gap in gaps_encontrados:
            print(f"     • {gap}")
    else:
        print("  ✅ Sin gaps detectados")

    print()
    print("=" * 100)

    return gaps_encontrados


if __name__ == "__main__":
    generar_rtm()
