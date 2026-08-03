import os

import uvicorn

from app.core.config import settings


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = settings.debug
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)
