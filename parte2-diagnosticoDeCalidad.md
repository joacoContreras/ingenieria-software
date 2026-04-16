DIAGNOSTICO DE CALIDAD — GRUPO 3
====================================================
Proyecto: Monitoreo de Sensores IoT
Integrantes: Alasino Benjamin, Calvo Tomas, Contreras Joaquin
Fecha: 15/4/2026
RESUMEN FLAKE8
 Total de problemas: 28
 Imports sin usar (F401): 3
 Lineas largas (E501): 7
 Except generico (E722): 2
 Variables ambiguas (E741): 4

RESUMEN RADON
 Funcion mas compleja: reporte_diario     Complejidad: 10
 Indice de mantenibilidad global: 42.5

TOP 5 PROBLEMAS (ordenados por gravedad)
 1. Linea 134: Uso de `except` generico en `exportar_lecturas`, oculta fallos reales.
 Severidad: [x] Critico [ ] Mayor [ ] Menor [ ] Cosmetico
 Categoria: [ ] Funcionalidad [ ] Seguridad [ ] Legibilidad
 [x] Mantenibilidad [x] Buenas Practicas

 2. Linea 143: Uso de `except` generico en `importar_lecturas`, oculta fallos reales.
 Severidad: [x] Critico [ ] Mayor [ ] Menor [ ] Cosmetico
 Categoria: [ ] Funcionalidad [ ] Seguridad [ ] Legibilidad
 [x] Mantenibilidad [x] Buenas Practicas

 3. Linea 90: `reporte_diario` es la funcion mas compleja (complejidad 10).
 Severidad: [ ] Critico [x] Mayor [ ] Menor [ ] Cosmetico
 Categoria: [ ] Funcionalidad [ ] Seguridad [x] Legibilidad
 [x] Mantenibilidad [x] Buenas Practicas
 
 4. Linea 53: Variable ambigua `l` en `leer_todos`.
 Severidad: [ ] Critico [ ] Mayor [x] Menor [ ] Cosmetico
 Categoria: [ ] Funcionalidad [ ] Seguridad [x] Legibilidad
 [x] Mantenibilidad [x] Buenas Practicas
 
 5. Linea 20: Linea demasiado larga y con logica concentrada en un solo bloque.
 Severidad: [ ] Critico [ ] Mayor [ ] Menor [x] Cosmetico
 Categoria: [ ] Funcionalidad [ ] Seguridad [x] Legibilidad
 [x] Mantenibilidad [x] Buenas Practicas