import os
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

DATA_ROOT = os.getenv("DATA_ROOT", "data/")
FLASK_ENV = os.getenv("FLASK_ENV", "development")