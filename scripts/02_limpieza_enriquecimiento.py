# ============================================================
# 02 - LIMPIEZA Y ENRIQUECIMIENTO
# ============================================================

# Objetivo:
# Cargar el dataset RAW utilizando una ruta construida a partir
# de la ubicación del script para evitar problemas con el
# directorio desde el que se ejecuta Python.

import pandas as pd
from pathlib import Path


# ------------------------------------------------------------
# 1. CARGA DEL DATASET RAW
# ------------------------------------------------------------

# Obtener la carpeta donde se encuentra este script.
script_dir = Path(__file__).resolve().parent

# Subir un nivel desde "scripts" hasta la raíz del proyecto.
project_dir = script_dir.parent

# Construir la ruta al archivo RAW.
raw_path = project_dir / "data" / "raw" / "retail_store_sales.csv"

# Cargar el dataset RAW sin modificar sus valores.
df = pd.read_csv(raw_path)

# Mostrar la ruta utilizada para facilitar la trazabilidad.
print(f"Archivo cargado: {raw_path}")

# Mostrar las dimensiones para comprobar que el archivo
# conserva la estructura esperada.
print(f"Registros: {df.shape[0]}")
print(f"Columnas: {df.shape[1]}")

# ------------------------------------------------------------
# 2. RECONSTRUCCIÓN DE PRICE PER UNIT
# ------------------------------------------------------------

# Objetivo:
# Identificar los registros donde Price Per Unit está vacío,
# pero Quantity y Total Spent están disponibles.
# Estos registros pueden reconstruirse utilizando la relación:
# Price Per Unit = Total Spent / Quantity.

price_missing_before = df['Price Per Unit'].isna().sum()

reconstructable_price = (
    df['Price Per Unit'].isna()
    & df['Quantity'].notna()
    & df['Total Spent'].notna()
)

reconstructable_count = reconstructable_price.sum()

print(f"Valores faltantes de Price Per Unit: {price_missing_before}")
print(f"Valores reconstruibles: {reconstructable_count}")

# ------------------------------------------------------------
# 3. RECONSTRUCCIÓN DE PRICE PER UNIT
# ------------------------------------------------------------

# Objetivo:
# Completar Price Per Unit únicamente en los registros donde
# puede calcularse de forma exacta a partir de Total Spent
# y Quantity.
#
# Fórmula:
# Price Per Unit = Total Spent / Quantity

# Reconstruir el precio unitario únicamente en los registros
# identificados previamente como reconstruibles.
df.loc[reconstructable_price, 'Price Per Unit'] = (
    df.loc[reconstructable_price, 'Total Spent']
    / df.loc[reconstructable_price, 'Quantity']
)

# Contar nuevamente los valores faltantes para validar
# que los 609 registros fueron completados.
price_missing_after = df['Price Per Unit'].isna().sum()

# Mostrar el resultado de la transformación.
print(f"Valores faltantes de Price Per Unit después de reconstruir: {price_missing_after}")

# ------------------------------------------------------------
# 4. IDENTIFICACIÓN DE QUANTITY Y TOTAL SPENT RECONSTRUIBLES
# ------------------------------------------------------------

# Objetivo:
# Identificar los registros donde Quantity y Total Spent están
# vacíos, pero Price Per Unit está disponible.
#
# En estos casos no podemos recuperar los valores originales
# de Quantity y Total Spent de forma exacta. Por eso primero
# identificamos el grupo antes de aplicar la regla de imputación.

# Identificar los registros con Price Per Unit disponible,
# pero Quantity y Total Spent faltantes.
reconstructable_quantity = (
    df['Price Per Unit'].notna()
    & df['Quantity'].isna()
    & df['Total Spent'].isna()
)

# Contar los registros que cumplen esta condición.
reconstructable_quantity_count = reconstructable_quantity.sum()

# Mostrar el resultado para validar que coincide con el
# diagnóstico realizado durante el EDA.
print(
    f"Registros con Quantity y Total Spent faltantes: "
    f"{reconstructable_quantity_count}"
)

# ------------------------------------------------------------
# 5. CÁLCULO DE LA MEDIANA DE QUANTITY
# ------------------------------------------------------------

# Objetivo:
# Obtener la mediana de Quantity utilizando únicamente los
# valores disponibles.
#
# La mediana fue seleccionada durante el EDA porque Quantity
# es una variable discreta entre 1 y 10, no presenta outliers
# relevantes y su valor central observado es 6.

# Calcular la mediana ignorando los valores faltantes.
quantity_median = df['Quantity'].median()

# Mostrar la estadística que será utilizada para la imputación.
print(f"Mediana de Quantity: {quantity_median}")

# ------------------------------------------------------------
# 6. IMPUTACIÓN DE QUANTITY Y RECONSTRUCCIÓN DE TOTAL SPENT
# ------------------------------------------------------------

# Objetivo:
# Completar Quantity en los 604 registros identificados
# utilizando la mediana calculada durante el EDA.
#
# Una vez completada Quantity, Total Spent puede calcularse
# mediante la relación:
#
# Total Spent = Price Per Unit * Quantity

# Imputar Quantity únicamente en los registros identificados.
df.loc[reconstructable_quantity, 'Quantity'] = quantity_median

# Calcular Total Spent únicamente para esos mismos registros.
df.loc[reconstructable_quantity, 'Total Spent'] = (
    df.loc[reconstructable_quantity, 'Price Per Unit']
    * df.loc[reconstructable_quantity, 'Quantity']
)

# Contar los valores faltantes restantes para validar
# el resultado de la transformación.
quantity_missing_after = df['Quantity'].isna().sum()
total_spent_missing_after = df['Total Spent'].isna().sum()

# Mostrar los resultados de la imputación y reconstrucción.
print(f"Valores faltantes de Quantity después de imputar: {quantity_missing_after}")
print(
    f"Valores faltantes de Total Spent después de reconstruir: "
    f"{total_spent_missing_after}"
)

# ------------------------------------------------------------
# 7. VALIDACIÓN DE LA RELACIÓN ENTRE VARIABLES NUMÉRICAS
# ------------------------------------------------------------

# Objetivo:
# Verificar que Total Spent mantiene la relación de negocio
# con Price Per Unit y Quantity después de las transformaciones.
#
# Fórmula esperada:
# Total Spent = Price Per Unit * Quantity

# Calcular la diferencia entre el valor registrado y el valor
# que debería resultar de Price Per Unit * Quantity.
numeric_difference = (
    df['Total Spent']
    - (df['Price Per Unit'] * df['Quantity'])
)

# Obtener estadísticas de la diferencia para comprobar
# si existen discrepancias después de la limpieza.
print("Validación de la diferencia entre Total Spent y Price Per Unit * Quantity:")
print(numeric_difference.describe())

# ------------------------------------------------------------
# 8. ANÁLISIS DE VALORES FALTANTES DE ITEM
# ------------------------------------------------------------

# Objetivo:
# Analizar los registros donde Item está vacío para determinar
# si existe información suficiente en otras columnas que permita
# identificar el producto de forma confiable.
#
# No se imputará Item hasta conocer el significado del faltante.

# Identificar los registros donde Item está faltante.
item_missing = df['Item'].isna()

# Contar los registros afectados.
item_missing_count = item_missing.sum()

# Analizar las categorías asociadas a los registros sin Item.
item_missing_categories = df.loc[
    item_missing,
    'Category'
].value_counts()

# Mostrar los resultados.
print(f"Valores faltantes de Item: {item_missing_count}")
print("Categorías asociadas a los registros sin Item:")
print(item_missing_categories)

# ------------------------------------------------------------
# 9. VALIDACIÓN DE VALORES VACÍOS EN ITEM
# ------------------------------------------------------------

# Objetivo:
# Comprobar si Item contiene cadenas vacías o valores compuestos
# únicamente por espacios, además de los valores nulos ya
# identificados.

# Identificar valores de texto vacíos o con solo espacios.
item_empty = (
    df['Item'].notna()
    & df['Item'].astype(str).str.strip().eq('')
)

# Contar los registros afectados.
item_empty_count = item_empty.sum()

# Mostrar el resultado.
print(f"Valores de Item vacíos o con espacios: {item_empty_count}")

# ------------------------------------------------------------
# 10. TRATAMIENTO DE VALORES FALTANTES DE ITEM
# ------------------------------------------------------------

# Objetivo:
# Representar explícitamente los productos cuyo nombre no está
# disponible en el dataset original.
#
# No se asigna un producto específico porque Category no permite
# determinar de forma confiable cuál era el Item original.

# Reemplazar únicamente los valores nulos de Item.
df['Item'] = df['Item'].fillna('Unknown')

# Contar los valores faltantes restantes.
item_missing_after = df['Item'].isna().sum()

# Contar cuántos registros fueron marcados como Unknown.
item_unknown_count = (df['Item'] == 'Unknown').sum()

# Mostrar los resultados de la transformación.
print(f"Valores faltantes de Item después de limpiar: {item_missing_after}")
print(f"Registros de Item marcados como Unknown: {item_unknown_count}")

# ------------------------------------------------------------
# 11. ANÁLISIS DE VALORES FALTANTES DE DISCOUNT APPLIED
# ------------------------------------------------------------

# Objetivo:
# Analizar los registros donde Discount Applied está faltante
# para determinar si existe algún patrón que permita interpretar
# correctamente estos valores.

# Identificar los registros donde Discount Applied está faltante.
discount_missing = df['Discount Applied'].isna()

# Contar los registros afectados.
discount_missing_count = discount_missing.sum()

# Analizar la distribución de Category en los registros
# donde Discount Applied está faltante.
discount_missing_categories = df.loc[
    discount_missing,
    'Category'
].value_counts()

# Analizar la distribución de Location en los mismos registros.
discount_missing_locations = df.loc[
    discount_missing,
    'Location'
].value_counts()

# Analizar la distribución de Payment Method.
discount_missing_payment = df.loc[
    discount_missing,
    'Payment Method'
].value_counts()

# Mostrar los resultados.
print(f"Valores faltantes de Discount Applied: {discount_missing_count}")

print("Categorías asociadas a los valores faltantes:")
print(discount_missing_categories)

print("Ubicaciones asociadas a los valores faltantes:")
print(discount_missing_locations)

print("Métodos de pago asociados a los valores faltantes:")
print(discount_missing_payment)

# ------------------------------------------------------------
# 12. TRATAMIENTO DE VALORES FALTANTES DE DISCOUNT APPLIED
# ------------------------------------------------------------

# Objetivo:
# Representar explícitamente los registros donde no existe
# información sobre la aplicación de descuentos.
#
# No se convierten los valores faltantes en False porque no
# existe evidencia suficiente para afirmar que esos registros
# no tuvieron descuento.

# Reemplazar únicamente los valores nulos por Unknown.
df['Discount Applied'] = df['Discount Applied'].fillna('Unknown')

# Contar los valores faltantes restantes.
discount_missing_after = df['Discount Applied'].isna().sum()

# Contar los registros marcados como Unknown.
discount_unknown_count = (
    df['Discount Applied'] == 'Unknown'
).sum()

# Mostrar los resultados de la transformación.
print(
    f"Valores faltantes de Discount Applied después de limpiar: "
    f"{discount_missing_after}"
)

print(
    f"Registros de Discount Applied marcados como Unknown: "
    f"{discount_unknown_count}"
)

# ------------------------------------------------------------
# 13. NORMALIZACIÓN DE NOMBRES DE COLUMNAS
# ------------------------------------------------------------

# Objetivo:
# Estandarizar los nombres de las columnas para facilitar su
# uso posterior en Pandas, PostgreSQL, SQL y Power BI.
#
# Regla aplicada:
# - minúsculas
# - espacios reemplazados por "_"

# Crear un diccionario con los nombres actuales y sus versiones
# normalizadas.
column_rename = {
    column: column.strip().lower().replace(' ', '_')
    for column in df.columns
}

# Aplicar los nuevos nombres de columnas.
df = df.rename(columns=column_rename)

# Mostrar los nombres resultantes para validar la transformación.
print("Columnas después de normalizar:")
print(df.columns.tolist())

# ------------------------------------------------------------
# 14. CONVERSIÓN DE TRANSACTION_DATE
# ------------------------------------------------------------

# Objetivo:
# Convertir Transaction Date desde texto a datetime para
# permitir posteriormente análisis temporales como año,
# mes, día y tendencias de ventas.

# Convertir la columna a tipo datetime.
df['transaction_date'] = pd.to_datetime(
    df['transaction_date'],
    errors='coerce'
)

# Contar los valores que no pudieron convertirse.
invalid_dates = df['transaction_date'].isna().sum()

# Mostrar el tipo resultante y la cantidad de fechas inválidas.
print(f"Tipo de transaction_date: {df['transaction_date'].dtype}")
print(f"Fechas inválidas después de convertir: {invalid_dates}")


# ------------------------------------------------------------
# 15. CONVERSIÓN DE TIPOS DE DATOS
# ------------------------------------------------------------

# Objetivo:
# Optimizar y estandarizar los tipos de datos del dataset
# procesado, considerando la naturaleza de cada variable.

# Convertir las variables categóricas a category.
categorical_columns = [
    'customer_id',
    'category',
    'item',
    'payment_method',
    'location',
    'discount_applied'
]

for column in categorical_columns:
    df[column] = df[column].astype('category')

# Convertir las variables numéricas a float32 para reducir
# el uso de memoria manteniendo precisión suficiente para
# este dataset.
numeric_columns = [
    'price_per_unit',
    'quantity',
    'total_spent'
]

for column in numeric_columns:
    df[column] = df[column].astype('float32')

# Mostrar los tipos finales para validar las conversiones.
print("Tipos de datos después de la conversión:")
print(df.dtypes)


# ------------------------------------------------------------
# 16. VALIDACIÓN INTEGRAL DEL DATASET PROCESADO
# ------------------------------------------------------------
# Objetivo:
# Realizar una revisión final del DataFrame después de todas
# las transformaciones de limpieza aplicadas hasta este punto.

# Mostrar dimensiones finales.
print(f"Dimensiones finales: {df.shape[0]} filas x {df.shape[1]} columnas")

# Mostrar cantidad de valores faltantes por columna.
print("\nValores faltantes por columna:")
print(df.isna().sum())

# Mostrar cantidad de registros duplicados.
print(f"\nRegistros duplicados: {df.duplicated().sum()}")

# Mostrar los tipos de datos finales.
print("\nTipos de datos finales:")
print(df.dtypes)


# ------------------------------------------------------------
# 17. VALIDACIÓN DE IDENTIFICADORES DE TRANSACCIÓN
# ------------------------------------------------------------

# Objetivo:
# Verificar que Transaction ID mantiene su unicidad después
# de todas las transformaciones realizadas.

# Contar la cantidad total de identificadores.
transaction_id_count = df['transaction_id'].count()

# Contar la cantidad de identificadores únicos.
transaction_id_unique = df['transaction_id'].nunique()

# Mostrar ambos valores para comprobar que coinciden.
print(f"Total de transaction_id: {transaction_id_count}")
print(f"transaction_id únicos: {transaction_id_unique}")

# Validar explícitamente la unicidad.
transaction_id_unique_check = (
    transaction_id_count == transaction_id_unique
)

print(
    f"¿Todos los transaction_id son únicos?: "
    f"{transaction_id_unique_check}"
)


# ------------------------------------------------------------
# 18. GUARDAR DATASET PROCESADO
# ------------------------------------------------------------

# Objetivo:
# Guardar el DataFrame limpio y transformado en la carpeta
# processed, manteniendo el archivo RAW original sin modificar.

# Construir la ruta de salida utilizando la raíz del proyecto.
processed_dir = project_dir / "data" / "processed"

# Crear la carpeta processed si todavía no existe.
processed_dir.mkdir(parents=True, exist_ok=True)

# Definir el nombre del archivo procesado.
processed_path = processed_dir / "retail_store_sales_processed.csv"

# Guardar el DataFrame procesado.
df.to_csv(processed_path, index=False)

# Mostrar información sobre el archivo generado.
print(f"Dataset procesado guardado en: {processed_path}")
print(f"Registros guardados: {df.shape[0]}")
print(f"Columnas guardadas: {df.shape[1]}")


# ------------------------------------------------------------
# 19. VALIDACIÓN DEL ARCHIVO PROCESADO
# ------------------------------------------------------------

# Objetivo:
# Volver a leer el archivo procesado desde disco para comprobar
# que conserva la cantidad de registros y columnas esperadas
# después de la exportación.

# Leer nuevamente el archivo procesado.
df_processed = pd.read_csv(processed_path)

# Mostrar las dimensiones reales del archivo guardado.
print(
    f"Dimensiones del archivo procesado: "
    f"{df_processed.shape[0]} filas x {df_processed.shape[1]} columnas"
)

# Mostrar los valores faltantes presentes en el archivo.
print("\nValores faltantes en el archivo procesado:")
print(df_processed.isna().sum())

# Mostrar la cantidad de registros duplicados.
print(
    f"\nRegistros duplicados en el archivo procesado: "
    f"{df_processed.duplicated().sum()}"
)


# ------------------------------------------------------------
# 20. INSPECCIÓN FINAL DEL DATASET PROCESADO
# ------------------------------------------------------------

# Objetivo:
# Revisar las principales características del archivo procesado
# antes de diseñar el modelo de datos para PostgreSQL.

# Mostrar una muestra de los registros procesados.
print("\nPrimeros registros del dataset procesado:")
print(df_processed.head())

# Mostrar la cantidad de valores únicos por columna.
print("\nValores únicos por columna:")
print(df_processed.nunique())

# Mostrar las categorías existentes.
print("\nCategorías:")
print(df_processed['category'].unique())

# Mostrar los métodos de pago existentes.
print("\nMétodos de pago:")
print(df_processed['payment_method'].unique())

# Mostrar las ubicaciones existentes.
print("\nUbicaciones:")
print(df_processed['location'].unique())

# Mostrar los valores existentes de Discount Applied.
print("\nValores de Discount Applied:")
print(df_processed['discount_applied'].unique())


# ------------------------------------------------------------
# 21. INSPECCIÓN DE LOS PRODUCTOS
# ------------------------------------------------------------
# Objetivo:
# Analizar cómo están estructurados los valores de item y
# comprobar su relación con las categorías antes de diseñar
# la dimensión de productos.
#
# Esta revisión permite determinar si item puede utilizarse
# como identificador de producto y qué atributos deberían
# pertenecer a dim_product.

print("\nCantidad de items distintos:")
print(df_processed["item"].nunique())

print("\nPrimeros 30 items:")
print(df_processed["item"].drop_duplicates().head(30).to_list())

print("\nCantidad de items por categoría:")
print(
    df_processed.groupby("category", observed=True)["item"]
    .nunique()
    .sort_values(ascending=False)
)


# ------------------------------------------------------------
# 22. INSPECCIÓN DEL PERÍODO TEMPORAL
# ------------------------------------------------------------
# Objetivo:
# Identificar la fecha mínima y máxima de las transacciones
# para determinar el período que deberá cubrir la dimensión
# calendario del modelo estrella.

print("\nFecha mínima:")
print(df_processed["transaction_date"].min())

print("\nFecha máxima:")
print(df_processed["transaction_date"].max())

print("\nCantidad de fechas distintas:")
print(df_processed["transaction_date"].nunique())


# ------------------------------------------------------------
# 23. VALIDACIÓN DE LA RELACIÓN ITEM → CATEGORY
# ------------------------------------------------------------
# Objetivo:
# Confirmar que cada producto identificable pertenece a una
# única categoría antes de utilizar ambas columnas dentro de
# dim_product.
#
# Los valores Unknown se excluyen porque representan datos
# faltantes reemplazados durante la limpieza.

item_category_check = (
    df_processed[df_processed["item"] != "Unknown"]
    .groupby("item", observed=True)["category"]
    .nunique()
)

print("\nCantidad máxima de categorías por item:")
print(item_category_check.max())

print("\nItems asociados a más de una categoría:")
print(item_category_check[item_category_check > 1])