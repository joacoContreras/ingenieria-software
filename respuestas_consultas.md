# Respuestas a consignas

## a) `flake8 sensor_temperatura.py`

- Total de problemas detectados: 28
- Los 3 códigos de error más frecuentes:
  - E302 (cantidad: 10)
  - E501 (cantidad: 7)
  - E741 (cantidad: 4)
- El problema más grave según mi criterio: E722, porque usa `except` genérico en `exportar_lecturas` e `importar_lecturas` y puede ocultar fallos reales, dificultando el diagnóstico.

b) Ejecutar radon cc sensor_temperatura.py -s y completar:
Hay funciones con complejidad C o superior? _No hay funciones de complejidad C o superior__
Cual es la funcion con mayor complejidad?
-    F 90:0 reporte_diario - B (10)
    F 68:0 detectar_anomalias - B (7)


c) Ejecutar pytest test_sensor_temperatura.py -v y verificar: 

 -   pasan 16/16 tests





