# ============================================================
# 01. IMPORTACIÓN DE LIBRERÍAS Y CONFIGURACIÓN DE RUTAS
# ============================================================
# Objetivo:
# Importar las librerías necesarias para leer el archivo CSV,
# gestionar las variables de entorno y trabajar con PostgreSQL.
#
# También se construyen rutas relativas al proyecto para evitar
# depender de una ubicación específica del equipo.

import os
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import load_dotenv


# Identificar la carpeta raíz del proyecto a partir de la
# ubicación de este script.
script_dir = Path(__file__).resolve().parent
project_dir = script_dir.parent

# Definir la ruta del archivo procesado que será cargado.
processed_path = (
    project_dir
    / "data"
    / "processed"
    / "retail_store_sales_processed.csv"
)

# Cargar las variables de conexión almacenadas en .env.
load_dotenv(project_dir / ".env")


# ============================================================
# 02. CARGA DEL DATASET PROCESADO
# ============================================================
# Objetivo:
# Leer el dataset que fue limpiado y validado previamente
# utilizando Pandas.
#
# En esta etapa no se realizan nuevas transformaciones:
# trabajamos directamente con el archivo procesado que será
# utilizado como fuente para cargar PostgreSQL.

df = pd.read_csv(processed_path)

df["transaction_date"] = pd.to_datetime(
    df["transaction_date"],
    errors="coerce"
)

print("\nTipo de dato de transaction_date:")
print(df["transaction_date"].dtype)

print(f"Fechas inválidas encontradas: {df['transaction_date'].isna().sum()}")


# Mostrar información básica para confirmar que el archivo
# correcto fue cargado antes de continuar con PostgreSQL.
print("Dataset cargado correctamente.")
print(f"Filas: {df.shape[0]}")
print(f"Columnas: {df.shape[1]}")
print(f"Ruta utilizada: {processed_path}")


# ============================================================
# 03. VALIDACIÓN DE LAS VARIABLES DE CONEXIÓN
# ============================================================
# Objetivo:
# Confirmar que las variables necesarias para conectarnos a
# PostgreSQL fueron cargadas correctamente desde el archivo
# .env.
#
# La contraseña no se muestra por seguridad.

db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

print("\nConfiguración de PostgreSQL:")
print(f"DB_HOST: {db_host}")
print(f"DB_PORT: {db_port}")
print(f"DB_NAME: {db_name}")
print(f"DB_USER: {db_user}")
print(f"DB_PASSWORD configurada: {bool(db_password)}")


# ============================================================
# 04. PRUEBA DE CONEXIÓN A POSTGRESQL
# ============================================================
# Objetivo:
# Establecer una conexión con la base de datos PostgreSQL
# utilizando las credenciales almacenadas en .env.
#
# En esta etapa solamente comprobamos que la conexión funciona.
# Todavía no se insertan ni modifican datos.

connection = psycopg2.connect(
    host=db_host,
    port=db_port,
    dbname=db_name,
    user=db_user,
    password=db_password
)

print("\nConexión a PostgreSQL establecida correctamente.")

# Cerrar la conexión después de comprobarla para no mantener
# recursos abiertos innecesariamente.
connection.close()

print("Conexión cerrada correctamente.")


# ============================================================
# 05. PREPARACIÓN DE LA DIMENSIÓN DE CLIENTES
# ============================================================
# Objetivo:
# Obtener los identificadores de clientes únicos presentes
# en el dataset procesado para utilizarlos como registros
# de la dimensión dim_customer.
#
# customer_key no se genera en Pandas: será generado por
# PostgreSQL mediante la columna IDENTITY definida en la tabla.

customers = (
    df[["customer_id"]]
    .drop_duplicates()
    .sort_values("customer_id")
    .reset_index(drop=True)
)

print("\nClientes únicos preparados:")
print(f"Cantidad de clientes: {len(customers)}")
print(customers.head())


# ============================================================
# 06. CARGA DE LA DIMENSIÓN DE CLIENTES
# ============================================================
# Objetivo:
# Insertar los clientes únicos preparados anteriormente en
# dim_customer.
#
# PostgreSQL generará automáticamente customer_key mediante
# la columna IDENTITY definida en la tabla.

connection = psycopg2.connect(
    host=db_host,
    port=db_port,
    dbname=db_name,
    user=db_user,
    password=db_password
)

cursor = connection.cursor()

insert_customer_query = """
    INSERT INTO dim_customer (customer_id)
    VALUES (%s)
    ON CONFLICT (customer_id) DO NOTHING
"""

customer_records = [
    (customer_id,)
    for customer_id in customers["customer_id"]
]

cursor.executemany(insert_customer_query, customer_records)

connection.commit()

print("\nDimensión dim_customer cargada correctamente.")
print(f"Registros insertados: {cursor.rowcount}")

cursor.close()
connection.close()

# ============================================================
# 07. PREPARACIÓN DE LA DIMENSIÓN DE PRODUCTOS
# ============================================================
# Objetivo:
# Obtener los productos únicos junto con su categoría para
# construir la dimensión dim_product.
#
# El valor "Unknown" se conserva porque representa las
# transacciones cuyo producto original no estaba informado.
# No debe eliminarse, ya que esas transacciones también deben
# poder relacionarse con dim_product.

products = (
    df[["item", "category"]]
    .drop_duplicates()
    .sort_values(["item", "category"])
    .reset_index(drop=True)
)

print("\nProductos únicos preparados:")
print(f"Cantidad de combinaciones producto-categoría: {len(products)}")
print(f"Productos identificados: {(products['item'] != 'Unknown').sum()}")
print(f"Registros Unknown: {(products['item'] == 'Unknown').sum()}")

print("\nPrimeros registros:")
print(products.head())


# ============================================================
# 08. CARGA DE LA DIMENSIÓN DE PRODUCTOS
# ============================================================
# Objetivo:
# Insertar los productos y sus categorías en dim_product.
#
# Se utiliza ON CONFLICT DO NOTHING para que el script pueda
# ejecutarse nuevamente sin intentar duplicar productos que
# ya hayan sido cargados previamente.
#
# PostgreSQL generará automáticamente product_key mediante
# la columna IDENTITY definida en la tabla.

connection = psycopg2.connect(
    host=db_host,
    port=db_port,
    dbname=db_name,
    user=db_user,
    password=db_password
)

cursor = connection.cursor()

insert_product_query = """
    INSERT INTO dim_product (item, category)
    VALUES (%s, %s)
    ON CONFLICT (item) DO NOTHING
"""

product_records = [
    (row["item"], row["category"])
    for _, row in products.iterrows()
]

cursor.executemany(insert_product_query, product_records)

connection.commit()

print("\nDimensión dim_product cargada correctamente.")
print(f"Registros insertados: {cursor.rowcount}")

cursor.close()
connection.close()

# ============================================================
# 09. PREPARACIÓN DE LA DIMENSIÓN DE FECHAS
# ============================================================
# Objetivo:
# Construir una fila por cada fecha única presente en el
# dataset procesado y derivar los atributos necesarios para
# el análisis temporal.
#
# day_of_week utiliza la convención de PostgreSQL:
# 0 = domingo, 1 = lunes, ..., 6 = sábado.
#
# date_key se construye como YYYYMMDD para utilizarlo como
# clave primaria de la dimensión de fechas.

dates = (
    df[["transaction_date"]]
    .drop_duplicates()
    .sort_values("transaction_date")
    .reset_index(drop=True)
)

dates["date_key"] = dates["transaction_date"].dt.strftime("%Y%m%d").astype(int)
dates["full_date"] = dates["transaction_date"].dt.date
dates["year"] = dates["transaction_date"].dt.year
dates["quarter"] = dates["transaction_date"].dt.quarter
dates["month"] = dates["transaction_date"].dt.month
dates["month_name"] = dates["transaction_date"].dt.strftime("%B")
dates["day"] = dates["transaction_date"].dt.day

# PostgreSQL EXTRACT(DOW) utiliza 0 = domingo y 6 = sábado.
# Python weekday() utiliza 0 = lunes, por lo que se ajusta
# la numeración para hacerla compatible con PostgreSQL.
dates["day_of_week"] = (dates["transaction_date"].dt.weekday + 1) % 7

dates = dates[
    [
        "date_key",
        "full_date",
        "year",
        "quarter",
        "month",
        "month_name",
        "day",
        "day_of_week",
    ]
]

print("\nFechas únicas preparadas:")
print(f"Cantidad de fechas: {len(dates)}")
print(f"Fecha inicial: {dates['full_date'].min()}")
print(f"Fecha final: {dates['full_date'].max()}")

print("\nPrimeros registros:")
print(dates.head())

print("\nÚltimos registros:")
print(dates.tail())


# ============================================================
# 10. CARGA DE LA DIMENSIÓN DE FECHAS
# ============================================================
# Objetivo:
# Insertar las fechas preparadas en dim_date junto con sus
# atributos temporales.
#
# ON CONFLICT DO NOTHING permite ejecutar nuevamente el script
# sin duplicar fechas que ya existan en PostgreSQL.

connection = psycopg2.connect(
    host=db_host,
    port=db_port,
    dbname=db_name,
    user=db_user,
    password=db_password
)

cursor = connection.cursor()

insert_date_query = """
    INSERT INTO dim_date (
        date_key,
        full_date,
        year,
        quarter,
        month,
        month_name,
        day,
        day_of_week
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (date_key) DO NOTHING
"""

date_records = [
    (
        row["date_key"],
        row["full_date"],
        row["year"],
        row["quarter"],
        row["month"],
        row["month_name"],
        row["day"],
        row["day_of_week"]
    )
    for _, row in dates.iterrows()
]

cursor.executemany(insert_date_query, date_records)

connection.commit()

print("\nDimensión dim_date cargada correctamente.")
print(f"Registros insertados: {cursor.rowcount}")

cursor.close()
connection.close()


# ============================================================
# 11. PREPARACIÓN DE LA DIMENSIÓN DE MÉTODOS DE PAGO
# ============================================================
# Objetivo:
# Obtener los métodos de pago únicos presentes en el dataset
# procesado para construir la dimensión dim_payment_method.
#
# Los valores ya fueron limpiados previamente, por lo que en
# esta etapa solamente identificamos y ordenamos los valores
# que serán cargados en PostgreSQL.

payment_methods = (
    df[["payment_method"]]
    .drop_duplicates()
    .sort_values("payment_method")
    .reset_index(drop=True)
)

print("\nMétodos de pago preparados:")
print(f"Cantidad de métodos de pago: {len(payment_methods)}")

print("\nValores encontrados:")
print(payment_methods)


# ============================================================
# 12. CARGA DE LA DIMENSIÓN DE MÉTODOS DE PAGO
# ============================================================
# Objetivo:
# Insertar los métodos de pago únicos en
# dim_payment_method.
#
# ON CONFLICT DO NOTHING permite ejecutar nuevamente el script
# sin generar duplicados si los registros ya existen.

connection = psycopg2.connect(
    host=db_host,
    port=db_port,
    dbname=db_name,
    user=db_user,
    password=db_password
)

cursor = connection.cursor()

insert_payment_method_query = """
    INSERT INTO dim_payment_method (payment_method)
    VALUES (%s)
    ON CONFLICT (payment_method) DO NOTHING
"""

payment_method_records = [
    (payment_method,)
    for payment_method in payment_methods["payment_method"]
]

cursor.executemany(
    insert_payment_method_query,
    payment_method_records
)

connection.commit()

print("\nDimensión dim_payment_method cargada correctamente.")
print(f"Registros insertados: {cursor.rowcount}")

cursor.close()
connection.close()


# ============================================================
# 13. PREPARACIÓN DE LA DIMENSIÓN DE UBICACIONES
# ============================================================
# Objetivo:
# Obtener las ubicaciones únicas presentes en el dataset
# procesado para construir la dimensión dim_location.
#
# En esta etapa solamente identificamos y ordenamos los
# valores que posteriormente serán cargados en PostgreSQL.

locations = (
    df[["location"]]
    .drop_duplicates()
    .sort_values("location")
    .reset_index(drop=True)
)

print("\nUbicaciones preparadas:")
print(f"Cantidad de ubicaciones: {len(locations)}")

print("\nValores encontrados:")
print(locations)


# ============================================================
# 14. CARGA DE LA DIMENSIÓN DE UBICACIONES
# ============================================================
# Objetivo:
# Insertar las ubicaciones únicas en dim_location.
#
# ON CONFLICT DO NOTHING permite ejecutar nuevamente el script
# sin generar duplicados si las ubicaciones ya existen.

connection = psycopg2.connect(
    host=db_host,
    port=db_port,
    dbname=db_name,
    user=db_user,
    password=db_password
)

cursor = connection.cursor()

insert_location_query = """
    INSERT INTO dim_location (location)
    VALUES (%s)
    ON CONFLICT (location) DO NOTHING
"""

location_records = [
    (location,)
    for location in locations["location"]
]

cursor.executemany(
    insert_location_query,
    location_records
)

connection.commit()

print("\nDimensión dim_location cargada correctamente.")
print(f"Registros insertados: {cursor.rowcount}")

cursor.close()
connection.close()


# ============================================================
# 15. OBTENCIÓN DE CLAVES SUSTITUTAS DE LAS DIMENSIONES
# ============================================================
# Objetivo:
# Obtener desde PostgreSQL las claves sustitutas generadas
# para cada dimensión.
#
# Estas claves serán necesarias para relacionar cada
# transacción del dataset con:
# - dim_customer
# - dim_product
# - dim_date
# - dim_payment_method
# - dim_location
#
# En esta etapa solamente recuperamos las dimensiones.
# Todavía no se insertan registros en fact_sales.

connection = psycopg2.connect(
    host=db_host,
    port=db_port,
    dbname=db_name,
    user=db_user,
    password=db_password
)

customers_db = pd.read_sql(
    """
    SELECT customer_key, customer_id
    FROM dim_customer
    ORDER BY customer_key
    """,
    connection
)

products_db = pd.read_sql(
    """
    SELECT product_key, item, category
    FROM dim_product
    ORDER BY product_key
    """,
    connection
)

dates_db = pd.read_sql(
    """
    SELECT date_key, full_date
    FROM dim_date
    ORDER BY date_key
    """,
    connection
)

payment_methods_db = pd.read_sql(
    """
    SELECT payment_method_key, payment_method
    FROM dim_payment_method
    ORDER BY payment_method_key
    """,
    connection
)

locations_db = pd.read_sql(
    """
    SELECT location_key, location
    FROM dim_location
    ORDER BY location_key
    """,
    connection
)

connection.close()

print("\nClaves de dimensiones recuperadas correctamente.")

print(f"Clientes: {len(customers_db)}")
print(f"Productos: {len(products_db)}")
print(f"Fechas: {len(dates_db)}")
print(f"Métodos de pago: {len(payment_methods_db)}")
print(f"Ubicaciones: {len(locations_db)}")


# ============================================================
# 16. RELACIÓN ENTRE FACT_SALES Y DIM_CUSTOMER
# ============================================================
# Objetivo:
# Relacionar cada customer_id del dataset procesado con el
# customer_key generado por PostgreSQL en dim_customer.
#
# El resultado permitirá verificar que todas las transacciones
# tienen un cliente válido antes de construir fact_sales.
#
# Todavía no se insertan datos en PostgreSQL.

fact_test = df[["transaction_id", "customer_id"]].copy()

fact_test = fact_test.merge(
    customers_db,
    on="customer_id",
    how="left"
)

missing_customer_keys = fact_test["customer_key"].isna().sum()

print("\nValidación de relación customer_id → customer_key:")
print(f"Transacciones evaluadas: {len(fact_test)}")
print(f"Claves de cliente faltantes: {missing_customer_keys}")

print("\nEjemplo de registros relacionados:")
print(fact_test.head())


# ============================================================
# 17. RELACIÓN ENTRE FACT_SALES Y DIM_PRODUCT
# ============================================================
# Objetivo:
# Relacionar cada producto del dataset con el product_key
# generado por PostgreSQL en dim_product.
#
# Se utilizan item y category para identificar correctamente
# el registro correspondiente en la dimensión.
#
# Esto también permite comprobar que el registro "Unknown"
# puede relacionarse correctamente con dim_product.

fact_test_product = df[
    ["transaction_id", "item", "category"]
].copy()

fact_test_product = fact_test_product.merge(
    products_db,
    on=["item", "category"],
    how="left"
)

missing_product_keys = fact_test_product["product_key"].isna().sum()

print("\nValidación de relación item + category → product_key:")
print(f"Transacciones evaluadas: {len(fact_test_product)}")
print(f"Claves de producto faltantes: {missing_product_keys}")

print("\nEjemplo de registros relacionados:")
print(fact_test_product.head())

# ============================================================
# 17.1. INVESTIGACIÓN DE PRODUCTOS SIN CLAVE
# ============================================================
# Objetivo:
# Identificar los valores de item y category que no pudieron
# relacionarse con dim_product.
#
# No modificamos datos en esta etapa. Solamente investigamos
# la causa de las claves de producto faltantes.

unmatched_products = (
    fact_test_product[
        fact_test_product["product_key"].isna()
    ][["item", "category"]]
    .value_counts()
    .reset_index(name="transaction_count")
)

print("\nCombinaciones item + category sin product_key:")
print(f"Cantidad de combinaciones no relacionadas: {len(unmatched_products)}")

print("\nPrimeras combinaciones encontradas:")
print(unmatched_products.head(20))


# ============================================================
# 17.2. VALIDACIÓN DE PRODUCTO UTILIZANDO SOLO ITEM
# ============================================================
# Objetivo:
# Comprobar que item es suficiente para relacionar las
# transacciones con dim_product.
#
# Esto permite que todas las transacciones con item = Unknown
# utilicen el único registro Unknown de dim_product,
# independientemente de la categoría original.

fact_test_product_item = df[
    ["transaction_id", "item", "category"]
].copy()

fact_test_product_item = fact_test_product_item.merge(
    products_db[["product_key", "item"]],
    on="item",
    how="left"
)

missing_product_keys_item = (
    fact_test_product_item["product_key"].isna().sum()
)

print("\nValidación de relación item → product_key:")
print(f"Transacciones evaluadas: {len(fact_test_product_item)}")
print(f"Claves de producto faltantes: {missing_product_keys_item}")

print("\nEjemplos de registros relacionados:")
print(fact_test_product_item.head())

print("\nEjemplos de transacciones con item = Unknown:")
print(
    fact_test_product_item[
        fact_test_product_item["item"] == "Unknown"
    ].head()
)


# ============================================================
# 18. RELACIÓN ENTRE FACT_SALES Y DIM_DATE
# ============================================================
# Objetivo:
# Relacionar cada fecha de transacción con el date_key
# generado por PostgreSQL en dim_date.
#
# Se normalizan ambos campos como fecha para garantizar que
# la comparación utilice el mismo tipo de dato.
#
# Todavía no se insertan datos en fact_sales.

fact_test_date = df[
    ["transaction_id", "transaction_date"]
].copy()

fact_test_date["transaction_date"] = pd.to_datetime(
    fact_test_date["transaction_date"]
).dt.date

dates_db["full_date"] = pd.to_datetime(
    dates_db["full_date"]
).dt.date

fact_test_date = fact_test_date.merge(
    dates_db,
    left_on="transaction_date",
    right_on="full_date",
    how="left"
)

missing_date_keys = fact_test_date["date_key"].isna().sum()

print("\nValidación de relación transaction_date → date_key:")
print(f"Transacciones evaluadas: {len(fact_test_date)}")
print(f"Claves de fecha faltantes: {missing_date_keys}")

print("\nEjemplo de registros relacionados:")
print(fact_test_date.head())


# ============================================================
# 19. RELACIÓN ENTRE FACT_SALES Y DIM_PAYMENT_METHOD
# ============================================================
# Objetivo:
# Relacionar cada método de pago del dataset con el
# payment_method_key generado por PostgreSQL.
#
# Esta validación confirma que todas las transacciones podrán
# obtener una clave válida para la dimensión de métodos de pago.
#
# Todavía no se insertan datos en fact_sales.

fact_test_payment = df[
    ["transaction_id", "payment_method"]
].copy()

fact_test_payment = fact_test_payment.merge(
    payment_methods_db,
    on="payment_method",
    how="left"
)

missing_payment_keys = (
    fact_test_payment["payment_method_key"].isna().sum()
)

print("\nValidación de relación payment_method → payment_method_key:")
print(f"Transacciones evaluadas: {len(fact_test_payment)}")
print(f"Claves de método de pago faltantes: {missing_payment_keys}")

print("\nEjemplo de registros relacionados:")
print(fact_test_payment.head())


# ============================================================
# 20. RELACIÓN ENTRE FACT_SALES Y DIM_LOCATION
# ============================================================
# Objetivo:
# Relacionar cada ubicación del dataset con el location_key
# generado por PostgreSQL en dim_location.
#
# Esta es la última relación de dimensión que debemos validar
# antes de construir fact_sales.
#
# Todavía no se insertan datos en fact_sales.

fact_test_location = df[
    ["transaction_id", "location"]
].copy()

fact_test_location = fact_test_location.merge(
    locations_db,
    on="location",
    how="left"
)

missing_location_keys = (
    fact_test_location["location_key"].isna().sum()
)

print("\nValidación de relación location → location_key:")
print(f"Transacciones evaluadas: {len(fact_test_location)}")
print(f"Claves de ubicación faltantes: {missing_location_keys}")

print("\nEjemplo de registros relacionados:")
print(fact_test_location.head())

# ============================================================
# 21. CONSTRUCCIÓN DEL DATAFRAME FACT_SALES
# ============================================================
# Objetivo:
# Construir el dataframe que contiene el grano final de la
# tabla de hechos: una fila por cada transacción.
#
# Se incorporan las claves sustitutas de las cinco dimensiones:
# - customer_key
# - product_key
# - date_key
# - payment_method_key
# - location_key
#
# Todavía no se insertan registros en PostgreSQL.

fact_sales = df[
    [
        "transaction_id",
        "customer_id",
        "item",
        "transaction_date",
        "payment_method",
        "location",
        "price_per_unit",
        "quantity",
        "total_spent",
        "discount_applied"
    ]
].copy()

# Relacionar cada transacción con la dimensión de clientes.
fact_sales = fact_sales.merge(
    customers_db,
    on="customer_id",
    how="left"
)

# Relacionar cada transacción con la dimensión de productos.
# Se utiliza solamente item porque Unknown es un único miembro
# de la dimensión, independientemente de su categoría original.
fact_sales = fact_sales.merge(
    products_db[["product_key", "item"]],
    on="item",
    how="left"
)

# Normalizar la fecha antes de relacionarla con dim_date.
fact_sales["transaction_date"] = pd.to_datetime(
    fact_sales["transaction_date"]
).dt.date

fact_sales = fact_sales.merge(
    dates_db[["date_key", "full_date"]],
    left_on="transaction_date",
    right_on="full_date",
    how="left"
)

# Relacionar cada transacción con el método de pago.
fact_sales = fact_sales.merge(
    payment_methods_db,
    on="payment_method",
    how="left"
)

# Relacionar cada transacción con la ubicación.
fact_sales = fact_sales.merge(
    locations_db,
    on="location",
    how="left"
)

# Conservar únicamente las columnas que corresponden al
# diseño definitivo de fact_sales.
fact_sales = fact_sales[
    [
        "transaction_id",
        "customer_key",
        "product_key",
        "date_key",
        "payment_method_key",
        "location_key",
        "price_per_unit",
        "quantity",
        "total_spent",
        "discount_applied"
    ]
]

print("\nDataframe fact_sales construido correctamente.")
print(f"Filas: {fact_sales.shape[0]}")
print(f"Columnas: {fact_sales.shape[1]}")

print("\nPrimeros registros:")
print(fact_sales.head())


# ============================================================
# 22. VALIDACIÓN INTEGRAL DE FACT_SALES
# ============================================================
# Objetivo:
# Comprobar que fact_sales cumple las condiciones necesarias
# antes de insertar los registros en PostgreSQL.
#
# Se validará:
# - cantidad total de filas
# - unicidad de transaction_id
# - claves foráneas sin valores nulos
# - medidas numéricas sin valores nulos
# - coherencia matemática entre precio, cantidad y total

print("\nVALIDACIÓN INTEGRAL DE FACT_SALES")
print("=" * 60)

# Validar cantidad de transacciones.
print(f"Filas: {len(fact_sales)}")

# Validar unicidad de transaction_id.
transaction_duplicates = fact_sales["transaction_id"].duplicated().sum()
print(f"transaction_id duplicados: {transaction_duplicates}")

# Validar claves foráneas.
foreign_key_columns = [
    "customer_key",
    "product_key",
    "date_key",
    "payment_method_key",
    "location_key"
]

print("\nClaves foráneas nulas:")
for column in foreign_key_columns:
    print(f"{column}: {fact_sales[column].isna().sum()}")

# Validar medidas numéricas.
measure_columns = [
    "price_per_unit",
    "quantity",
    "total_spent"
]

print("\nMedidas numéricas nulas:")
for column in measure_columns:
    print(f"{column}: {fact_sales[column].isna().sum()}")

# Validar la relación matemática del importe total.
fact_sales_difference = (
    fact_sales["total_spent"]
    - (
        fact_sales["price_per_unit"]
        * fact_sales["quantity"]
    )
)

print("\nValidación matemática:")
print(f"Diferencias distintas de cero: {(fact_sales_difference != 0).sum()}")
print(f"Diferencia máxima absoluta: {fact_sales_difference.abs().max()}")

# Validación final del tamaño esperado.
print("\nResultado final:")
validation_passed = (
    len(fact_sales) == 12575
    and transaction_duplicates == 0
    and all(
        fact_sales[column].isna().sum() == 0
        for column in foreign_key_columns
    )
    and all(
        fact_sales[column].isna().sum() == 0
        for column in measure_columns
    )
    and (fact_sales_difference != 0).sum() == 0
)

print(f"Validación aprobada: {validation_passed}")


# ============================================================
# 23. CARGA DE LA TABLA DE HECHOS FACT_SALES
# ============================================================
# Objetivo:
# Insertar las 12.575 transacciones validadas en fact_sales.
#
# La tabla de hechos utiliza las claves sustitutas obtenidas
# desde las dimensiones y conserva las medidas originales:
# price_per_unit, quantity y total_spent.
#
# La transacción se confirma únicamente si toda la carga
# termina correctamente. Si ocurre un error, se revierte
# mediante rollback.

connection = psycopg2.connect(
    host=db_host,
    port=db_port,
    dbname=db_name,
    user=db_user,
    password=db_password
)

cursor = connection.cursor()

insert_fact_query = """
    INSERT INTO fact_sales (
        transaction_id,
        customer_key,
        product_key,
        date_key,
        payment_method_key,
        location_key,
        price_per_unit,
        quantity,
        total_spent,
        discount_applied
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

fact_records = [
    (
        row["transaction_id"],
        int(row["customer_key"]),
        int(row["product_key"]),
        int(row["date_key"]),
        int(row["payment_method_key"]),
        int(row["location_key"]),
        row["price_per_unit"],
        row["quantity"],
        row["total_spent"],
        row["discount_applied"]
    )
    for _, row in fact_sales.iterrows()
]

try:
    cursor.executemany(
        insert_fact_query,
        fact_records
    )

    connection.commit()

    print("\nTabla fact_sales cargada correctamente.")
    print(f"Registros insertados: {cursor.rowcount}")

except Exception as error:
    connection.rollback()

    print("\nError durante la carga de fact_sales.")
    print(f"Detalle: {error}")

finally:
    cursor.close()
    connection.close()

# ============================================================
# 24. CARGA DE LA TABLA DE HECHOS FACT_SALES
# ============================================================
# Objetivo:
# Insertar las transacciones validadas en fact_sales.
#
# ON CONFLICT DO NOTHING permite ejecutar nuevamente el script
# sin generar errores cuando una transacción ya existe.
#
# Esto hace que la carga sea repetible y evita duplicados.

connection = psycopg2.connect(
    host=db_host,
    port=db_port,
    dbname=db_name,
    user=db_user,
    password=db_password
)

cursor = connection.cursor()

insert_fact_query = """
    INSERT INTO fact_sales (
        transaction_id,
        customer_key,
        product_key,
        date_key,
        payment_method_key,
        location_key,
        price_per_unit,
        quantity,
        total_spent,
        discount_applied
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (transaction_id) DO NOTHING
"""

fact_records = [
    (
        row["transaction_id"],
        int(row["customer_key"]),
        int(row["product_key"]),
        int(row["date_key"]),
        int(row["payment_method_key"]),
        int(row["location_key"]),
        row["price_per_unit"],
        row["quantity"],
        row["total_spent"],
        row["discount_applied"]
    )
    for _, row in fact_sales.iterrows()
]

try:
    cursor.executemany(
        insert_fact_query,
        fact_records
    )

    connection.commit()

    print("\nCarga de fact_sales ejecutada correctamente.")
    print(f"Registros procesados: {len(fact_records)}")
    print(f"Registros afectados por la operación: {cursor.rowcount}")

except Exception as error:
    connection.rollback()

    print("\nError durante la carga de fact_sales.")
    print(f"Detalle: {error}")

finally:
    cursor.close()
    connection.close()