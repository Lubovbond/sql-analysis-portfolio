-- Задача: Выявить бренды, чья средняя цена значительно (на 20%+) выше средней цены по магазину
-- Позволяет отделу закупок находить премиальный сегмент

SELECT 
    product_brand, 
    ROUND(AVG(price)::numeric, 2) AS brand_avg_price,
    -- Показываем общую среднюю цену для наглядности сравнения
    ROUND((SELECT AVG(price) FROM order_items)::numeric, 2) AS market_avg_price
FROM products
JOIN order_items USING(product_id)
GROUP BY product_brand
-- Фильтруем только те бренды, где средняя цена > (общая средняя * 1.2)
HAVING AVG(price) > (SELECT AVG(price) FROM order_items) * 1.2
ORDER BY brand_avg_price DESC;
