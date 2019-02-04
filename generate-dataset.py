import sqlite3
import pandas as pd
import re
import csv
from zipfile import ZipFile


query_servicios = open('./sql/search_most_used.sql', mode='r', encoding='utf-8').read()
query_clientes = open('./sql/get_clients.sql', mode='r', encoding='utf-8').read()
query_suscripciones = open('./sql/get_client_suscriptions.sql', mode='r', encoding='utf-8').read()
query_domicilios = open('./sql/get_client_address.sql', mode='r', encoding='utf-8').read()

connection = sqlite3.connect('errepar-data.db')
cursor = connection.cursor()

cursor.execute(query_clientes)
clientes = list(map(lambda cliente: cliente[0], cursor.fetchall()))


def get_client_n_most_used_services(client_code, n):
    cursor.execute(query_servicios.format(client_code, n))

    headers = list(map(lambda x: x[0], cursor.description))
    headers.extend([('suscripcion_' + str(i)) for i in range(1, 15)])
    headers.extend([('localidad_' + str(i)) for i in range(1, 3)])

    results = cursor.fetchall()

    return headers, results


def get_client_suscriptions(client_code):
    cursor.execute(query_suscripciones.format(client_code))

    suscriptions = list(map(lambda x: x[0].strip(), cursor.fetchall()))
    suscriptions = list(map(lambda x: x.replace(',', ''), suscriptions))
    suscriptions = list(map(lambda x: x.replace('.', ''), suscriptions))
    suscriptions = list(map(lambda x: x.replace('(', ''), suscriptions))
    suscriptions = list(map(lambda x: x.replace(')', ''), suscriptions))
    suscriptions = list(map(lambda x: x.replace('-', ''), suscriptions))
    suscriptions = list(map(lambda x: x.replace('+', ''), suscriptions))
    suscriptions = list(map(lambda x: x.replace('/', ''), suscriptions))

    return suscriptions


def get_client_address(client_code):
    cursor.execute(query_domicilios.format(client_code))

    return list(map(lambda x: x[0].strip(), cursor.fetchall()))


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

    if aux == '[No Per. Consec.]':
        return 'None'

    if aux == '':
        return 'None'

    return aux


def extract_years(text):
    matches = re.search('[0-9]+', text)

    if matches is None:
        return text

    return matches.group(0)


def format_number(text):
    aux = extract_years(text)

    aux = aux.replace('None', '0')
    aux = aux.replace('>=', '')
    aux = aux.replace('<=', '')

    return aux


def format_score(value):
    return value.replace('None', '0.0')


def format_persona_juridica_fisica(value):
    return value.replace('None', '2')


limitar_cantidad_clientes = False
cantidad_clientes_buscar = 20

n_max_servicios = 5
factor_replicacion = 10
max_suscripciones = 14
max_domicilios = 2

contador = 0
maximo = len(clientes)

df = pd.DataFrame()
for cliente in clientes:
    header, datos = get_client_n_most_used_services(cliente, n_max_servicios)
    datos = list(map(lambda lista: list(map(lambda x: clean_values(str(x)), lista)), datos))

    suscripciones = get_client_suscriptions(cliente)
    suscripciones.extend(['0' for i in range(0, max_suscripciones - len(suscripciones))])
    domicilios = get_client_address(cliente)
    domicilios.extend(['0' for i in range(0, max_domicilios - len(domicilios))])

    for lista in datos:
        lista.extend(suscripciones)
        lista.extend(domicilios)

    df_aux = pd.DataFrame(data=datos, columns=header)
    df_aux['TotalVisitas'] = pd.to_numeric(df_aux['CantidadVisitas']).sum()
    df_aux['Proporcion'] = (pd.to_numeric(df_aux['CantidadVisitas']) / pd.to_numeric(df_aux['TotalVisitas'])).round(2)
    df_aux['CantidadReplicaciones'] = (df_aux['Proporcion'] * factor_replicacion).round()

    df = df.append(df_aux)

    contador += 1
    print('Procesando cliente {0}'.format(contador))

    if limitar_cantidad_clientes and clientes.index(cliente) + 1 == cantidad_clientes_buscar:
        break


df['Edad'] = df['Edad'].apply(lambda x: format_number(x))
df['TasaEOL'] = df['TasaEOL'].apply(lambda x: format_number(x))
df['TasaIUS'] = df['TasaIUS'].apply(lambda x: format_number(x))
df['TipoPersona'] = df['TipoPersona'].apply(lambda x: format_persona_juridica_fisica(x))
df['DebitoAutomatico'] = df['DebitoAutomatico'].apply(lambda x: format_persona_juridica_fisica(x))
df['Score'] = df['Score'].apply(lambda x: format_score(x))

df.to_csv('./dls/datasets/dataset_intermedio.csv', index=False, sep=';')


csv_file = open('./dls/datasets/dataset_intermedio.csv', mode='r')
csv_reader = csv.reader(csv_file, delimiter=';')
csv_rows = list(csv_reader)

# Elimino el header del CSV
header = csv_rows[0]

del csv_rows[0]

# posicion_cantidad_replicaciones = 13
posicion_cantidad_replicaciones = len(df.columns) - 1

final_csv = []
# for row in csv_rows:
for i in range(0, len(csv_rows)):
    print('Procesando fila {0} de {1}'.format(i, len(csv_rows)))

    row = csv_rows[i]

    # Agrego UNO por las filas que no tienen replicación
    cantidad_replicaciones = round(float(row[posicion_cantidad_replicaciones]) + 1)

    # Replico las filas según la cantidad especificada en el último campo del CSV
    for j in range(0, cantidad_replicaciones):
        final_csv.append(row)

df = pd.DataFrame(data=final_csv, columns=header)
del df['CantidadReplicaciones']
del df['Proporcion']
del df['TotalVisitas']
del df['CantidadVisitas']

del df['CodigoCliente']
del df['NameTema']
del df['NameBehaviour']

servicios = df['suscripcion_1']\
    .append(df['suscripcion_2'])\
    .append(df['suscripcion_3'])\
    .append(df['suscripcion_4'])\
    .append(df['suscripcion_5'])\
    .append(df['suscripcion_6'])\
    .append(df['suscripcion_7'])\
    .append(df['suscripcion_8'])\
    .append(df['suscripcion_9'])\
    .append(df['suscripcion_10'])\
    .append(df['suscripcion_11'])\
    .append(df['suscripcion_12'])\
    .append(df['suscripcion_13'])\
    .append(df['suscripcion_14'])\
    .unique()

dict_servicios = dict(zip(servicios, range(0, len(servicios))))

df = df.replace({'suscripcion_1': dict_servicios})\
    .replace({'suscripcion_2': dict_servicios})\
    .replace({'suscripcion_3': dict_servicios})\
    .replace({'suscripcion_4': dict_servicios})\
    .replace({'suscripcion_5': dict_servicios})\
    .replace({'suscripcion_6': dict_servicios})\
    .replace({'suscripcion_7': dict_servicios})\
    .replace({'suscripcion_8': dict_servicios})\
    .replace({'suscripcion_9': dict_servicios})\
    .replace({'suscripcion_10': dict_servicios})\
    .replace({'suscripcion_11': dict_servicios})\
    .replace({'suscripcion_12': dict_servicios})\
    .replace({'suscripcion_13': dict_servicios})\
    .replace({'suscripcion_14': dict_servicios})

df.to_csv('./dls/datasets/train.csv', index=False, sep=',')

zf = ZipFile('./dls/datasets/dataset_final.zip', mode='w')
zf.write('./dls/datasets/train.csv')
zf.close()
