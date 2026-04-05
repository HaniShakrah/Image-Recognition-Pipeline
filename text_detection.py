import boto3
import json
from config import (
    S3_BUCKET, SQS_QUEUE_NAME, AWS_REGION,
    TEXT_CONFIDENCE_THRESHOLD, POLL_WAIT_SECONDS, VISIBILITY_TIMEOUT, QUEUE_END, OUTPUT_FILE
)

sqs_client = boto3.client('sqs', region_name=AWS_REGION)
s3_client = boto3.client("s3")
rekognition_client = boto3.client('rekognition', region_name = AWS_REGION)

def get_or_create_queue(sqs_client):
    
    try:
        queue_response = sqs_client.get_queue_url(QueueName=SQS_QUEUE_NAME)
        queue_url = queue_response["QueueUrl"]
        
        print(f"Using Queue '{SQS_QUEUE_NAME}'")
    
    except:
        queue_response = sqs_client.create_queue(
            QueueName=SQS_QUEUE_NAME,
            Attributes={
                'FifoQueue': 'true',
                'ContentBasedDeduplication': 'false'
            })
        
        queue_url = queue_response["QueueUrl"]
        print(f"Created Queue '{SQS_QUEUE_NAME}'")
    
    return queue_url

def pull_from_queue(sqs_client, queue_url):
    response = sqs_client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=POLL_WAIT_SECONDS,
            VisibilityTimeout=VISIBILITY_TIMEOUT,
        )

    messages = response.get("Messages", [])

    return messages
 
def detect_text(rekognition_client, image_key):

    response = rekognition_client.detect_text(
            Image={"S3Object": {"Bucket": S3_BUCKET, "Name": image_key}})
    texts = []
    if response['TextDetections']:
        for i in response['TextDetections']:
            if i['Type'] == 'LINE' and i['Confidence'] > TEXT_CONFIDENCE_THRESHOLD: 
                texts.append(i['DetectedText'])
                
        return texts

    return None
def write_output(image_key, text):
    with open(OUTPUT_FILE, "a") as f:
        f.write(f"Image {image_key.split('.')[0]}: {', '.join(text)}\n")
    
def main():
    
    sqs_client = boto3.client('sqs', region_name=AWS_REGION)
    rekognition_client = boto3.client('rekognition', region_name = AWS_REGION)

    queue_url = get_or_create_queue(sqs_client)
    
    while True:
        messages = pull_from_queue(sqs_client, queue_url)
        
        if messages[0]["Body"] == QUEUE_END:
            sqs_client.delete_message(QueueUrl=queue_url, ReceiptHandle=messages[0]['ReceiptHandle'])
            print(f"Reached end of queue")            
            break
        
        image_key = json.loads(messages[0]["Body"])['key']

        text = detect_text(rekognition_client, image_key)
        
        if text:
            write_output(image_key, text)
        
        print(f"Deleting image {image_key.split('.')[0]} from {SQS_QUEUE_NAME}")
        
        sqs_client.delete_message(QueueUrl=queue_url, ReceiptHandle=messages[0]['ReceiptHandle'])
    
if __name__ == "__main__":
    main()