import logging
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from .config import APP_TITLE, DOCS_URL
from .routers.push import router as push_router
from .routers.client import router as client_router


logger = logging.getLogger(__name__)


app = FastAPI(
    title=APP_TITLE,
    docs_url=DOCS_URL,
    version="0.1.0",
)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home_page():
    return f"""
    <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>{APP_TITLE}</title>
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    font-family: Arial, sans-serif;
                }}
                .hero {{
                    background-color: #209cee;
                    color: #fff;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                }}
                .container {{
                    text-align: center;
                }}
                .title {{
                    font-size: 3rem;
                    margin-bottom: 1rem;
                }}
                .subtitle {{
                    font-size: 1.5rem;
                }}
                .subtitle a {{
                    color: #fff;
                    text-decoration: none;
                }}
            </style>
        </head>
        <body>
            <section class="hero">
                <div class="container">
                    <h1 class="title">
                        {APP_TITLE}
                    </h1>
                    <h2 class="subtitle">
                        <a href="{DOCS_URL}">Document</a>
                    </h2>
                </div>
            </section>
        </body>
    </html>
    """


app.include_router(push_router, prefix="/push")
app.include_router(client_router, prefix="/client")
