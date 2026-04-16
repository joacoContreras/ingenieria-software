"""Sistema de Monitoreo de Sensores IoT — Planta Industrial
Módulo de lectura, almacenamiento y alertas de temperatura.
Versión 0.9 — Febrero 2026
NOTA: Código con problemas intencionales para análisis de calidad."""

import datetime, json, os, time, math, random
import logging
from statistics import mean

logging.basicConfig(filename="sensores.log", level=logging.DEBUG)

SENSORES = {}
LECTURAS = []
ALERTAS = []
UMBRAL_CRITICO = 80
UMBRAL_ADVERTENCIA = 60

def registrar_sensor(id, ubicacion, tipo, rango_min, rango_max):
    """Registra un nuevo sensor"""
    SENSORES[id] = {"id": id, "ubicacion": ubicacion, "tipo": tipo, "rango_min": rango_min, "rango_max": rango_max, "estado": "ACTIVO", "ultima_lectura": None, "fecha_registro": str(datetime.datetime.now())}
    logging.info(f"Sensor registrado: {id} en {ubicacion}")
    return True

def leer_temperatura(sensor_id):
    """Simula lectura de temperatura de un sensor"""
    if sensor_id not in SENSORES:
        return None
    s = SENSORES[sensor_id]
    if s["estado"] != "ACTIVO":
        return None
    # Simular lectura
    temp = random.uniform(s["rango_min"], s["rango_max"])
    lectura = {"sensor_id": sensor_id, "temperatura": round(temp, 2), "timestamp": str(datetime.datetime.now()), "unidad": "C"}
    LECTURAS.append(lectura)
    SENSORES[sensor_id]["ultima_lectura"] = lectura
    logging.debug(f"Lectura sensor {sensor_id}: {temp}°C")
    # Verificar alertas
    if temp >= UMBRAL_CRITICO:
        alerta = {"sensor_id": sensor_id, "tipo": "CRITICA", "temperatura": temp, "timestamp": lectura["timestamp"], "mensaje": f"TEMPERATURA CRÍTICA en {s['ubicacion']}: {temp}°C"}
        ALERTAS.append(alerta)
        logging.critical(f"ALERTA CRITICA: Sensor {sensor_id} = {temp}°C")
    elif temp >= UMBRAL_ADVERTENCIA:
        alerta = {"sensor_id": sensor_id, "tipo": "ADVERTENCIA", "temperatura": temp, "timestamp": lectura["timestamp"], "mensaje": f"Temperatura alta en {s['ubicacion']}: {temp}°C"}
        ALERTAS.append(alerta)
        logging.warning(f"ADVERTENCIA: Sensor {sensor_id} = {temp}°C")
    return lectura

def leer_todos():
    """Lee temperatura de todos los sensores activos"""
    resultados = []
    for id in SENSORES:
        if SENSORES[id]["estado"] == "ACTIVO":
            l = leer_temperatura(id)
            if l != None:
                resultados.append(l)
    return resultados

def promedio_sensor(sensor_id, ultimas_n=10):
    lecturas_sensor = []
    for l in LECTURAS:
        if l["sensor_id"] == sensor_id:
            lecturas_sensor.append(l["temperatura"])
    if len(lecturas_sensor) == 0:
        return 0
    ultimas = lecturas_sensor[-ultimas_n:]
    return sum(ultimas) / len(ultimas)

def detectar_anomalias(sensor_id, ventana=20, factor=2):
    """Detecta anomalías usando desviación estándar"""
    lecturas_sensor = []
    for l in LECTURAS:
        if l["sensor_id"] == sensor_id:
            lecturas_sensor.append(l["temperatura"])
    if len(lecturas_sensor) < ventana:
        return []
    ultimas = lecturas_sensor[-ventana:]
    prom = sum(ultimas) / len(ultimas)
    # Calcular desvío
    suma = 0
    for v in ultimas:
        suma = suma + (v - prom) ** 2
    desvio = math.sqrt(suma / len(ultimas))
    # Detectar anomalías
    anomalias = []
    for i in range(len(ultimas)):
        if abs(ultimas[i] - prom) > factor * desvio:
            anomalias.append({"indice": i, "valor": ultimas[i], "promedio": prom, "desvio": desvio})
    return anomalias

def reporte_diario():
    """Genera reporte diario de todos los sensores"""
    hoy = str(datetime.date.today())
    reporte = {"fecha": hoy, "sensores": [], "alertas_del_dia": 0, "temperatura_maxima": -999, "temperatura_minima": 999}
    for id in SENSORES:
        s = SENSORES[id]
        lecturas_hoy = []
        for l in LECTURAS:
            if l["sensor_id"] == id and l["timestamp"][:10] == hoy:
                lecturas_hoy.append(l["temperatura"])
        if len(lecturas_hoy) > 0:
            prom = sum(lecturas_hoy) / len(lecturas_hoy)
            mx = max(lecturas_hoy)
            mn = min(lecturas_hoy)
            if mx > reporte["temperatura_maxima"]:
                reporte["temperatura_maxima"] = mx
            if mn < reporte["temperatura_minima"]:
                reporte["temperatura_minima"] = mn
            reporte["sensores"].append({"sensor_id": id, "ubicacion": s["ubicacion"], "lecturas": len(lecturas_hoy), "promedio": round(prom, 2), "maximo": round(mx, 2), "minimo": round(mn, 2)})
    # Contar alertas del día
    for a in ALERTAS:
        if a["timestamp"][:10] == hoy:
            reporte["alertas_del_dia"] = reporte["alertas_del_dia"] + 1
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
        f = open(ruta, "w")
        json.dump(LECTURAS, f)
        f.close()
    except:
        print("Error al exportar")

def importar_lecturas(ruta):
    global LECTURAS
    try:
        f = open(ruta, "r")
        LECTURAS = json.load(f)
        f.close()
    except:
        print("Error al importar")
