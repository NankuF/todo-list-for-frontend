import os
from dotenv import load_dotenv


load_dotenv()

SECRET_KEY= os.getenv("SECRET_KEY")
ALGORITHM= os.getenv("ALGORITHM")

PG_DATABASE_URL=os.getenv("PG_DATABASE_URL")