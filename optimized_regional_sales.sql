-- Задача: Найти топ-10 клиентов из Москвы, совершивших заказы в 2024 году, по сумме трат.
-- Оптимизация: Фильтруем таблицы ДО объединения (JOIN), чтобы снизить нагрузку на память.

WITH filtered_customers AS (
    -- Отрезаем лишние регионы сразу
    SELECT customer_id, customer_city
    FROM customers
    WHERE customer_city = 'Москва'
),
filtered_orders AS (
    -- Отрезаем старые года и недоставленные заказы
    SELECT order_id, customer_id
    FROM orders
    WHERE order_created_time >= '2024-01-01'
      AND order_status = 'Delivered'
),
order_totals AS (
    -- Считаем стоимость заказов перед финальным джоином
    SELECT order_id, SUM(price) AS order_sum
    FROM order_items
    GROUP BY order_id
)
SELECT 
    c.customer_id,
    c.customer_city,
    ROUND(SUM(ot.order_sum)::numeric, 2) AS total_spent
FROM filtered_customers c
JOIN filtered_orders o USING(customer_id)
JOIN order_totals ot USING(order_id)
GROUP BY 1, 2
ORDER BY total_spent DESC
LIMIT 10;
