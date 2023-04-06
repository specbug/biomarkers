import os

import gunicorn.app.base
from dotenv import load_dotenv
from fastapi import FastAPI

from controllers import strugglebus, fit
from utils import number_of_workers

app = FastAPI()

# Configure endpoints
app.include_router(strugglebus.router, prefix='/api/struggle-bus', tags=['control'])
app.include_router(fit.router, prefix='/api/markers', tags=['yield'])


class StandaloneApplication(gunicorn.app.base.BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def init(self, parser, opts, args):
        pass

    def load_config(self):
        config = {key: value for key, value in self.options.items() if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


if __name__ == '__main__':
    load_dotenv('config.env')
    HOST = os.getenv('HOST')
    PORT = int(os.getenv('PORT'))
    options = {
        'bind': f'{HOST}:{PORT}',
        'workers': number_of_workers(),
        'worker_class': 'uvicorn.workers.UvicornWorker',
    }
    StandaloneApplication(app, options).run()
    # uvicorn.run(app, host=HOST, port=PORT)
