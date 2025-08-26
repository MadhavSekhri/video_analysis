import os
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import openai

# Load environment variables from .env file
load_dotenv()

# Access the MONGO_URI environment variable
MONGO_URI = os.getenv('MONGO_URI')

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['Mentei']
config_collection = db['configuration']

# Fetch configuration from MongoDB
config = config_collection.find_one()

if not config:
    raise ValueError("Configuration not found in the database")

# Retrieve API keys and configuration data from DB
WHISPER_API_KEY = config['services']['whisper']['api_key']
openai.api_key=config['services']['whisper']['api_key']
models = openai.Model.list()
print(models)

PERSPECTIVE_API_KEY = config['services']['perspective_api']['api_key']
AWS_ACCESS_KEY = config['services']['aws_rekognition']['access_key']
AWS_SECRET_KEY = config['services']['aws_rekognition']['secret_key']
AWS_REGION = config['services']['aws_rekognition']['region']
BUCKET_NAME = config['services']['aws_rekognition']['bucket_name']
# OPENAI_API_KEY = config['services']['openai']['api_key']


