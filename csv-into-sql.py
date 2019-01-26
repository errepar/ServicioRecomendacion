# SCRIPT QUE LEVANTA LOS CSV Y LOS GUARDA EN UN SQLITE

import pandas as pd
import sqlite3

# Cargar cada CSV en un DataFrame
temas = pd.read_csv('./data/AS_Temas.csv', sep=';')
subtemas = pd.read_csv('./data/AS_SubTemas.csv', sep=';')
behaviours = pd.read_csv('./data/AS_TypesOfBehaviour.csv', sep=';')
behaviours_data = pd.read_csv('./data/GetBehaviurData.csv', sep=';')
behaviours_data_client = pd.read_csv('./data/get_BehaviuorDataClient.csv', sep=';')
no_aciertos = pd.read_csv('./data/AS_NoAciertosByLink.csv', sep=';')

# Burocracia para conectar a SQLite
connection = sqlite3.connect('errepar-data.db')

# Cada DataFrame se guarda en su respectiva tabla
temas.to_sql('temas', connection, if_exists='replace')
subtemas.to_sql('subtemas', connection, if_exists='replace')
behaviours.to_sql('behaviours', connection, if_exists='replace')
behaviours_data.to_sql('behaviours_data', connection, if_exists='replace')
behaviours_data_client.to_sql('behaviours_data_client', connection, if_exists='replace')
no_aciertos.to_sql('no_aciertos', connection, if_exists='replace')

# Burocracia para confirmar y cerrar la conexión
connection.commit()
connection.close()
