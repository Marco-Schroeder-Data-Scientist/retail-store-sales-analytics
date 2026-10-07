-- ============================================================
-- 01. VALIDACIÓN DE LA ESTRUCTURA DEL MODELO
-- ============================================================
-- Objetivo:
-- Confirmar que las cinco dimensiones y la tabla de hechos
-- fueron creadas correctamente dentro del esquema public.
--
-- Esta validación se realiza antes de cargar los datos para
-- detectar problemas estructurales en el modelo.

SELECT
    table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN (
      'dim_customer',
      'dim_product',
      'dim_date',
      'dim_payment_method',
      'dim_location',
      'fact_sales'
  )
ORDER BY table_name;


-- ============================================================
-- 02. VALIDACIÓN DE LAS COLUMNAS DEL MODELO
-- ============================================================
-- Objetivo:
-- Confirmar que las seis tablas contienen las columnas
-- definidas previamente en el modelo estrella.
--
-- Esta validación permite detectar errores en nombres,
-- columnas faltantes o columnas adicionales antes de
-- comenzar la carga de datos.

SELECT
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name IN (
      'dim_customer',
      'dim_product',
      'dim_date',
      'dim_payment_method',
      'dim_location',
      'fact_sales'
  )
ORDER BY
    table_name,
    ordinal_position;


-- ============================================================
-- 03. VALIDACIÓN DE LAS CLAVES PRIMARIAS
-- ============================================================
-- Objetivo:
-- Confirmar que cada tabla del modelo estrella tenga definida
-- la clave primaria esperada.
--
-- Las claves primarias garantizan la identificación única de
-- cada registro dentro de las dimensiones y de la tabla de hechos.

SELECT
    tc.table_name,
    kcu.column_name,
    tc.constraint_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
    AND tc.table_name = kcu.table_name
WHERE tc.table_schema = 'public'
  AND tc.constraint_type = 'PRIMARY KEY'
  AND tc.table_name IN (
      'dim_customer',
      'dim_product',
      'dim_date',
      'dim_payment_method',
      'dim_location',
      'fact_sales'
  )
ORDER BY
    tc.table_name;


-- ============================================================
-- 04. VALIDACIÓN DE LAS CLAVES FORÁNEAS
-- ============================================================
-- Objetivo:
-- Confirmar que la tabla de hechos tenga definidas las cinco
-- relaciones con las dimensiones del modelo estrella.
--
-- Estas relaciones garantizan que las claves utilizadas en
-- fact_sales correspondan a registros existentes en las
-- dimensiones relacionadas.

SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS referenced_table,
    ccu.column_name AS referenced_column,
    tc.constraint_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
    AND tc.table_name = kcu.table_name
JOIN information_schema.constraint_column_usage AS ccu
    ON tc.constraint_name = ccu.constraint_name
    AND tc.table_schema = ccu.table_schema
WHERE tc.table_schema = 'public'
  AND tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_name = 'fact_sales'
ORDER BY
    kcu.column_name;


-- ============================================================
-- 05. VALIDACIÓN DE LAS RESTRICCIONES UNIQUE
-- ============================================================
-- Objetivo:
-- Confirmar que los atributos que identifican de forma única
-- los registros de cada dimensión tengan definida la
-- restricción UNIQUE correspondiente.
--
-- Esto evita duplicados dentro de las dimensiones y mantiene
-- la integridad de los identificadores naturales.

SELECT
    tc.table_name,
    kcu.column_name,
    tc.constraint_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
    AND tc.table_name = kcu.table_name
WHERE tc.table_schema = 'public'
  AND tc.constraint_type = 'UNIQUE'
  AND tc.table_name IN (
      'dim_customer',
      'dim_product',
      'dim_date',
      'dim_payment_method',
      'dim_location'
  )
ORDER BY
    tc.table_name;


-- ============================================================
-- 06. VALIDACIÓN DEL ESTADO INICIAL DE LAS TABLAS
-- ============================================================
-- Objetivo:
-- Confirmar que las dimensiones y la tabla de hechos se
-- encuentran vacías antes de comenzar la carga de datos.
--
-- Partir de tablas vacías permite realizar la carga inicial
-- sin duplicar registros existentes.

SELECT
    'dim_customer' AS table_name,
    COUNT(*) AS row_count
FROM dim_customer

UNION ALL

SELECT
    'dim_product',
    COUNT(*)
FROM dim_product

UNION ALL

SELECT
    'dim_date',
    COUNT(*)
FROM dim_date

UNION ALL

SELECT
    'dim_payment_method',
    COUNT(*)
FROM dim_payment_method

UNION ALL

SELECT
    'dim_location',
    COUNT(*)
FROM dim_location

UNION ALL

SELECT
    'fact_sales',
    COUNT(*)
FROM fact_sales

ORDER BY
    table_name;


-- ============================================================
-- 07. VALIDACIÓN DE LA DIMENSIÓN DE CLIENTES
-- ============================================================
-- Objetivo:
-- Confirmar que los clientes fueron cargados correctamente
-- en dim_customer y que PostgreSQL generó las claves
-- sustitutas correspondientes.
--
-- También comprobamos que cada customer_id aparezca una
-- sola vez dentro de la dimensión.

SELECT
    customer_key,
    customer_id
FROM dim_customer
ORDER BY customer_key;


-- ============================================================
-- 08. VALIDACIÓN DE CANTIDAD DE REGISTROS
-- ============================================================
-- Objetivo:
-- Confirmar que las tablas del modelo estrella contienen
-- la cantidad de registros esperada después de la carga.

SELECT 'dim_customer' AS tabla, COUNT(*) AS registros
FROM dim_customer

UNION ALL

SELECT 'dim_product', COUNT(*)
FROM dim_product

UNION ALL

SELECT 'dim_date', COUNT(*)
FROM dim_date

UNION ALL

SELECT 'dim_payment_method', COUNT(*)
FROM dim_payment_method

UNION ALL

SELECT 'dim_location', COUNT(*)
FROM dim_location

UNION ALL

SELECT 'fact_sales', COUNT(*)
FROM fact_sales;


-- ============================================================
-- 09. VALIDACIÓN DE INTEGRIDAD REFERENCIAL
-- ============================================================
-- Objetivo:
-- Comprobar que todas las claves foráneas de fact_sales
-- tienen correspondencia en sus respectivas dimensiones.
--
-- Un resultado de 0 en cada columna indica que no existen
-- registros huérfanos.

SELECT
    COUNT(*) FILTER (
        WHERE c.customer_key IS NULL
    ) AS clientes_huerfanos,

    COUNT(*) FILTER (
        WHERE p.product_key IS NULL
    ) AS productos_huerfanos,

    COUNT(*) FILTER (
        WHERE d.date_key IS NULL
    ) AS fechas_huerfanas,

    COUNT(*) FILTER (
        WHERE pm.payment_method_key IS NULL
    ) AS metodos_pago_huerfanos,

    COUNT(*) FILTER (
        WHERE l.location_key IS NULL
    ) AS ubicaciones_huerfanas

FROM fact_sales f

LEFT JOIN dim_customer c
    ON f.customer_key = c.customer_key

LEFT JOIN dim_product p
    ON f.product_key = p.product_key

LEFT JOIN dim_date d
    ON f.date_key = d.date_key

LEFT JOIN dim_payment_method pm
    ON f.payment_method_key = pm.payment_method_key

LEFT JOIN dim_location l
    ON f.location_key = l.location_key;


-- ============================================================
-- 10. VALIDACIÓN DE DUPLICADOS EN FACT_SALES
-- ============================================================
-- Objetivo:
-- Confirmar que cada transaction_id aparece una sola vez
-- en la tabla de hechos.
--
-- El modelo define transaction_id como la clave primaria,
-- por lo que no deberían existir duplicados.

SELECT
    COUNT(*) AS total_filas,
    COUNT(DISTINCT transaction_id) AS transacciones_unicas,
    COUNT(*) - COUNT(DISTINCT transaction_id) AS duplicados
FROM fact_sales;


-- ============================================================
-- 11. VALIDACIÓN DE CONSISTENCIA DE LAS MEDIDAS
-- ============================================================
-- Objetivo:
-- Confirmar que total_spent mantiene la relación matemática
-- esperada con price_per_unit y quantity.
--
-- Se permiten diferencias únicamente por precisión numérica.
-- El modelo utiliza NUMERIC, por lo que esperamos que todas
-- las diferencias sean exactamente 0.

SELECT
    COUNT(*) AS total_transacciones,
    COUNT(*) FILTER (
        WHERE total_spent <> price_per_unit * quantity
    ) AS inconsistencias,
    MAX(
        ABS(total_spent - price_per_unit * quantity)
    ) AS diferencia_maxima
FROM fact_sales;


-- ============================================================
-- 12. VALIDACIÓN DE VALORES CATEGÓRICOS
-- ============================================================
-- Objetivo:
-- Confirmar que los atributos categóricos utilizados por el
-- modelo contienen únicamente los valores esperados después
-- del proceso de limpieza y transformación.

SELECT
    'payment_method' AS atributo,
    payment_method AS valor,
    COUNT(*) AS registros
FROM dim_payment_method
GROUP BY payment_method

UNION ALL

SELECT
    'location' AS atributo,
    location AS valor,
    COUNT(*) AS registros
FROM dim_location
GROUP BY location

UNION ALL

SELECT
    'discount_applied' AS atributo,
    discount_applied AS valor,
    COUNT(*) AS registros
FROM fact_sales
GROUP BY discount_applied

ORDER BY atributo, valor;


-- ============================================================
-- 13. VALIDACIÓN DEL PRODUCTO UNKNOWN
-- ============================================================
-- Objetivo:
-- Confirmar que existe un único miembro Unknown en dim_product
-- y conocer la categoría que quedó asociada a dicho miembro.
--
-- El valor Unknown representa productos cuyo nombre original
-- no estaba disponible en el dataset.

SELECT
    product_key,
    item,
    category
FROM dim_product
WHERE item = 'Unknown';


-- ============================================================
-- 14. VALIDACIÓN DE PRODUCTOS Y CATEGORÍAS
-- ============================================================
-- Objetivo:
-- Confirmar que dim_product contiene 200 productos
-- identificables y un único miembro Unknown.
--
-- También se verifica que cada producto identificable esté
-- asociado a una sola categoría.

SELECT
    COUNT(*) FILTER (
        WHERE item <> 'Unknown'
    ) AS productos_identificables,

    COUNT(*) FILTER (
        WHERE item = 'Unknown'
    ) AS productos_unknown,

    COUNT(DISTINCT item) FILTER (
        WHERE item <> 'Unknown'
    ) AS productos_distintos
FROM dim_product;


SELECT
    item,
    COUNT(DISTINCT category) AS categorias_asociadas
FROM dim_product
WHERE item <> 'Unknown'
GROUP BY item
HAVING COUNT(DISTINCT category) > 1;


-- ============================================================
-- 15. VALIDACIÓN FINAL DE FACT_SALES
-- ============================================================
-- Objetivo:
-- Confirmar que la ejecución repetida del script no generó
-- duplicados y que la tabla conserva las 12.575 transacciones.

SELECT
    COUNT(*) AS total_filas,
    COUNT(DISTINCT transaction_id) AS transacciones_unicas,
    COUNT(*) - COUNT(DISTINCT transaction_id) AS duplicados
FROM fact_sales;