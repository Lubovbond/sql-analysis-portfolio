# Анализ пользовательских сессий
В этом кейсе я рассчитываю уникальные ID сессий для клиентов на основе 30-минутного окна неактивности.

### Использованные инструменты:
- CTE (временные таблицы)
- Оконные функции: `LAG`, `SUM() OVER`
- Условная логика `CASE WHEN`

WITH events_with_lag AS (
    SELECT
        customer_id,
        event_timestamp,
        -- Находим время предыдущего события внутри группы клиента
        LAG(event_timestamp) OVER (
            PARTITION BY customer_id
            ORDER BY event_timestamp
        ) AS prev_event_time
    FROM customer_actions
),
session_boundaries AS (
    -- Размечаем границы сессий: 1 — начало новой сессии, 0 — продолжение текущей
    SELECT
        customer_id,
        event_timestamp,
        CASE 
            WHEN prev_event_time IS NULL
                 OR (event_timestamp - prev_event_time) > INTERVAL '30 minutes'
                THEN 1
            ELSE 0
        END AS is_new_session
    FROM events_with_lag
),
sessions AS (
    -- Генерируем порядковый номер сессии через накопительную сумму флагов
    SELECT
        customer_id,
        event_timestamp,
        SUM(is_new_session) OVER (
            PARTITION BY customer_id
            ORDER BY event_timestamp
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS session_num
    FROM session_boundaries
)
-- Финальный вывод с формированием уникального идентификатора сессии
SELECT 
    customer_id,
    event_timestamp,
    CONCAT(customer_id, '_', session_num) AS session_id
FROM sessions;

