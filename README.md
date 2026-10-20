# Análisis de ventas retail: desempeño comercial y calidad de datos

Proyecto end-to-end de análisis de ventas de una tienda retail (transacciones 2022–2024).

**Preguntas de negocio que responde el proyecto:**

1. **¿Cómo se comportan las ventas, el ticket y el mix de categorías en el tiempo?**
2. **¿Hay diferencias relevantes entre canal, método de pago y clientes?**
3. **¿Qué se puede afirmar (y qué no) sobre los descuentos con la calidad de dato disponible?**
4. **¿Dónde fallan los datos (producto no identificado, descuento sin estado) y qué implica eso para decidir?**

**Herramientas:** Python · PostgreSQL · SQL · Power BI · DAX

---

## Hallazgos clave

1. **Bebidas (Beverages) lidera el mix de ventas**  
   Es la categoría con mayor participación en $; el resto del catálogo está más repartido.

2. **El Pareto de productos es disperso**  
   Los ítems top acumulan una fracción moderada del total: no hay un “producto héroe” que concentre la venta.

3. **Canales Online e In-store están equilibrados**  
   La diferencia de participación es pequeña (~52% vs ~48% en el período analizado). No hay base fuerte para priorizar un solo canal solo con estos datos.

4. **Métodos de pago también repartidos**  
   Cash, Credit Card y Digital Wallet tienen pesos similares; no surge un medio dominante claro.

5. **Solo 25 clientes en el universo analítico**  
   Limita cualquier conclusión de “segmentación de clientes” o CRM avanzado. El valor de la página de clientes es de escala y homogeneidad, no de microsegmentos.

6. **~35% de las ventas sin estado de descuento (Unknown / sin dato)**  
   Con tickets muy parecidos entre “con descuento”, “sin descuento” y “sin dato”, **no se recomienda decidir política de descuentos** solo con este campo.

7. **~10% de las ventas con producto no identificado (Unknown)**  
   Alerta de calidad de catálogo / pipeline: el análisis a nivel ítem queda limitado; el de categoría sigue siendo usable.

8. **No hay costo en el dataset**  
   No se calcula margen ni beneficio real; el informe se centra en ventas, volumen, ticket y calidad de datos.

---

## Recomendaciones

1. **Priorizar limpieza del flag de descuento** (y, si es posible, validar descuento con precio unitario × cantidad vs total pagado).
2. **Mejorar identificación de productos Unknown** en el maestro / ETL, especialmente si se concentra en categorías de alto volumen.
3. **No sobreinterpretar canal ni pago**: el negocio se ve homogéneo en esas dimensiones.
4. **Usar el informe para explorar mix y tendencias**, no para ROI de descuentos ni rentabilidad por producto.
5. **Tratar enero incompleto (si aplica) fuera del calendario de análisis** para no distorsionar totales y series.

Recomendaciones **descriptivas**; no implican causalidad.

---

## Dashboard de Power BI

Archivo: `powerbi/retail_store_sales.pbix` *(ajustar ruta si en el repo es otra)*

| # | Página | Pregunta que responde |
|---|--------|------------------------|
| 1 | **Resumen ejecutivo** | ¿Cómo van ventas, ticket y qué alertas de calidad hay (% sin dato de descuento / producto)? |
| 2 | **Productos y concentración** | ¿Qué categorías e ítems concentran la venta? ¿Cuánto se vende con producto no identificado? |
| 3 | **Clientes y canal** | ¿Hay diferencia material entre Online / In-store y métodos de pago? |
| 4 | **Descuentos y límites** | ¿Qué peso tiene cada estado de descuento y por qué no se puede inferir impacto comercial? |
| 5 | **Deep dive** | Exploración con filtros (año, categoría, canal, pago, descuento) + recordatorio de límites |

**Reglas reflejadas en el informe**

- Calendario de análisis acotado a **años completos 2022–2024** (se excluye el tramo incompleto de 2025 para no distorsionar filtros y series).
- **% ventas sin dato de descuento** como KPI de alerta (rojo si ≥ 20%).
- **% ventas con producto Unknown** como alerta de calidad de catálogo.
- En descuentos: título orientado a **comparativo**, no a “impacto” causal.
- Categorías presentadas con etiquetas en español (p. ej. Bebidas, Carnicería, Informática, Hogar eléctrico, Alimentación, Muebles, Lácteos, Pastelería).

---

## Datos

| Concepto | Detalle |
|----------|---------|
| **Período de análisis** | 2022–2024 (años completos) |
| **Hechos** | Ventas, unidades, transacciones, ticket, descuento (True / False / Unknown) |
| **Dimensiones** | Producto, cliente, ubicación/canal, método de pago, calendario |
| **Clientes** | 25 en el modelo analítico |
| **Limitación estructural** | Sin costo → sin margen/beneficio |
| **Calidad** | Alto % de descuento sin dato; parte de ventas con producto Unknown |

*(Completar fuente exacta Kaggle/CSV y licencia si aplica en el repo.)*

---

## Arquitectura y método

1. **Exploración y limpieza** del origen de ventas.  
2. **Modelo dimensional** (hechos + dimensiones de producto, cliente, ubicación, pago, fecha).  
3. **Calendario de análisis** (`dim_date`) limitado a 2022-01-01 → 2024-12-31.  
4. **Medidas DAX** de ventas, transacciones, ticket, MoM/YoY, Pareto de producto, % por estado de descuento, alertas de calidad.  
5. **Informe Power BI** en cinco páginas con foco en decisión y límites del dato.

### Modelo (referencia)

- `public fact_sales` (hechos)  
- `public dim_product`, `public dim_customer`, `public dim_location`, `public dim_payment_method`  
- `dim_date` (relacionada por `date_key` / `Date Key`; time intelligence sobre `Date`)

---

## Decisiones de modelado y calidad

- Productos **Unknown** no se ocultan: se miden como % de ventas para argumentar mejora de pipeline.
- Descuento **Unknown / sin dato** se trata como estado explícito, no se imputa.
- Medidas de % por estado de descuento usan el **mismo campo de fila** en el `ALL()` (evitar el 100% por filtro incorrecto).
- Se eliminó / no se usa una medida genérica de “Cumulative Sales” incorrecta; el Pareto usa rank + acumulado por producto/cliente.
- Etiquetas de categoría en español vía Power Query (solo presentación).

---

## Limitaciones

- **Sin margen:** no hay costo en los datos.
- **Descuento incompleto:** ~1/3 de las ventas sin estado usable → no evaluar efectividad comercial del descuento.
- **Producto Unknown:** limita el análisis a nivel ítem.
- **25 clientes:** no soporta conclusiones finas de comportamiento de cliente.
- **Canales y pagos homogéneos:** el valor está en constatar equilibrio, no en un “ganador”.
- Análisis **descriptivo**, sin causalidad.

---

## Cómo reproducir el proyecto

### Requisitos

- Python (si aplica el pipeline del repo)  
- PostgreSQL (si el modelo está en BD)  
- Power BI Desktop  
- Dependencias del repositorio (`requirements.txt` si existe)

### Pasos generales

1. Clonar el repositorio.  
2. Configurar conexión a datos (CSV / PostgreSQL) sin publicar credenciales.  
3. Actualizar el modelo en Power BI.  
4. Validar KPI: ventas, ticket, % sin dato de descuento, % producto Unknown, comparativo de canales.

*(Ajustar comandos y rutas al árbol real del repo.)*

---

## Estructura del repositorio (referencia)

```text
retail-store-sales-analytics/
├── data/
├── powerbi/
│   └── retail_store_sales.pbix
├── scripts/          # si aplica
├── sql/              # si aplica
├── .gitignore
├── requirements.txt  # si aplica
├── LICENSE
└── README.md
