from app.config.config import config
from app.config.config import MONGO_URI
import boto3
import os
from app.utils.logger import log_message
from botocore.exceptions import NoCredentialsError

from pymongo import MongoClient
import os

class MongoDB:
    def __init__(self):
        self.mongo_uri = os.getenv("MONGO_URI")  # Ensure .env is loaded properly
        if not self.mongo_uri:
            raise ValueError("MONGO_URI is not defined in the environment variables")
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client.get_database()  # Set default database

    def insert_document(self, collection_name, document):
        try:
            collection = self.db[collection_name]
            result = collection.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            raise Exception(f"Error inserting document into {collection_name}: {str(e)}")


def save_file_to_s3(file_path: str, file_extension: str) -> str:
    try:
        s3 = boto3.client('s3')
        bucket_name = config['BUCKET_NAME']  # Access bucket name from config

        # Set the destination file name on S3
        s3_file_name = f"audio/{os.path.basename(file_path)}"
        
        # Upload the file to S3
        s3.upload_file(file_path, bucket_name, s3_file_name)

        # Return the URL of the uploaded file
        file_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_file_name}"
        return file_url
    except NoCredentialsError:
        print("Credentials not available")
        return None
