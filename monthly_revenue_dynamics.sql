-- Задача: Рассчитать ежемесячную выручку и суммарную выручку за все ПРЕДЫДУЩИЕ периоды
-- Важно для анализа темпов роста (MoM) и накопленного профита

WITH monthly_data AS (
    SELECT 
        DATE_TRUNC('month', o.order_created_time)::DATE AS category_month,
        p.product_category_name,
        SUM(oi.price) AS monthly_revenue
    FROM orders o
    JOIN order_items oi USING(order_id)
    JOIN products p USING(product_id)
    GROUP BY 1, 2
)
SELECT 
    category_month,
    product_category_name,
    COALESCE(monthly_revenue, 0) AS monthly_revenue,
    -- Используем рамку до 1 PRECEDING, чтобы текущий месяц не входил в "предыдущие"
    COALESCE(
        SUM(monthly_revenue) OVER (
            PARTITION BY product_category_name 
            ORDER BY category_month
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ), 
    0) AS total_revenue_before_this_month
FROM monthly_data
ORDER BY product_category_name, category_month;
