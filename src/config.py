import uvicorn
import os
from dotenv import load_dotenv
load_dotenv()

log_config = uvicorn.config.LOGGING_CONFIG
log_config["formatters"]["access"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"
uvicorn_conf = dict(
    app='main:app',
    host=os.getenv('HOST'),
    port=int(os.getenv('PORT')),
    log_level='debug' if bool(os.getenv('DEBUG', False)) else 'info',
    log_config=log_config,
    reload=bool(os.getenv('DEBUG', False)),
)
