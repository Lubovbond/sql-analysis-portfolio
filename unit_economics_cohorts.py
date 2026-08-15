import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import colors

df = pd.read_csv("Данные.csv")
df_copy = df.copy()

# Переводим в дату и усекаем время до дня
df_copy['dlk_cob_date'] = pd.to_datetime(df_copy['dlk_cob_date']).dt.normalize()

# Находим ТОЧНУЮ ДАТУ первого действия пользователя (а не месяц)
df_copy['first_date'] = df_copy.groupby("user_id")["dlk_cob_date"].transform('min')

# На основе первой даты определяем календарный месяц когорты (для строк графика)
df_copy['cohort'] = df_copy['first_date'].dt.to_period('M')

# Считаем разницу в ДНЯХ между текущим платежом и самым первым
df_copy['days_lifespan'] = (df_copy['dlk_cob_date'] - df_copy['first_date']).dt.days

# Переводим дни в 30-дневные периоды (0, 1, 2...) строго по методологии лекции
df_copy['cohort_lifetime_m'] = df_copy['days_lifespan'] // 30

# Агрегируем уникальных пользователей
cohorts = df_copy.groupby(['cohort', 'cohort_lifetime_m']).agg({'user_id': 'nunique'}).reset_index()
cohorts = cohorts.rename(columns={'user_id': 'total_users'})

# Строим базовую матрицу в абсолютных числах
retention_matrix = cohorts.pivot(index='cohort', columns='cohort_lifetime_m', values='total_users')

# Вытаскиваем размеры когорт (столбец 0) для левого белого графика
cohort_size = retention_matrix.iloc[:, 0]

# Переводим основную матрицу в проценты (начиная с 0-го месяца жизни)
retention_rate_matrix = retention_matrix.divide(cohort_size, axis=0)

# ЧАСТЬ 2: Отрисовка сдвоенного графика

with sns.axes_style("white"):
    fig, ax = plt.subplots(1, 2, figsize=(16, 12), sharey=True, gridspec_kw={'width_ratios': [1, 11]})
    
    # Правая большая тепловая карта для коэффициентов удержания
    sns.heatmap(retention_rate_matrix,
                mask=retention_rate_matrix.isnull(),
                annot=True,
                fmt='.0%',  # Выводит знак процента автоматически
                cmap='RdYlGn',
                ax=ax[1])
    ax[1].set_title('Monthly Retention', fontsize=16)
    ax[1].set(xlabel='№ периода', ylabel='')
    
    # Левая узкая тепловая карта для размеров когорт (на белом фоне)
    cohort_size_df = pd.DataFrame(cohort_size).rename(columns={0: 'cohort_size'})
    white_cmap = colors.ListedColormap(['white'])
    sns.heatmap(cohort_size_df,
                annot=True,
                cbar=False,
                fmt='g',  # Выводит обычные целые числа
                cmap=white_cmap,
                ax=ax[0])
    ax[0].set(ylabel='Когорта')
                
    fig.tight_layout()
    plt.show()

# ЧАСТЬ 3: Расчет переменных затрат за 15 месяцев (Включая нулевой)

# Комиссия банка: 5 руб * 100 платежей = 500 руб в месяц на активного клиента
variable_cost_per_month = 500  

# Вытаскиваем первые 15 месяцев жизни когорты апреля 2023 (периоды от 0 до 14 включительно)
retention_15_months = retention_rate_matrix.loc['2023-04'].iloc[0:15]

# Умножаем 500 рублей на процент выживших в каждый из 15 периодов и суммируем
total_variable_costs = (retention_15_months * variable_cost_per_month).sum()

import math
print(f"Переменные затраты на среднего клиента за 15 месяцев (включая нулевой): {math.ceil(total_variable_costs)} руб.")

# 1. Задаем базовые данные для расчета

variable_costs = 2345  # накопленные переменные затраты из прошлого шага
cost_per_month = 500  # Затраты в месяц (5 руб * 100 платежей)
revenue_per_month = 1530  # Выручка в месяц (1500 руб комиссия + 30 руб реклама)
cac_paying = 7300  # Стоимость привлечения платящего (146 руб / 0.02)

# 2. Считаем суммарный коэффициент Retention за 15 месяцев (количество "активных месяцев")
retention_sum = variable_costs / cost_per_month

# Пункт 1: Накопленная выручка клиента
nakop_revenue = retention_sum * revenue_per_month

# Пункт 2: Переменные затраты на клиента
   # Это и есть наши 2344.5 рублей

# Пункт 3: Находим LTV (Выручка минус Затраты)
ltv_exact = nakop_revenue - variable_costs

# --- Финальное сопоставление ---
final_difference = ltv_exact - cac_paying
ltv_cac_ratio = ltv_exact / cac_paying

print("\n" + "=" * 40)
print("ФИНАЛЬНЫЙ АНАЛИТИЧЕСКИЙ ВЕРДИКТ БИЗНЕСУ:")
print("" * 40)
print(f"Финансовая разность (LTV - CAC): {final_difference:.2f} руб.")
print(f"Относительное соотношение (LTV / CAC): {ltv_cac_ratio:.2f}")

if final_difference > 0:
    print("📈 Юнит-экономика СХОДИТСЯ. Продукт зарабатывает на пользователях.")
    if ltv_cac_ratio >= 3:
        print("     Модель идеальна (LTV/CAC >= 3). Можно агрессивно масштабироваться!")
    else:
        print("     Модель хрупкая (LTV/CAC < 3). Опасно масштабировать, косты рекламы могут сожрать прибыль.")
else:
    print("📉 Юнит-экономика НЕ СХОДИТСЯ. Продукт работает в убыток с каждого юзера.")
    print("     Масштабирование запрещено. Нужно чинить конверсию или снижать стоимость клика.")
print("=" * 40)
