import streamlit as st
import pandas as pd
import plotly.express as px

# Настройка страницы дашборда
st.set_page_config(page_title="Дашборд: Анализ чаевых", layout="wide")

# 1. Загрузка данных
@st.cache_data
def load_data():
    # Автоматически загружаем встроенный датасет tips из seaborn
    import seaborn as sns
    df = sns.load_dataset('tips')
    # Добавляем ваш расчетный столбец процента чаевых из работы
    df['tip_percent'] = (df['tip'] / df['total_bill']) * 100
    return df

tips = load_data()

# Заголовок дашборда
st.title("Интерактивный дашборд: Счета и чаевые в ресторане")
st.markdown("Финальный проект: Исследовательский анализ датасета tips")

# --- БОКОВАЯ ПАНЕЛЬ С ФИЛЬТРАМИ ---
st.sidebar.header("Фильтры данных")

# Фильтр по дням недели
all_days = tips['day'].unique().tolist()
selected_days = st.sidebar.multiselect("Выберите дни недели:", all_days, default=all_days)

# Фильтр по времени суток
all_times = tips['time'].unique().tolist()
selected_times = st.sidebar.multiselect("Выберите время суток:", all_times, default=all_times)

# Фильтр по курению
smoker_filter = st.sidebar.radio("Статус курения гостей:", ["Все", "Курящие", "Некурящие"])

# Применение фильтров к датасету
filtered_tips = tips[
    (tips['day'].isin(selected_days)) & 
    (tips['time'].isin(selected_times))
]

if smoker_filter == "Курящие":
    filtered_tips = filtered_tips[filtered_tips['smoker'] == 'Yes']
elif smoker_filter == "Некурящие":
    filtered_tips = filtered_tips[filtered_tips['smoker'] == 'No']


# --- БЛОК С ОСНОВНЫМИ МЕТРИКАМИ (KPI) ---
st.subheader("Ключевые показатели (KPI)")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Всего чеков", len(filtered_tips))
with col2:
    st.metric("Средний чек", f"${filtered_tips['total_bill'].mean():.2f}")
with col3:
    st.metric("Средние чаевые", f"${filtered_tips['tip'].mean():.2f}")
with col4:
    st.metric("Медианный процент чаевых", f"{filtered_tips['tip_percent'].median():.2f}%")


# --- БЛОК ВИЗУАЛИЗАЦИИ ---
st.markdown("---")
st.subheader("Анализ зависимостей и распределений")

# Ряд 1: Связь счета и чаевых + Процент чаевых по дням
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.markdown("**Связь между суммой счета и чаевыми**")
    fig_scatter = px.scatter(
        filtered_tips,
        x='total_bill',
        y='tip',
        color='day',
        size='size',
        hover_data=['sex', 'smoker', 'time', 'tip_percent'],
        labels={'total_bill': 'Сумма счета ($)', 'tip': 'Чаевые ($)', 'day': 'День', 'size': 'Размер компании'}
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with row1_col2:
    st.markdown("**Распределение процента чаевых по дням недели (Boxplot)**")
    fig_box = px.box(
        filtered_tips,
        x='day',
        y='tip_percent',
        color='day',
        labels={'day': 'День недели', 'tip_percent': 'Процент чаевых (%)'}
    )
    st.plotly_chart(fig_box, use_container_width=True)

# Ряд 2: Средние чаевые по категориям
st.markdown("---")
st.subheader("Сравнение чаевых по категориям")
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.markdown("**Средний размер чаевых по дням недели**")
    df_day_mean = filtered_tips.groupby('day', as_index=False, observed=False)['tip'].mean().round(2)
    fig_bar_day = px.bar(
        df_day_mean, x='day', y='tip', color='day',
        labels={'day': 'День недели', 'tip': 'Средние чаевые ($)'}, text_auto=True
    )
    st.plotly_chart(fig_bar_day, use_container_width=True)

with row2_col2:
    st.markdown("**Средний процент чаевых в зависимости от размера компании**")
    df_size_mean = filtered_tips.groupby('size', as_index=False, observed=False)['tip_percent'].mean().round(2)
    fig_bar_size = px.bar(
        df_size_mean, x='size', y='tip_percent',
        labels={'size': 'Размер компании (чел.)', 'tip_percent': 'Средний процент чаевых (%)'},
        text_auto=True, color_discrete_sequence=['#45039f']
    )
    st.plotly_chart(fig_bar_size, use_container_width=True)


# --- ТАБЛИЦА ДАННЫХ ---
st.markdown("---")
with st.expander("Посмотреть отфильтрованные сырые данные"):
    st.dataframe(filtered_tips, use_container_width=True)
