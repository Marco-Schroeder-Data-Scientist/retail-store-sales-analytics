-- ============================================================
-- 01. CREACIÓN DE LA DIMENSIÓN DE CLIENTES
-- ============================================================
-- Objetivo:
-- Crear la dimensión que almacenará los clientes únicos
-- identificados en las transacciones.
--
-- customer_key será la clave sustituta utilizada por el
-- modelo estrella, mientras que customer_id conserva el
-- identificador original del dataset.

CREATE TABLE dim_customer (
    customer_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL UNIQUE
);

-- ============================================================
-- 02. CREACIÓN DE LA DIMENSIÓN DE PRODUCTOS
-- ============================================================
-- Objetivo:
-- Crear la dimensión que almacenará los productos identificados
-- en el dataset y la categoría a la que pertenece cada producto.
--
-- product_key será la clave sustituta utilizada por el modelo
-- estrella. item conserva el identificador original del producto.

CREATE TABLE dim_product (
    product_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(100) NOT NULL
);


-- ============================================================
-- 03. CREACIÓN DE LA DIMENSIÓN DE FECHAS
-- ============================================================
-- Objetivo:
-- Crear una dimensión calendario que permita analizar las
-- transacciones por año, trimestre, mes y día.
--
-- La dimensión cubrirá todo el período identificado en el
-- dataset: desde 2022-01-01 hasta 2025-01-18.

CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    day INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL
);


-- ============================================================
-- 04. CREACIÓN DE LA DIMENSIÓN DE MÉTODOS DE PAGO
-- ============================================================
-- Objetivo:
-- Crear una dimensión que permita analizar las ventas según
-- el método de pago utilizado en cada transacción.

CREATE TABLE dim_payment_method (
    payment_method_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    payment_method VARCHAR(50) NOT NULL UNIQUE
);


-- ============================================================
-- 05. CREACIÓN DE LA DIMENSIÓN DE UBICACIÓN
-- ============================================================
-- Objetivo:
-- Crear una dimensión que permita analizar las transacciones
-- según el canal o ubicación donde fueron realizadas.

CREATE TABLE dim_location (
    location_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    location VARCHAR(50) NOT NULL UNIQUE
);

-- ============================================================
-- 06. CREACIÓN DE LA TABLA DE HECHOS DE VENTAS
-- ============================================================
-- Objetivo:
-- Crear la tabla central del modelo estrella.
--
-- Cada registro representa una única transacción y contiene
-- las claves que relacionan la venta con sus dimensiones,
-- además de las medidas utilizadas para el análisis.

CREATE TABLE fact_sales (
    transaction_id VARCHAR(50) PRIMARY KEY,

    customer_key INTEGER NOT NULL,
    product_key INTEGER NOT NULL,
    date_key INTEGER NOT NULL,
    payment_method_key INTEGER NOT NULL,
    location_key INTEGER NOT NULL,

    price_per_unit NUMERIC(10, 2) NOT NULL,
    quantity NUMERIC(10, 2) NOT NULL,
    total_spent NUMERIC(12, 2) NOT NULL,

    discount_applied VARCHAR(10) NOT NULL,

    CONSTRAINT fk_fact_customer
        FOREIGN KEY (customer_key)
        REFERENCES dim_customer(customer_key),

    CONSTRAINT fk_fact_product
        FOREIGN KEY (product_key)
        REFERENCES dim_product(product_key),

    CONSTRAINT fk_fact_date
        FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key),

    CONSTRAINT fk_fact_payment_method
        FOREIGN KEY (payment_method_key)
        REFERENCES dim_payment_method(payment_method_key),

    CONSTRAINT fk_fact_location
        FOREIGN KEY (location_key)
        REFERENCES dim_location(location_key)
);