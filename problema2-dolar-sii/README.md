# La ganancia que se evapora — Dólar observado SII 2022–2025

Laboratorio evaluado 1 — Análisis de error (cifras significativas, punto flotante, propagación).  
Universidad Católica del Maule.

## Objetivo
Con el promedio mensual del dólar observado SII (48 meses, 2022-01 a 2025-12, `data/dolar_observado_sii_2022_2025.csv`) se estudia:

* Error de representación al guardar con mantisa corta (2 cifras significativas, base 10, como en punto flotante).
* Propagación del error en `/` y `*` (suma de relativos) y en `-` (suma de absolutos).
* Cancelación al restar dos meses parecidos y definición de una norma arbitraria para decidir si una diferencia es concluyente.
* Utilidad real de comprar/vender dólares con `M = 1.000.000 CLP`.

> **Nota sobre cifras:** El enunciado principal exige 2 cifras (`963.44→960`, `1000.76→1000`). A3/B1 mencionan 3 cifras. El código implementa `SIG` parametrizable; por defecto `SIG=2` (norma base) y se reportan comparaciones con 3 sig en `outputs/*_3sig.csv` y en el texto.

## Estructura
```
problema2-dolar-sii/
├── README.md
├── INFORME.md
├── requirements.txt
├── data/dolar_observado_sii_2022_2025.csv
├── src/
│   ├── cargar_datos.py      # np.genfromtxt
│   ├── errores.py           # redondeo, Ea, Er, A1/A2/A3/A5
│   ├── anualidad.py         # A4
│   ├── punto_flotante.py    # B1, B2, B4
│   ├── generar_graficos.py  # 5 gráficos obligatorios
│   └── generar_tablas.py    # tablas adicionales
├── graficos/
│   ├── 01_serie_mensual.png
│   ├── 02_delta_mes_a_mes.png
│   ├── 03_error_representacion.png
│   ├── 04_rentabilidad_desde_minimo.png
│   └── 05_deriva_ida_vuelta.png
└── outputs/
    ├── errores_mensuales_2sig.csv
    ├── anualidad_2sig.csv
    ├── delta_mes_a_mes_2sig.csv
    ├── rentabilidad_desde_minimo_2sig.csv
    ├── ejemplos_compra_venta.csv
    ├── A3_cancelacion_diciembre.csv
    └── B4_float_comparacion.csv
```

## Instalación y ejecución

```bash
pip install -r requirements.txt   # numpy, matplotlib

python src/cargar_datos.py        # verifica carga con np.genfromtxt
python src/errores.py             # A1, A2, A3, A5 + tablas mensuales
python src/anualidad.py           # A4
python src/punto_flotante.py      # B1, B2, B4 + gráfico deriva
python src/generar_graficos.py    # gráficos 1-5
python src/generar_tablas.py      # tablas delta, rentabilidad, ejemplos
```

Todos los cálculos usan `numpy` vectorizado. El redondeo a N sig es vectorizado (`redondear_sig` en `src/errores.py:13`).

## Resultados rápidos (2 cifras, norma base)

| Pregunta | Resultado clave |
|---|---|
| **A1 mayor Er** | Abril 2022 `815.12→820 Ea 4.88 Er 0.599%` (top: dic23 0.534%, ago23 0.507%) |
| **A3 dic22→dic23** | `Δreal -0.99`, `Δaprox -10.00 ±9.01 Er 90.1%` (3 sig: `-1.00 ±0.67 Er 67%`) — cancelación domina |
| **A4 anualidad** | Orden confiabilidad 2sig: 2025 (5.8%) > 2024 (6.2%) > 2022 (10.6%) > 2023 (20.8%). Poco confiables 2022-2023 |
| **A5 min→max** | Min Feb-2023 `798.26`, Max Ene-2025 `1000.76`. Rent `25.00% ±0.37 Er1.5%` — **sólida** (rent >> Ea) |
| **B4** | `874.67-875.66` float32 `-0.989990 Ea 9.7e-06 (~5 cifras)` vs float64 `-0.99 Ea 9e-15` |

Ver detalle, gráficos y tablas en `INFORME.md` y `outputs/`.

## Gráficos

* `graficos/01_serie_mensual.png` — serie mensual con min/max anotados.
* `graficos/02_delta_mes_a_mes.png` — ΔP mes-a-mes con barras `±Ea`; rojo = `|Δ|≤Ea` (no concluyente).
* `graficos/03_error_representacion.png` — Ea y Er por mes (2 sig).
* `graficos/04_rentabilidad_desde_minimo.png` — rentabilidad comprando en mínimo (Feb23) y vendiendo después, con `±Ea`.
* `graficos/05_deriva_ida_vuelta.png` — deriva `M→USD→M` float32 vs float64.

## Evaluación de error

Tablas con `Ea`, `Er` y propagado: `outputs/errores_mensuales_2sig.csv`, `outputs/anualidad_2sig.csv`, `outputs/delta_mes_a_mes_2sig.csv`, `outputs/rentabilidad_desde_minimo_2sig.csv`, `outputs/ejemplos_compra_venta.csv`.

## Créditos

Datos: SII dólar observado promedio mensual 2022-2025.
