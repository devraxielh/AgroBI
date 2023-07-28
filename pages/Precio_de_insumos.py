import streamlit as st
import numpy as np
import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
from PIL import Image
import mysql.connector as connection
import pandas as pd
try:
    mydb = connection.connect(host="localhost", database = 'db',user="admin", passwd="admin",use_pure=True)
    query = """
Select 
h.vr_unitario as Valor,h.fecha,p.nombre as producto,n.razon_social,tp.nombre as tipo,m.nombre as municipio,d.nombre as departamento,z.nombre as zona 
from db.historico_precios h,db.productos p,db.negocios n,db.tipo_productos tp,db.municipios m,db.departamentos d,db.zonas z 
where 
h.productos_id = p.id 
and 
h.negocios_id = n.id 
and
p.tipo_productos_id = tp.id 
and
n.municipios_id = m.id 
and
m.departamentos_id = d.id
and
m.zonas_id = z.id 
    """
    df = pd.read_sql(query,mydb)
    mydb.close() #close the connection
except Exception as e:
    mydb.close()
    print(str(e))

with st.sidebar:
  dep = st.selectbox('Seleccionar departamento',df['departamento'].unique())
  zona = st.selectbox('Seleccionar zona',df.query('departamento=="'+dep+'"')['zona'].unique())
  muni = st.selectbox('Seleccionar municipio',df.query('departamento=="'+dep+'" and zona=="'+zona+'"')['municipio'].unique())
  tipo = st.selectbox('Seleccionar tipo de producto',df.query('departamento=="'+dep+'" and zona=="'+zona+'" and municipio=="'+muni+'" ')['tipo'].unique())
  razon = st.selectbox('Seleccionar razon social',df.query('departamento=="'+dep+'" and zona=="'+zona+'" and municipio=="'+muni+'" ')['razon_social'].unique())
  prod = st.selectbox('Seleccionar producto',df.query('departamento=="'+dep+'" and zona=="'+zona+'" and municipio=="'+muni+'" and tipo=="'+tipo+'" and razon_social=="'+razon+'"')['producto'].unique())

df = df.query('departamento=="'+dep+'" and zona=="'+zona+'" and municipio=="'+muni+'" and tipo=="'+tipo+'" and razon_social=="'+razon+'" and producto=="'+prod+'" ')

df = df[['fecha','Valor']]
df.index = df['fecha']
df = df.drop(['fecha'],axis=1)

tab1, tab2 = st.tabs(["📈 Grafico", "🗃 Datos"])
data = np.random.randn(10, 1)

tab1.line_chart(df)
tab2.dataframe(df)