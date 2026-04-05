import boto3
import json
import uuid

from config import (
    S3_BUCKET, SQS_QUEUE_NAME, AWS_REGION,
    CAR_CONFIDENCE_THRESHOLD, QUEUE_END
)

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

def get_list_of_images(s3_client):
    s3_response = s3_client.list_objects_v2(Bucket=S3_BUCKET)
    contents = s3_response["Contents"]
    
    images = []
    for image in contents:
        images.append(image["Key"])
        
    return images

def recognize_car(rekognition_client, image_key): 

    response = rekognition_client.detect_labels(Image={'S3Object':{'Bucket': S3_BUCKET,'Name': image_key}})

    for i in response['Labels']:
        if i['Name'] == 'Car' and i['Confidence'] >= CAR_CONFIDENCE_THRESHOLD:
            return True
        
    return False 
        
def main():
    print("Instance A - Starting car recognition pipeline...")
    
    sqs_client = boto3.client('sqs', region_name=AWS_REGION)
    s3_client = boto3.client("s3")
    rekognition_client = boto3.client('rekognition', region_name = AWS_REGION)
    
     
    queue_url = get_or_create_queue(sqs_client)
     
    images = get_list_of_images(s3_client)
    
    for image_key in images:
        if recognize_car(rekognition_client, image_key):
            message_body = json.dumps({
            'bucket': S3_BUCKET,
            'key': image_key})      
            
            sqs_client.send_message(
                QueueUrl=queue_url,
                MessageBody=message_body,
                MessageGroupId='pipeline',
                MessageDeduplicationId=str(uuid.uuid4())
    )                
            print(f"Car found - sent image {image_key.split('.')[0]} to queue named {SQS_QUEUE_NAME}")
            
        else:
            print(f"No car found in image {image_key.split('.')[0]}, skipping")
            
    sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=QUEUE_END,
        MessageGroupId='pipeline',
        MessageDeduplicationId=str(uuid.uuid4()))

    print("Instance A Car Recognition Complete.")
 
if __name__ == "__main__":
    main()                 