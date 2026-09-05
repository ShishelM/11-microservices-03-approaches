import os
import io
from fastapi import FastAPI, Request, HTTPException
import boto3
from botocore.client import Config
import json

app = FastAPI()

# Читаем адрес MinIO из переменных окружения (внутри Docker-сети)
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
BUCKET_NAME = "images"

# Инициализируем полноценный S3 клиент для работы с MinIO
s3_client = boto3.client(
    's3',
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id='minioadmin',
    aws_secret_access_key='minioadmin',
    config=Config(signature_version='s3v4'),
    region_name='us-east-1'
)

import json

# Автоматическое создание бакета и настройка публичного доступа на чтение
try:
    s3_client.head_bucket(Bucket=BUCKET_NAME)
except Exception:
    s3_client.create_bucket(Bucket=BUCKET_NAME)
    
    # Создаем политику ReadOnly, чтобы Nginx мог забирать файлы из этого бакета
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicRead",
                "Effect": "Allow",
                "Principal": "*",
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{BUCKET_NAME}/*"]
            }
        ]
    }
    s3_client.put_bucket_policy(Bucket=BUCKET_NAME, Policy=json.dumps(bucket_policy))
    print(f"Bucket '{BUCKET_NAME}' created and policy set to ReadOnly successfully.")


@app.post("/v1/upload")
async def upload_file(request: Request):
    # Получаем бинарное содержимое картинки из curl
    body = await request.body()
    if not body:
        raise HTTPException(status_code=400, detail="Empty file data")
        
    # Генерируем имя файла. Для простоты теста назовем его 'yourfilename.jpg'.
    # В реальном проде имя можно брать из заголовков запроса.
    file_name = "yourfilename.jpg"
    
    try:
        # Загружаем бинарный поток напрямую в бакет MinIO
        s3_client.upload_fileobj(
            io.BytesIO(body),
            BUCKET_NAME,
            file_name,
            ExtraArgs={'ContentType': 'image/jpeg'}
        )
        return {
            "status": "success", 
            "message": f"File '{file_name}' successfully uploaded to MinIO bucket '{BUCKET_NAME}'"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MinIO upload error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
