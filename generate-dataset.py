import sqlite3
import pandas as pd
import re


connection = sqlite3.connect('errepar-data.db')
cursor = connection.cursor()
query_servicios = open('search_most_used.sql', mode='r', encoding='utf-8').read()
query_clientes = open('get_clients.sql', mode='r', encoding='utf-8').read()

cursor.execute(query_clientes)
clientes = list(map(lambda cliente: cliente[0], cursor.fetchall()))


def get_client_n_most_used_services(client_code, n):
    cursor.execute(query_servicios.format(client_code, n))
    headers = list(map(lambda x: x[0], cursor.description))
    results = cursor.fetchall()
    return headers, results


def clean_values(value):
    aux = value.strip()

    if aux == 'ND':
        return 'None'

    if aux == 'SC':
        return 'None'

    if aux == 'N':
        return '0'

    if aux == 'S':
        return '1'

    if aux == 'PJ':
        return '1'

    if aux == 'PF':
        return '0'

    return aux


def extract_years(text):
    matches = re.search('[0-9]+', text)

    if matches is None:
        return text

    return matches.group(0)


limitar_cantidad_clientes = True
cantidad_clientes_buscar = 20

n_max_servicios = 5
factor_replicacion = 10

contador = 0
maximo = len(clientes)

df = pd.DataFrame()
for cliente in clientes:
    header, datos = get_client_n_most_used_services(cliente, n_max_servicios)
    datos = list(map(lambda lista: list(map(lambda x: clean_values(str(x)), lista)), datos))

    df_aux = pd.DataFrame(data=datos, columns=header)
    df_aux['TotalVisitas'] = pd.to_numeric(df_aux['CantidadVisitas']).sum()
    df_aux['Proporcion'] = (pd.to_numeric(df_aux['CantidadVisitas']) / pd.to_numeric(df_aux['TotalVisitas'])).round(2)
    df_aux['CantidadReplicaciones'] = (df_aux['Proporcion'] * factor_replicacion).round()

    df = df.append(df_aux)

    contador += 1
    print('Procesando cliente {0}'.format(contador))

    if limitar_cantidad_clientes and clientes.index(cliente) + 1 == cantidad_clientes_buscar:
        break


df['TasaEOL'] = df['TasaEOL'].apply(lambda x: extract_years(x))
df['TasaIUS'] = df['TasaIUS'].apply(lambda x: extract_years(x))

df.to_csv('dataset_intermedio.csv', index=False, sep=';')
