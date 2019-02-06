from flask import Flask, jsonify
import pandas as pd
from keras.models import load_model
import pickle
import numpy as np

app = Flask(__name__)

clasificador_tema = load_model('./dls/models/recomendador-errepar-tema_83/model.h5')
clasificador_subtema = load_model('./dls/models/recomendador-errepar-subtema_4/model.h5')
clasificador_behaviour = load_model('./dls/models/recomendador-errepar-behaviour_0/model.h5')

diccionario_servicios = pd.read_csv('diccionario_servicios.csv').set_index('servicio').to_dict()['id']

data_mapping_tema = pickle.load(open('./dls/models/recomendador-errepar-tema_83/mapping.pkl', mode='rb'))
data_mapping_subtema = pickle.load(open('./dls/models/recomendador-errepar-subtema_4/mapping.pkl', mode='rb'))
data_mapping_behaviour = pickle.load(open('./dls/models/recomendador-errepar-behaviour_0/mapping.pkl', mode='rb'))


@app.route('/')
def hello_world():
    return jsonify(servicios=diccionario_servicios)


@app.route('/predict')
def predict():
    # client_data = {}  # Parte del body del GET
    client_data = pd.read_csv('prueba.csv').to_dict(orient='index')[0]  # PROVISORIO!!

    y_tema = make_single_stage_prediction(client_data, data_mapping_tema, clasificador_tema)
    client_data['IdTema'] = extract_prediction_from_onehot(y_tema, data_mapping_tema)

    y_subtema = make_single_stage_prediction(client_data, data_mapping_subtema, clasificador_subtema)
    client_data['IdSubtema'] = extract_prediction_from_onehot(y_subtema, data_mapping_subtema)

    y_behaviour = make_single_stage_prediction(client_data, data_mapping_behaviour, clasificador_behaviour)
    client_data['IdBehaviour'] = extract_prediction_from_onehot(y_behaviour, data_mapping_behaviour)

    return jsonify(
        tema=y_tema.tolist(), subtema=y_subtema.tolist(), behaviour=y_behaviour.tolist(),
        tema_final=client_data['IdTema'],
        subtema_final=client_data['IdSubtema'],
        behaviour_final=client_data['IdBehaviour']
    )


def make_single_stage_prediction(client_data, data_mapping, clasificador):
    onehot_shape = extract_classifier_input_shape(clasificador)

    vectorized_representation = get_vectorized_representation(client_data, data_mapping, onehot_shape)

    prediction = clasificador.predict(vectorized_representation)

    return prediction


def extract_classifier_input_shape(clasificador):
    return 1, clasificador.input.shape[1].value


def extract_prediction_from_onehot(onehot_vector, data_mapping):
    categories = data_mapping['outputs']['OutputPort0']['details'][0]['categories']
    onehot_max = np.argmax(onehot_vector) + 1

    return int(categories[onehot_max])


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
