"""Main file for running the server."""
import uvicorn


if __name__ == '__main__':
    uvicorn.run('app.api:app', host='127.0.0.1', port=3000, reload=True,
                log_level='debug')
