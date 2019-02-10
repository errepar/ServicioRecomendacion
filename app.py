from flask import Flask, jsonify, request
from flask_cors import CORS
from io import StringIO
import pandas as pd
from keras.models import load_model
import pickle
import numpy as np
import sqlite3

app = Flask(__name__)
CORS(app)

clasificador_tema = load_model('./dls/models/recomendador-errepar-tema_83/model.h5')
clasificador_subtema = load_model('./dls/models/recomendador-errepar-subtema_4/model.h5')
clasificador_behaviour = load_model('./dls/models/recomendador-errepar-behaviour_0/model.h5')

diccionario_servicios = pd.read_csv('diccionario_servicios.csv').set_index('servicio').to_dict()['id']
diccionario_subtema_tema = pd.read_csv('diccionario_subtema_tema.csv').set_index('subtema').to_dict()['tema']
diccionario_behaviour_subtema = pd.read_csv('diccionario_behaviour_subtema.csv').set_index('behaviour')\
    .to_dict()['subtema']

data_mapping_tema = pickle.load(open('./dls/models/recomendador-errepar-tema_83/mapping.pkl', mode='rb'))
data_mapping_subtema = pickle.load(open('./dls/models/recomendador-errepar-subtema_4/mapping.pkl', mode='rb'))
data_mapping_behaviour = pickle.load(open('./dls/models/recomendador-errepar-behaviour_0/mapping.pkl', mode='rb'))

connection = sqlite3.connect('errepar-data.db')
cursor = connection.cursor()
query_client_services = open('./sql/get_client_used_services.sql', mode='r', encoding='utf-8').read()


@app.route('/')
def hello_world():
    return jsonify(servicios=diccionario_servicios)


@app.route('/predict', methods=['POST'])
def predict():
    client_data = read_csv_from_request()

    y_tema = make_single_stage_prediction(client_data, data_mapping_tema, clasificador_tema)
    pred_tema, categorias_tema = extract_prediction_from_onehot(y_tema, data_mapping_tema)
    client_data['IdTema'] = pred_tema

    y_subtema = make_single_stage_prediction(client_data, data_mapping_subtema, clasificador_subtema)
    pred_subtema, categorias_subtema = extract_prediction_from_onehot(y_subtema, data_mapping_subtema)
    # pred_subtema = validate_consistency(y_subtema, categorias_subtema, pred_subtema, pred_tema, diccionario_subtema_tema)
    client_data['IdSubtema'] = pred_subtema

    y_behaviour = make_single_stage_prediction(client_data, data_mapping_behaviour, clasificador_behaviour)
    pred_behaviour, categorias_behaviour = extract_prediction_from_onehot(y_behaviour, data_mapping_behaviour)
    # pred_behaviour = validate_consistency(y_behaviour, categorias_behaviour, pred_behaviour, pred_subtema, diccionario_behaviour_subtema)
    client_data['IdBehaviour'] = pred_behaviour

    return jsonify(
        predicciones_raw={
            'tema': y_tema.tolist(),
            'subtema': y_subtema.tolist(),
            'behaviour': y_behaviour.tolist()
        },
        categorias_asociadas={
            'tema': categorias_tema.tolist(),
            'subtema': categorias_subtema.tolist(),
            'behaviour': categorias_behaviour.tolist()
        },
        prediccion_final={
            'tema': client_data['IdTema'],
            'subtema': client_data['IdSubtema'],
            'behaviour': client_data['IdBehaviour']
        }
    )


@app.route('/clientservices/<client_id>', methods=['GET'])
def get_client_used_services(client_id):
    cursor.execute(query_client_services.format(client_id))

    results = cursor.fetchall()
    results = list(map(lambda x: x[0], results))

    return jsonify(servicios=results)


def read_csv_from_request():
    client_data = StringIO(request.files['client_data'].stream.read().decode('utf-8'))
    client_data = pd.read_csv(client_data).to_dict(orient='index')[0]

    return client_data


def make_single_stage_prediction(client_data, data_mapping, clasificador):
    onehot_shape = extract_classifier_input_shape(clasificador)

    vectorized_representation = get_vectorized_representation(client_data, data_mapping, onehot_shape)

    prediction = clasificador.predict(vectorized_representation)

    return prediction


def extract_prediction_from_onehot(onehot_vector, data_mapping):
    categories = data_mapping['outputs']['OutputPort0']['details'][0]['categories']
    onehot_max = np.argmax(onehot_vector)

    final_prediction = int(categories[onehot_max])

    return final_prediction, categories


def validate_consistency(current_pred_raw, categories, current_pred, last_pred, consistency_dict):
    if consistency_dict[current_pred] == last_pred:
        return current_pred

    probabilities_ranking = []
    for prob, cat in zip(current_pred_raw[0].tolist(), categories.tolist()):
        probabilities_ranking.append((prob, cat))

    # probabilities_ranking = zip(current_pred_raw.tolist(), categories)
    probabilities_ranking = sorted(probabilities_ranking, key=lambda tupla: tupla[0], reverse=True)

    for prob_cat in probabilities_ranking:
        if consistency_dict[prob_cat[1]] == last_pred:
            return prob_cat[1]

    raise RuntimeError('validate_consistency: no se encontró consistencia')


def extract_classifier_input_shape(clasificador):
    return 1, clasificador.input.shape[1].value


def get_vectorized_representation(features_dict, data_mapping, shape):
    vectorized_representation = np.array([])
    categorias = list(map(lambda x: x['name'], data_mapping['inputs']['InputPort0']['details']))

    for categoria in categorias:
        associated_onehot = get_associated_onehot(categoria, features_dict[categoria], data_mapping)
        vectorized_representation = np.append(vectorized_representation, associated_onehot)

    vectorized_representation = np.reshape(vectorized_representation, shape)

    return vectorized_representation


def get_associated_onehot(column, value, data_mapping):
    column_detail = list(filter(lambda x: x['name'] == column, data_mapping['inputs']['InputPort0']['details']))[0]

    if column_detail['type'] != 'Categorical':
        return np.array([value])

    if column_detail['name'] in ('localidad_1', 'localidad_2'):
        value = str(value)

    vector_size = len(column_detail['categories'])
    index_in_onehot = np.where(column_detail['categories'] == value)[0][0]

    onehot_vector = np.zeros(vector_size)
    onehot_vector[index_in_onehot] = 1.0

    return onehot_vector


if __name__ == '__main__':
    app.run()
