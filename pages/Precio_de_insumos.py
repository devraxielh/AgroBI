import streamlit as st
from sqlalchemy import URL,create_engine, text
import plotly.express as px
import pandas as pd
from datetime import date,timedelta
import pmdarima as pm
from sympy import Point
st.set_page_config(layout="wide")
url_object = URL.create(
    "mysql+mysqlconnector",
    username="adminbi",
    password="Unicordoba@23",
    host="ec2-18-221-11-203.us-east-2.compute.amazonaws.com",
    database="insumos",
)
df = pd.DataFrame()
try:
    engine = create_engine(url_object)
    sql_query = text("SELECT * FROM vista_precios")
    df = pd.read_sql(sql_query, engine.connect())
except Exception as e:
    print(str(e))

with st.sidebar:
    dep = st.selectbox('Seleccionar departamento',df['departamento_nombre'].unique())
    filtro_departamento = 'departamento_nombre=="%s"'% dep
    muni = st.selectbox('Seleccionar municipio',df.query(filtro_departamento)['municipio_nombre'].unique())
    filtro_municipio = 'municipio_nombre=="%s"'% muni
    filtro_de_mu = filtro_departamento+' and '+filtro_municipio
    prod = st.selectbox('Seleccionar producto',df.query(filtro_de_mu)['producto_nombre'].unique())
    filtro_producto = 'producto_nombre=="%s"'% prod
    filtro_de_mu_pr = filtro_de_mu +' and '+filtro_producto

unano = date.today()
hoy = date.today()
unano -= timedelta(days=365)
col1, col2, col3, col4 = st.columns(4)
with col1:
    fi = st.date_input("Fecha Inicio", unano)
with col2:
    ff = st.date_input("Fecha Final", hoy)
with col3:
    option = st.selectbox('Frecuencia de los datos',('Mensual','Quincenal','Semanal'))
with col4:
    number = st.number_input('Cantidad %s a predecir'%option, 1, 10, 1)

if option == 'Mensual':
    frecuencia = 'M'
elif option == 'Quincenal':
    frecuencia = '15D'
else:  
    frecuencia = 'W'
df = df.query(filtro_de_mu_pr)
df = df.loc[df["fechapublicacion"].between(str(fi),str(ff))]

df.set_index('fechapublicacion', inplace=True)
df = df['valor']
df = df.asfreq(frecuencia, method='ffill')
model = pm.auto_arima(df)
pred = model.predict(n_periods=number)

lista = []
for i in range(len(pred)+1):
    if i == 0:
        lista.append([df.tail(1).index.values[0],df.tail(1).values[0]])
    else:
        lista.append([pred.index.values[i-1],pred[i-1]])

pred = pd.DataFrame(lista)
pred.set_index(0, inplace=True)
df = pd.DataFrame(df)
df['grupo']='Historico'
pred['grupo']='Prediccion'
pred.rename(columns={1:'valor'}, inplace=True)
total = pd.concat([df,pred], axis=0)
fig = px.line(total, x=total.index, y='valor', color='grupo', symbol='grupo', symbol_map={'Historico': 'square', 'Prediccion': 'cross'}, title='Gráfica con la prediccion %s de precios de insumos' % option, color_discrete_map={'Historico': 'green', 'Prediccion': 'blue'})
fig.update_traces(line={'width': 3})
st.plotly_chart(fig, use_container_width=True)

co1, co2 = st.columns(2)
with co1:
    st.write(model.summary())
with co2:
    st.write(total, use_container_width=True)