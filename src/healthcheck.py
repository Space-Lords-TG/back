import datetime
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

# Добавляем эндпоинт для проверки здоровья
@app.get("/health")
async def health_check():
    return JSONResponse(
        content={
            "status": "healthy",
            "timestamp": datetime.datetime.now().isoformat(),
            "service": "space-lords-dev",
        },
        status_code=200
    )

# Функция для запуска FastAPI сервера
def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8002)