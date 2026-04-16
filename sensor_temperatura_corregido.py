"""Sistema de Monitoreo de Sensores IoT — Planta Industrial
Módulo de lectura, almacenamiento y alertas de temperatura.
Versión 0.9 — Febrero 2026
NOTA: Código con problemas intencionales para análisis de calidad."""

import datetime
import json
import logging
import math
import random

logging.basicConfig(filename="sensores.log", level=logging.DEBUG)

SENSORES = {}
LECTURAS = []
ALERTAS = []
UMBRAL_CRITICO = 80
UMBRAL_ADVERTENCIA = 60


def registrar_sensor(sensor_id, ubicacion, tipo, rango_min, rango_max):
    """Registra un nuevo sensor"""
    SENSORES[sensor_id] = {
        "id": sensor_id,
        "ubicacion": ubicacion,
        "tipo": tipo,
        "rango_min": rango_min,
        "rango_max": rango_max,
        "estado": "ACTIVO",
        "ultima_lectura": None,
        "fecha_registro": str(datetime.datetime.now()),
    }
    logging.info("Sensor registrado: %s en %s", sensor_id, ubicacion)
    return True


def leer_temperatura(sensor_id):
    """Simula lectura de temperatura de un sensor"""
    if sensor_id not in SENSORES:
        return None

    sensor = SENSORES[sensor_id]
    if sensor["estado"] != "ACTIVO":
        return None

    # Simular lectura
    temp = random.uniform(sensor["rango_min"], sensor["rango_max"])
    lectura = {
        "sensor_id": sensor_id,
        "temperatura": round(temp, 2),
        "timestamp": str(datetime.datetime.now()),
        "unidad": "C",
    }
    LECTURAS.append(lectura)
    SENSORES[sensor_id]["ultima_lectura"] = lectura
    logging.debug(f"Lectura sensor {sensor_id}: {temp}°C")

    # Verificar alertas
    if temp >= UMBRAL_CRITICO:
        alerta = {
            "sensor_id": sensor_id,
            "tipo": "CRITICA",
            "temperatura": temp,
            "timestamp": lectura["timestamp"],
            "mensaje": (
                f"TEMPERATURA CRÍTICA en {sensor['ubicacion']}: {temp}°C"
            ),
        }
        ALERTAS.append(alerta)
        logging.critical(f"ALERTA CRITICA: Sensor {sensor_id} = {temp}°C")
    elif temp >= UMBRAL_ADVERTENCIA:
        alerta = {
            "sensor_id": sensor_id,
            "tipo": "ADVERTENCIA",
            "temperatura": temp,
            "timestamp": lectura["timestamp"],
            "mensaje": f"Temperatura alta en {sensor['ubicacion']}: {temp}°C",
        }
        ALERTAS.append(alerta)
        logging.warning(f"ADVERTENCIA: Sensor {sensor_id} = {temp}°C")

    return lectura


def leer_todos():
    """Lee temperatura de todos los sensores activos"""
    resultados = []
    for sensor_id, sensor in SENSORES.items():
        if sensor["estado"] == "ACTIVO":
            lectura = leer_temperatura(sensor_id)
            if lectura is not None:
                resultados.append(lectura)

    return resultados


def promedio_sensor(sensor_id, ultimas_n=10):
    lecturas_sensor = [
        lectura["temperatura"]
        for lectura in LECTURAS
        if lectura["sensor_id"] == sensor_id
    ]
    if not lecturas_sensor:
        return 0

    ultimas = lecturas_sensor[-ultimas_n:]
    return sum(ultimas) / len(ultimas)


def detectar_anomalias(sensor_id, ventana=20, factor=2):
    """Detecta anomalías usando desviación estándar"""
    lecturas_sensor = [
        lectura["temperatura"]
        for lectura in LECTURAS
        if lectura["sensor_id"] == sensor_id
    ]
    if len(lecturas_sensor) < ventana:
        return []

    ultimas = lecturas_sensor[-ventana:]
    prom = sum(ultimas) / len(ultimas)

    # Calcular desvío
    suma = 0
    for valor in ultimas:
        suma = suma + (valor - prom) ** 2

    desvio = math.sqrt(suma / len(ultimas))

    # Detectar anomalías
    anomalias = []
    for indice, valor in enumerate(ultimas):
        if abs(valor - prom) > factor * desvio:
            anomalias.append(
                {
                    "indice": indice,
                    "valor": valor,
                    "promedio": prom,
                    "desvio": desvio,
                }
            )

    return anomalias


def _temperaturas_hoy(sensor_id, hoy):
    """Obtiene las temperaturas del día para un sensor."""
    return [
        lectura["temperatura"]
        for lectura in LECTURAS
        if (
            lectura["sensor_id"] == sensor_id
            and lectura["timestamp"][:10] == hoy
        )
    ]


def reporte_diario():
    """Genera reporte diario de todos los sensores"""
    hoy = str(datetime.date.today())
    reporte = {
        "fecha": hoy,
        "sensores": [],
        "alertas_del_dia": 0,
        "temperatura_maxima": -999,
        "temperatura_minima": 999,
    }

    for sensor_id, sensor in SENSORES.items():
        lecturas_hoy = _temperaturas_hoy(sensor_id, hoy)
        if lecturas_hoy:
            prom = sum(lecturas_hoy) / len(lecturas_hoy)
            mx = max(lecturas_hoy)
            mn = min(lecturas_hoy)

            if mx > reporte["temperatura_maxima"]:
                reporte["temperatura_maxima"] = mx
            if mn < reporte["temperatura_minima"]:
                reporte["temperatura_minima"] = mn

            reporte["sensores"].append(
                {
                    "sensor_id": sensor_id,
                    "ubicacion": sensor["ubicacion"],
                    "lecturas": len(lecturas_hoy),
                    "promedio": round(prom, 2),
                    "maximo": round(mx, 2),
                    "minimo": round(mn, 2),
                }
            )

    # Contar alertas del día
    reporte["alertas_del_dia"] = sum(
        1 for alerta in ALERTAS if alerta["timestamp"][:10] == hoy
    )

    return reporte


def calibrar_sensor(sensor_id, offset):
    """Aplica calibración a un sensor"""
    if sensor_id not in SENSORES:
        return False

    SENSORES[sensor_id]["calibracion_offset"] = offset
    logging.info(f"Sensor {sensor_id} calibrado con offset {offset}")
    return True


def desactivar_sensor(sensor_id):
    if sensor_id not in SENSORES:
        return False

    SENSORES[sensor_id]["estado"] = "INACTIVO"
    return True


def exportar_lecturas(ruta):
    try:
        with open(ruta, "w", encoding="utf-8") as archivo:
            json.dump(LECTURAS, archivo, ensure_ascii=False)
    except OSError as error:
        logging.error("Error al exportar lecturas en %s: %s", ruta, error)
        print("Error al exportar")


def importar_lecturas(ruta):
    global LECTURAS

    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            LECTURAS = json.load(archivo)
    except (OSError, json.JSONDecodeError) as error:
        logging.error("Error al importar lecturas en %s: %s", ruta, error)
        print("Error al importar")
