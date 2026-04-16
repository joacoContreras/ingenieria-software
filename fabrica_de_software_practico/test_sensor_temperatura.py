"""Tests para sensor_temperatura.py — Monitoreo IoT."""

import fabrica_de_software_practico.sensor_temperatura as st


class TestRegistrarSensor:
    def setup_method(self):
        st.SENSORES.clear()
        st.LECTURAS.clear()
        st.ALERTAS.clear()

    def test_registrar_sensor(self):
        assert st.registrar_sensor("S-001", "Horno 1", "termocupla", 20, 120) is True
        assert "S-001" in st.SENSORES

    def test_sensor_estado_activo(self):
        st.registrar_sensor("S-001", "Horno 1", "termocupla", 20, 120)
        assert st.SENSORES["S-001"]["estado"] == "ACTIVO"

    def test_sensor_datos_completos(self):
        st.registrar_sensor("S-002", "Caldera", "PT100", 0, 200)
        s = st.SENSORES["S-002"]
        assert s["ubicacion"] == "Caldera"
        assert s["rango_min"] == 0
        assert s["rango_max"] == 200


class TestLeerTemperatura:
    def setup_method(self):
        st.SENSORES.clear()
        st.LECTURAS.clear()
        st.ALERTAS.clear()
        st.registrar_sensor("S-001", "Horno 1", "termocupla", 20, 50)

    def test_lectura_valida(self):
        lectura = st.leer_temperatura("S-001")
        assert lectura is not None
        assert "temperatura" in lectura
        assert lectura["sensor_id"] == "S-001"

    def test_lectura_en_rango(self):
        lectura = st.leer_temperatura("S-001")
        assert 20 <= lectura["temperatura"] <= 50

    def test_lectura_sensor_inexistente(self):
        assert st.leer_temperatura("S-999") is None

    def test_lectura_se_acumula(self):
        st.leer_temperatura("S-001")
        st.leer_temperatura("S-001")
        assert len(st.LECTURAS) == 2


class TestAlertas:
    def setup_method(self):
        st.SENSORES.clear()
        st.LECTURAS.clear()
        st.ALERTAS.clear()
        # Sensor con rango que supera umbral crítico (80)
        st.registrar_sensor("S-HOT", "Fundición", "termocupla", 75, 95)

    def test_genera_alerta_critica(self):
        # Leer muchas veces para tener al menos una > 80
        for _ in range(50):
            st.leer_temperatura("S-HOT")
        alertas_criticas = [a for a in st.ALERTAS if a["tipo"] == "CRITICA"]
        assert len(alertas_criticas) > 0

    def test_genera_alerta_advertencia(self):
        # Sensor con rango 55-70 (puede superar umbral advertencia 60)
        st.registrar_sensor("S-WARM", "Secador", "NTC", 55, 70)
        for _ in range(50):
            st.leer_temperatura("S-WARM")
        alertas_warn = [a for a in st.ALERTAS if a["tipo"] == "ADVERTENCIA"]
        assert len(alertas_warn) > 0


class TestLeerTodos:
    def setup_method(self):
        st.SENSORES.clear()
        st.LECTURAS.clear()
        st.ALERTAS.clear()
        st.registrar_sensor("S-001", "Horno 1", "termocupla", 20, 50)
        st.registrar_sensor("S-002", "Caldera", "PT100", 30, 60)

    def test_leer_todos_activos(self):
        resultados = st.leer_todos()
        assert len(resultados) == 2

    def test_leer_todos_excluye_inactivos(self):
        st.desactivar_sensor("S-002")
        resultados = st.leer_todos()
        assert len(resultados) == 1


class TestPromedio:
    def setup_method(self):
        st.SENSORES.clear()
        st.LECTURAS.clear()
        st.ALERTAS.clear()
        st.registrar_sensor("S-001", "Horno 1", "termocupla", 20, 50)

    def test_promedio_con_lecturas(self):
        for _ in range(10):
            st.leer_temperatura("S-001")
        prom = st.promedio_sensor("S-001")
        assert 20 <= prom <= 50

    def test_promedio_sin_lecturas(self):
        assert st.promedio_sensor("S-001") == 0


class TestDesactivar:
    def setup_method(self):
        st.SENSORES.clear()
        st.registrar_sensor("S-001", "Horno 1", "termocupla", 20, 50)

    def test_desactivar(self):
        st.desactivar_sensor("S-001")
        assert st.SENSORES["S-001"]["estado"] == "INACTIVO"

    def test_desactivar_inexistente(self):
        assert st.desactivar_sensor("S-999") is False

    def test_sensor_inactivo_no_lee(self):
        st.desactivar_sensor("S-001")
        assert st.leer_temperatura("S-001") is None
