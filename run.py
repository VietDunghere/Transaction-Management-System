import sys
import os

# Thêm backend/ vào sys.path để import app, main hoạt động đúng
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
# Đặt working directory về backend/ để .env và ml_models/ được resolve đúng
os.chdir(os.path.join(os.path.dirname(__file__), "backend"))

import uvicorn
from app.core.config import get_settings

settings = get_settings()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
    )
