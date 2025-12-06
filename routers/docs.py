#  ____
# |  _ \  ___   ___ ___
# | | | |/ _ \ / __/ __|
# | |_| | (_) | (__\__ \
# |____/ \___/ \___|___/
#

from fastapi import APIRouter
from fastapi.responses import (
    FileResponse, HTMLResponse
)

docs_router = APIRouter(tags=["Docs"])


@docs_router.get(path="/openapi.json", include_in_schema=False)
async def openapi_file() -> "FileResponse":
    return FileResponse(path="openapi.json", media_type="application/json")


@docs_router.get(path="/docs", include_in_schema=False)
async def swagger_docs() -> "HTMLResponse":
    title = "AppServerX API Console"

    loud_theme = "https://unpkg.com/swagger-ui-themes/themes/3.x/theme-material.css"
    dark_theme = "https://unpkg.com/swagger-ui-themes/themes/3.x/theme-monokai.css"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8"/>
        <title>{title}</title>

        <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css"/>

        <link id="swagger-theme" rel="stylesheet" href="{dark_theme}"/>

        <style>
            body {{ margin:0; font-family: 'Inter', ui-sans-serif; }}

            .topbar {{
                background:#111!important;
                padding:8px 16px;
                display:flex;justify-content:space-between;align-items:center;
            }}

            .brand {{ color:#eee; font-size:18px;font-weight:600; }}

            #theme-btn {{
                background:#222; color:#eee; padding:4px 10px; border-radius:6px;
                cursor:pointer; border:1px solid #444; font-size:13px; transition:.25s;
            }}

            #theme-btn:hover {{ background:#555; }}
        </style>
    </head>

    <body>

    <div class="topbar">
        <div class="brand">{title}</div>
        <div id="theme-btn">🌙 Dark</div>
    </div>

    <div id="swagger-ui"></div>

    <script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>

    <script>
        const themeBtn = document.getElementById("theme-btn");
        const theme = document.getElementById("swagger-theme");

        const DARK = "{dark_theme}";
        const LOUD = "{loud_theme}";

        function setTheme(mode) {{
            if(mode === "loud") {{
                theme.href = LOUD;
                themeBtn.textContent = "🌞 Loud";
                themeBtn.style.background = "#f0f0f0";
                themeBtn.style.color = "#333";
            }} else {{
                theme.href = DARK;
                themeBtn.textContent = "🌙 Dark";
                themeBtn.style.background = "#222";
                themeBtn.style.color = "#eee";
            }}
            localStorage.setItem("swagger-theme", mode);
        }}

        let saved = localStorage.getItem("swagger-theme") || "dark";
        setTheme(saved);

        themeBtn.onclick = ()=>{{
            saved = (saved === "dark" ? "loud" : "dark");
            setTheme(saved);
        }}

        // Swagger Init
        SwaggerUIBundle({{
            url: "/openapi.json",
            dom_id: '#swagger-ui',
            deepLinking: true,
            displayRequestDuration:true,
            tryItOutEnabled:true,
            persistAuthorization:true,
            docExpansion:"none"
        }});
    </script>
    </body>
    </html>
    """

    return HTMLResponse(html)


if __name__ == '__main__':
    pass
