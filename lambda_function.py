import boto3
import json
import urllib.parse
import os

# Define las variables de entorno
output_bucket = os.environ['OUTPUT_BUCKET']
output_key = os.environ['OUTPUT_KEY']

def lambda_handler(event, context):
    # Inicializa los clientes para S3 y Textract
    s3_client = boto3.client('s3', region_name='eu-west-1')
    textract_client = boto3.client('textract')

    # Obtén el nombre del bucket y la clave del archivo subido del evento de S3
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    document_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    # Llama a Textract para procesar el documento con AnalyzeExpense
    analyze_expense_response = textract_client.analyze_expense(
        Document={'S3Object': {'Bucket': bucket_name, 'Name': document_key}}
    )

    # Extrae y estructura los datos relevantes del resultado
    structured_data = extract_data_from_response(analyze_expense_response)

    # Convierte la información de la factura a JSON
    factura_json = json.dumps(structured_data)

    # Guarda la información de la factura en S3 como un objeto JSON
    s3_client.put_object(Bucket=output_bucket, Key=output_key, Body=factura_json)

    return {
        'statusCode': 200,
        'body': json.dumps('Factura procesada y guardada con éxito'),
        'facturaInfo': structured_data
    }

def extract_data_from_response(response):
    # Estructura para almacenar los datos de la factura
    factura_info = {
        'fecha': '',
        'direccion': '',
        'importe': '',
        'numero_factura': ''
    }

    # Procesa la respuesta para extraer los datos relevantes
    for expense_doc in response.get('ExpenseDocuments', []):
        for field in expense_doc.get('SummaryFields', []):
            field_type = field.get('Type', {}).get('Text')
            field_value = field.get('ValueDetection', {}).get('Text')

            if field_type in ['INVOICE_RECEIPT_DATE']:
                factura_info['fecha'] = field_value
            elif field_type in ['ADDRESS', 'VENDOR_ADDRESS', 'RECEIVER_ADDRESS']:
                factura_info['direccion'] = field_value
            elif field_type in ['TOTAL', 'AMOUNT_DUE']:
                factura_info['importe'] = field_value
            elif field_type in ['INVOICE_RECEIPT_ID']:
                factura_info['numero_factura'] = field_value

    return factura_info
