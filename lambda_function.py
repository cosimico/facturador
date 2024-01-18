import boto3
import json
import urllib
import os

output_bucket = os.environ['OUTPUT_BUCKET']
output_key = os.environ['OUTPUT_KEY']

def lambda_handler(event, context):
    s3_client = boto3.client('s3', region_name='eu-west-1')

    # Obtén el nombre del bucket y la llave del archivo subido del evento de S3
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    document_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    # Llama a Textract para procesar el documento

    response = textract_client.detect_document_text(
        Document={'S3Object': {'Bucket': bucket_name, 'Name': document_key}}
    )

    # Extrae el texto del documento
    extracted_text = " ".join([item["Text"] for item in response["Blocks"] if item["BlockType"] == "LINE"])


    # Guarda la respuesta en S3
    s3_client.put_object(Bucket=output_bucket, Key=output_key, Body=extracted_text)

    return {
        'statusCode': 200,
        'body': json.dumps('Texto extraído con éxito'),
        'extractedText': extracted_text
    }
