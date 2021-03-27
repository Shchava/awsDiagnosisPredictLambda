import json

import boto3

def lambda_handler(event, context):
    endpoint_name = 'sagemaker-tensorflow-serving-2021-03-27-15-35-15-207'

    sagemakerClient = boto3.client('runtime.sagemaker')
    s3_client = boto3.resource('s3')

    data = [0] * 131

    symptoms_list_object = s3_client.Object('medical.train.data', 'dataMapping/symptomNamesList.json')
    symptoms_list_file = symptoms_list_object.get()['Body'].read().decode('utf-8')
    symptoms_list = json.loads(symptoms_list_file)

    for symptom in event['symptoms']:
        symptom_index = symptoms_list.index(symptom)
        data[symptom_index] = 1

    response = sagemakerClient.invoke_endpoint(EndpointName=endpoint_name,
                                               ContentType='application/json',
                                               Body=json.dumps(data))
    response_body = response['Body']
    response_payload = json.loads(response_body.read().decode("utf-8"))

    predictions = response_payload['predictions'][0]

    dignosis_probability = max(predictions)
    dignosis_id = predictions.index(dignosis_probability)

    diagnoses_dict_object = s3_client.Object('medical.train.data', 'dataMapping/diagnosesDict.json')
    diagnoses_dict_file = diagnoses_dict_object.get()['Body'].read().decode('utf-8')
    diagnoses_dict = json.loads(diagnoses_dict_file)

    dignosis_name = diagnoses_dict[str(dignosis_id)]

    response = {}
    response['diagnosis'] = dignosis_name
    response['probability'] = dignosis_probability

    return {
        'statusCode': 200,
        'body': response
    }
