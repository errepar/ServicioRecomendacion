import pandas as pd

# Organización (niveles de indirección)
temas = pd.read_csv('./data/AS_Temas.csv', sep=';')
subtemas = pd.read_csv('./data/AS_SubTemas.csv', sep=';')
behaviours = pd.read_csv('./data/AS_TypesOfBehaviour.csv', sep=';')

behaviours_data = pd.read_csv('./data/GetBehaviurData.csv', sep=';')
behaviours_data_client = pd.read_csv('./data/get_BehaviuorDataClient.csv', sep=';')
no_aciertos = pd.read_csv('./data/AS_NoAciertosByLink.csv', sep=';')

print('que onda bigote')
