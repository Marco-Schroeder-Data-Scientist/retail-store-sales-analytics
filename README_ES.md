# Retail Store Sales Analytics

## Resumen del proyecto

**Retail Store Sales Analytics** es un proyecto de análisis de datos de principio a fin que transforma un conjunto de datos transaccionales de retail con problemas de calidad en una base analítica validada y un informe interactivo en Power BI.

El proyecto demuestra un flujo de trabajo de análisis orientado al negocio: exploración, preparación y validación de datos; modelado dimensional en PostgreSQL; definición de indicadores con DAX; y comunicación de hallazgos mediante un informe interactivo.

El análisis aborda las ventas, las categorías y productos, los clientes, los canales, los medios de pago, la evolución temporal y, de manera destacada, las limitaciones para analizar los descuentos debido a la cantidad de registros cuyo estado no está informado.

> Los datos se utilizan con fines de aprendizaje y demostración analítica. Las conclusiones describen este conjunto de datos y no deben interpretarse como evidencia sobre una empresa real.

## Objetivos

- Explorar la estructura, la calidad y las limitaciones de los datos.
- Limpiar y transformar los registros con criterios explícitos y reproducibles.
- Validar la integridad de los datos y la coherencia de las métricas de venta.
- Organizar los datos en un modelo dimensional en PostgreSQL.
- Crear medidas de negocio con DAX.
- Desarrollar un informe de Power BI que permita explorar resultados y responder preguntas comerciales.
- Comunicar hallazgos y limitaciones sin atribuir causalidad que los datos no demuestran.

## Herramientas

- **Python y pandas:** exploración, limpieza, transformación y validación.
- **PostgreSQL y SQL:** almacenamiento analítico, modelado estrella y validaciones de integridad.
- **Power BI y DAX:** medidas de negocio, análisis interactivo y visualización.
- **Jupyter Notebook:** exploración inicial y documentación del análisis.

## Conjunto de datos

El proyecto utiliza el conjunto de datos **Retail Store Sales: Dirty for Data Cleaning**, publicado en Kaggle. El conjunto original contiene 12.575 registros y 11 columnas sobre transacciones de retail.

- **Período cubierto:** 1 de enero de 2022 al 18 de enero de 2025.
- **Transacciones:** 12.575.
- **Clientes identificados:** 25.
- **Categorías:** 8.
- **Canales:** Online e In-store.
- **Medios de pago:** 3.
- **Estados de descuento en el conjunto procesado:** `True`, `False` y `Unknown` transformadas en el informe de Power BI como   `Con Descuento`, `Sin Descuento` y `Sin Dato`.

Fuente: [Kaggle — Retail Store Sales: Dirty for Data Cleaning](https://www.kaggle.com/datasets?search=Retail+Store+Sales%3A+Dirty+for+Data+Cleaning)

## Proceso de trabajo y validaciones

### 1. Inspección y análisis exploratorio

Se revisaron las dimensiones, los tipos de datos, los valores faltantes, los posibles duplicados, las distribuciones y las relaciones entre variables. Los resultados de esta etapa orientaron las decisiones de preparación.

### 2. Limpieza y transformación

El proceso incluyó:

- Normalización de nombres de columnas a `snake_case`.
- Conversión de `transaction_date` a tipo fecha.
- Conversión de variables categóricas a tipos adecuados para el análisis.
- Uso de tipos numéricos más eficientes para las métricas de venta.
- Reconstrucción de los 609 valores faltantes de `price_per_unit` cuando fue posible mediante `total_spent / quantity`.
- Imputación de los 604 valores faltantes de `quantity` mediante la mediana (6 unidades) y reconstrucción de `total_spent` a partir del precio y la cantidad.
- Tratamiento de los valores faltantes de `item` como `Unknown`.
- Conservación de los estados de descuento desconocidos como `Unknown`, sin clasificarlos arbitrariamente como `False`.

### 3. Validación de calidad

Después de la preparación se comprobó que:

- El conjunto procesado contiene 12.575 registros y 11 columnas.
- No quedan valores nulos en las columnas procesadas; cuando no fue posible recuperar la información, se conservó el valor explícito `Unknown`.
- No se encontraron transacciones duplicadas.
- La igualdad `total_spent = price_per_unit × quantity` no presentó diferencias en los 12.575 registros procesados.
- Las validaciones de integridad referencial en PostgreSQL no detectaron registros huérfanos en las relaciones comprobadas.
- Los principales indicadores de Power BI se contrastaron con consultas SQL en PostgreSQL.

La consistencia aritmética de los importes no demuestra por sí sola si se aplicó un descuento ni permite establecer que el precio unitario original corresponda siempre a un precio de lista previo al descuento.

### 4. Modelado dimensional en PostgreSQL

Los datos se organizaron en una tabla de hechos y dimensiones para facilitar el análisis por fecha, cliente, producto, ubicación/canal y medio de pago:

- `fact_sales`
- `dim_customer`
- `dim_product`
- `dim_date`
- `dim_payment_method`
- `dim_location`

El modelo permite analizar los indicadores desde distintas perspectivas y comprobar la coherencia de los resultados agregados.

## Informe de Power BI

El informe final se organiza en cinco áreas complementarias:

1. **Executive Overview:** presenta los indicadores generales y la evolución de las ventas para establecer una visión ejecutiva del comportamiento observado.
2. **Sales Performance:** permite comparar ventas, unidades y participación por categoría, además de profundizar en el desempeño de productos.
3. **Customer & Channel Behavior:** explora el comportamiento agregado de clientes y compara resultados por canal de venta y medio de pago.
4. **Discounts & Commercial Behavior:** compara ventas, transacciones y ticket promedio según el estado del descuento. Mantiene separados los estados conocidos y desconocidos para no ocultar la falta de información.
5. **Deep Dive / Interactive Analysis:** facilita el análisis exploratorio mediante filtros y comparaciones por categoría, período, canal, medio de pago y estado del descuento.

El informe combina indicadores generales, tendencias temporales y desgloses comerciales para ayudar a pasar de una visión global a preguntas más específicas. Sus resultados son descriptivos: las diferencias entre grupos no prueban por sí mismas que un canal, medio de pago o descuento haya causado un resultado determinado.

## Indicadores globales validados

Los siguientes resultados se contrastaron entre Power BI y PostgreSQL:

| Indicador | Resultado |
|---|---:|
| Ventas totales (`Total Sales`) | 1.637.367,00 |
| Transacciones (`Total Transactions`) | 12.575 |
| Unidades vendidas (`Total Units`) | 69.900 |
| Ticket promedio (`Average Transaction Value`) | 130,21 |
| Precio unitario promedio (`Average Unit Price`) | 23,37 |
| Unidades promedio por transacción (`Average Units per Transaction`) | 5,56 |

Los importes se presentan en las unidades monetarias del conjunto de datos. La fuente no especifica una moneda inequívoca, por lo que no se asigna un símbolo monetario.

## Hallazgo y limitación clave: información sobre descuentos

La columna original `Discount Applied` contenía **4.199 valores faltantes, equivalentes al 33,4 % de los registros**. Esta proporción es considerable y no se explica únicamente por la ausencia de precio unitario o cantidad, ya que esos campos tenían menos valores faltantes.

Para evitar inventar información, los estados desconocidos se conservaron como `Unknown`, separados de `True` y `False`. El informe permite comparar los indicadores disponibles por estado del descuento, pero la presencia de una categoría desconocida limita la interpretación y la evaluación comercial de los descuentos.

La coherencia entre precio unitario, cantidad e importe total no demuestra que se haya aplicado o no un descuento. Tampoco hay evidencia suficiente para asegurar que `price_per_unit` represente siempre el precio de lista anterior al descuento. Por eso, los resultados no deben interpretarse como una medición concluyente del efecto de los descuentos.

## Otras limitaciones analíticas

- **Productos desconocidos:** los registros cuyo artículo no pudo identificarse se conservan como `Unknown`. Una categoría asociada a ese valor en el modelo puede ser un artefacto técnico y no debe interpretarse como una categoría comercial real.
- **Rentabilidad:** el conjunto de datos no aporta información suficiente sobre costos o márgenes para calcular rentabilidad.
- **Causalidad:** el análisis permite describir patrones y diferencias, pero no demostrar que los descuentos, los canales u otras variables hayan causado cambios en las ventas.
- **Representatividad:** las conclusiones describen el conjunto de datos utilizado y no deben generalizarse a una empresa real sin evidencia adicional.

## Estructura del repositorio

```text
retail-store-sales-analytics/
├── data/
│   ├── raw/
│   │   └── retail_store_sales.csv
│   └── processed/
│       └── retail_store_sales_processed.csv
├── notebooks/
│   └── 01_extraccion_eda.ipynb
├── scripts/
│   ├── 02_limpieza_enriquecimiento.py
│   └── 03_cargar_postgres.py
├── SQL/
│   ├── 01_modelo_estrella.sql
│   └── 02_validaciones_integridad.sql
├── Power_BI/
│   └── retail_store_sales.pbix
├── requirements.txt
├── .gitignore
├── LICENSE
├── README.md
└── README_EN.md
```

Los nombres de archivos y carpetas deben coincidir con los que estén efectivamente publicados en el repositorio.

## Cómo reproducir el proyecto

1. Clonar el repositorio.
2. Crear un entorno virtual de Python e instalar las dependencias de `requirements.txt`.
3. Revisar y ejecutar el notebook de exploración.
4. Ejecutar el script de limpieza y enriquecimiento para generar el archivo procesado.
5. Configurar PostgreSQL y ejecutar los scripts SQL en el orden correspondiente.
6. Ejecutar el script de carga para poblar el modelo, de acuerdo con la configuración local.
7. Abrir `Power_BI/retail_store_sales.pbix` en Power BI Desktop y configurar la conexión a la base de datos local.
8. Ejecutar las validaciones y contrastar los indicadores principales antes de interpretar los resultados.

Las credenciales y los parámetros de conexión deben configurarse localmente y no deben publicarse en el repositorio.

## Autor

**Marco Schroeder**  
Portfolio de análisis de datos y Business Intelligence.

Repositorio: [retail-store-sales-analytics](https://github.com/Marco-Schroeder-Data-Scientist/retail-store-sales-analytics)
