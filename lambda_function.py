import boto3
import json
import urllib.parse
import os
from openai import OpenAI

# Configura el cliente OpenAI
client = OpenAI()

# Define las variables de entorno
output_bucket = os.environ['OUTPUT_BUCKET']
output_key = os.environ['OUTPUT_KEY']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

def lambda_handler(event, context):
    # Inicializa el cliente S3
    s3_client = boto3.client('s3', region_name='eu-west-1')

    # Obtén el nombre del bucket y la clave del archivo subido del evento de S3
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    document_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    # Construye la URL de la imagen almacenada en S3
    image_url = f"https://{bucket_name}.s3.eu-west-1.amazonaws.com/{document_key}"

    # Construye y envía la solicitud a la API de GPT-4
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "You are an expert at reading invoices and returning data in a Python-valid JSON format. Extract the date, address, total amount, and invoice number from this invoice and return ONLY a compact, single-line JSON object without unnecessary whitespace or slashes, containing this information."},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ],
        max_tokens=300
    )

    # Extrae la respuesta y estructura los datos
    extracted_data = response.choices[0].message.content
    # Convierte la información extraída a JSON

    # Guarda la información extraída en S3 como un objeto JSON
    s3_client.put_object(Bucket=output_bucket, Key=output_key, Body=extracted_data)

    return {
        'statusCode': 200,
        'body': json.dumps('Factura procesada y guardada con éxito'),
        'facturaInfo': extracted_data
    }
