import uuid
import boto3
import os
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from loguru import logger

logger.add("logs/app.log", rotation="1 MB", retention="10 days", level="DEBUG")
# Initialize logging
logger.info("Starting CV Uploader API")

# Load environment variables from .env file
load_dotenv()
app = FastAPI(
    title="CV Uploader API",
    description="API for uploading CVs and storing metadata in AWS services.",
    version="1.0.0",
    docs_url="/swagger",  # Swagger UI path
    redoc_url="/docs"  # ReDoc path
)

# AWS Config (read from environment variables)

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET")
DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE")

s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)
dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)
table = dynamodb.Table(DYNAMODB_TABLE)

MAX_FILE_SIZE_MB = 500


def get_file_size(file):
    file.file.seek(0, 2)  # move to end of file
    size = file.file.tell()
    file.file.seek(0)  # reset
    return size

@app.get("/cv/{applicant_id}")
async def get_cv(applicant_id: str):
    try:
        # Fetch metadata from DynamoDB
        response = table.get_item(Key={"applicant_id": applicant_id})
        if "Item" not in response:
            raise HTTPException(status_code=404, detail="Applicant not found")
        item = response["Item"]["cv_s3_key"]
        logger.info("Fetched CV s3 url for applicant_id: %s", applicant_id)
        # Return metadata
        return JSONResponse(content=item)
    except ClientError as e:
        logger.error(f"AWS error: {e}")
        raise HTTPException(status_code=500, detail=f"AWS error: {e.response['Error']['Message']}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/upload-cv/")
async def upload_cv(
    name: str = Form(...),
    email: str = Form(...),
    cover_letter: str = Form(...),
    cv_file: UploadFile = File(...)
):
    # Validate file size
    size = get_file_size(cv_file)
    if size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Max 500MB.")

    # Generate unique ID and file key
    applicant_id = str(uuid.uuid4())
    s3_key = f"cvs/{applicant_id}_{cv_file.filename}"

    try:
        # Upload file to S3
        s3.upload_fileobj(cv_file.file, S3_BUCKET, s3_key)
        s3_url = f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"

        # Save metadata to DynamoDB
        table.put_item(Item={
            "applicant_id": applicant_id,
            "name": name,
            "email": email,
            "cover_letter": cover_letter,
            "cv_s3_key": s3_url
        })
        logger.info("CV uploaded successfully for applicant_id: %s", applicant_id)
        # Return s3 url
        logger.info("CV URL: %s", s3_url)
        # Return response
        response = {
            "message": "CV uploaded successfully",
            "applicant_id": applicant_id,
            "cv_url": s3_url
        }
        logger.info("Response: %s", response)
        # Return JSON response
        return JSONResponse(content=response)
    except ClientError as e:
        logger.error(f"AWS error: {e}")
        raise HTTPException(status_code=500, detail=f"AWS error: {e.response['Error']['Message']}")

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
