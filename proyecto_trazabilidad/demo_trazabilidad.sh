#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# DEMO: Pipeline de Trazabilidad — Sistema TurnosWeb
# Ingeniería de Software II — Clase 11
# ═══════════════════════════════════════════════════════════════
# Este script demuestra trazabilidad automatizada:
#   1. Tests por requerimiento (pytest -m)
#   2. Generación de RTM automática
#   3. Análisis de impacto ante un cambio
# ═══════════════════════════════════════════════════════════════

cd "$(dirname "$0")"

echo "═══════════════════════════════════════════════════════════"
echo "  DEMO DE TRAZABILIDAD — Sistema TurnosWeb"
echo "═══════════════════════════════════════════════════════════"
echo ""

# ─── PASO 1: TESTS POR REQUERIMIENTO ───────────────────────
echo "╔══════════════════════════════════════╗"
echo "║  PASO 1: TESTS POR REQUERIMIENTO   ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "→ Ejecutando SOLO tests de REQ-F04 (cancelación de turnos):"
echo "  Comando: pytest -m REQ_F04 -v"
echo "─────────────────────────────────────────"
pytest -m REQ_F04 -v 2>&1
echo ""
echo "→ Esto demuestra TRAZABILIDAD: podemos correr los tests"
echo "  de UN requerimiento específico."
echo ""

# ─── PASO 2: TODOS LOS TESTS ───────────────────────────────
echo "╔══════════════════════════════════════╗"
echo "║  PASO 2: TODOS LOS TESTS           ║"
echo "╚══════════════════════════════════════╝"
echo ""
pytest -v --tb=short 2>&1
echo ""

# ─── PASO 3: GENERAR RTM ───────────────────────────────────
echo "╔══════════════════════════════════════╗"
echo "║  PASO 3: MATRIZ DE TRAZABILIDAD    ║"
echo "╚══════════════════════════════════════╝"
echo ""
python3 generar_rtm.py 2>&1
echo ""

# ─── PASO 4: ANÁLISIS DE IMPACTO ───────────────────────────
echo "╔══════════════════════════════════════╗"
echo "║  PASO 4: ANÁLISIS DE IMPACTO       ║"
echo "╚══════════════════════════════════════╝"
echo ""
python3 analisis_impacto.py 2>&1
echo ""

# ─── RESUMEN ────────────────────────────────────────────────
echo "═══════════════════════════════════════════════════════════"
echo "  RESUMEN DE LA DEMO"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "  Lo que vieron:"
echo "  1. pytest -m REQ_F04 → ejecutar tests de UN requerimiento"
echo "  2. generar_rtm.py    → RTM automática desde el código"
echo "  3. analisis_impacto  → saber QUÉ cambia si cambia un REQ"
echo ""
echo "  Esto es lo que hace una fábrica de software moderna:"
echo "  la trazabilidad NO vive en un Excel, vive en el CÓDIGO."
echo ""
echo "═══════════════════════════════════════════════════════════"
