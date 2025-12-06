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


@docs_router.get(path="/custom-docs", include_in_schema=False)
async def custom_docs():

    openapi_url = "/openapi.json"
    logo = "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8"/>
    <title>AppServerX Developer Console</title>

    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css"/>
    <link id="theme-css" rel="stylesheet" href="https://unpkg.com/swagger-ui-themes/themes/3.x/theme-material.css"/>

    <style>

    /* ——— 全局结构 ——— */
    body {{
      margin:0; font-family:Inter, sans-serif;
      color:var(--fg); background:var(--bg);
      transition:.25s;
      display:flex;
    }}

    :root {{ --bg:#0e0e0f; --fg:#fff; --panel:#161616; --border:#333; }}
    .light{{ --bg:#fafafa; --fg:#000; --panel:#fff; --border:#ddd; }}

    .sidebar {{
      width:270px; background:var(--panel); height:100vh;
      border-right:1px solid var(--border);
      padding:20px; overflow-y:auto; position:fixed;
    }}

    .content {{
      margin-left:270px; width:calc(100vw - 270px);
      padding:20px 40px;
    }}

    /* ——— Landing Header ——— */
    .landing {{
      padding:60px 10px 40px;
      text-align:center;
      border-bottom:1px solid var(--border);
    }}

    .landing h1{{ font-size:32px; margin:0; font-weight:800; }}
    .landing p{{ opacity:.8; margin-top:10px; max-width:580px;margin:auto; }}

    .landing img{{height:48px;margin-bottom:14px;}}

    .btn-main {{
      padding:10px 18px; margin-top:22px; margin-right:8px;
      border-radius:8px; font-weight:600; cursor:pointer;
      background:#00b4d8; color:#fff; border:none;
    }}

    .btn-outline {{
      padding:10px 18px; margin-top:22px;
      border-radius:8px; font-weight:600; cursor:pointer;
      border:1px solid var(--border);
      background:var(--panel); color:var(--fg);
    }}

    .quickstart {{
      margin-top:40px; text-align:left; max-width:720px; margin:auto;
    }}

    pre {{
      background:#111; padding:14px; overflow-x:auto;
      border-radius:8px; color:#e0e0e0;
    }}

    .top-right {{
      position:fixed; right:20px; top:18px;
    }}
    .btn-theme {{ padding:6px 12px; border-radius:6px; cursor:pointer;
      background:var(--panel); border:1px solid var(--border);
    }}

    /* Sidebar */
    .section-title{{opacity:.6;font-size:12px;margin-top:18px;margin-bottom:6px;}}
    .api-item{{padding:6px;border-radius:6px;cursor:pointer;display:flex;gap:8px}}
    .api-item:hover{{background:rgba(255,255,255,.06)}}
    .method{{font-weight:700;color:#00e0ff;text-transform:uppercase;}}

    /* Hide default Swagger topbar */
    .swagger-ui .topbar {{display:none!important;}}

    </style>

    </head>
    <body id="root" class="dark">

    <div class="sidebar">
      <div class="logo" style="font-weight:700;font-size:19px;margin-bottom:22px;">
          <img src="{logo}"/> AppServerX
      </div>
      <input id="search" placeholder="Search API..."
          style="width:100%;padding:8px;border-radius:6px;margin-bottom:16px;
          background:var(--bg);color:var(--fg);border:1px solid var(--border);"/>

      <div id="menu"></div>
    </div>

    <!-- ███ Landing Page ███ -->
    <div class="content">

      <div class="landing">
         <img src="{logo}"/>
         <h1>AppServerX API Platform</h1>
         <p>Automation · Vector AI · Self-Healing · R2 Docs · Cloud Functions</p>

         <button onclick="jumpToAPI()" class="btn-main">📚 View API Reference</button>
         <button onclick="alert('Work In Progress')" class="btn-outline">🔑 Get API Key</button>

         <div class="quickstart">
             <h3>⭐ Quickstart</h3>

             <pre># cURL
    curl -X POST https://api.appserverx.com/healing \\
    -H "Authorization: Bearer <TOKEN>" \\
    -d '{{"ui":"button_login"}}'</pre>

             <pre># Python
    import requests
    r=requests.post("https://api.appserverx.com/healing",
      headers={{"Authorization":"Bearer TOKEN"}},
      json={{"ui":"button_login"}}
    )
    print(r.json())</pre>

             <pre>// Node.js
    await fetch("https://api.appserverx.com/healing",{{
      method:"POST",
      headers:{{Authorization:"Bearer TOKEN"}},
      body:JSON.stringify({{ui:"button_login"}})
    }})</pre>
         </div>
      </div>

      <div style="margin-top:40px" id="swagger-ui"></div>
    </div>

    <div class="top-right"><div id="theme-btn" class="btn-theme">🌙 Dark</div></div>


    <script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>

    <script>
    const ui=SwaggerUIBundle({{
       url:"{openapi_url}",
       dom_id:"#swagger-ui",
       tryItOutEnabled:true,
       persistAuthorization:true
    }})

    // Jump to API Reference
    function jumpToAPI(){{ document.getElementById('swagger-ui').scrollIntoView({{behavior:'smooth'}}) }}

    // Build Sidebar (with tags grouping)
    setTimeout(function build(){{
       let spec = ui.getSystem().specSelectors.specJson().toJS()
       if(!spec.paths) return setTimeout(build,500)

       let groups={{}}
       for(let p in spec.paths)
         for(let m in spec.paths[p]){{
            let t = spec.paths[p][m].tags?.[0] || "Others"
            ;(groups[t]=groups[t]||[]).push({{path:p,method:m}})
         }}

       let html=""
       for(let t in groups){{
          html+=`<div class='section-title'>${{t}}</div>`
          groups[t].forEach(ep=>{{
            html+=`<div class='api-item' onclick="jumpPath('${{ep.path}}')">
                     <span class='method'>${{ep.method}}</span> ${{ep.path}}
                   </div>`
          }})
       }}
       document.querySelector("#menu").innerHTML=html
    }},500)

    function jumpPath(path){{
      const el=document.querySelector(`[data-path="${{path}}"]`);
      el?.scrollIntoView({{behavior:"smooth"}});
    }}

    // Search filter
    document.getElementById("search").oninput=e=>{{
      const key=e.target.value.toLowerCase()
      document.querySelectorAll(".api-item").forEach(i=>{{
        i.style.display=i.innerText.toLowerCase().includes(key)?"":"none"
      }})
    }}

    // Theme toggle
    let mode=localStorage.getItem("mode")||"dark"
    applyTheme()
    document.getElementById("theme-btn").onclick=()=>{{
        mode=mode==="dark"?"light":"dark";applyTheme()
    }}
    function applyTheme(){{
      document.getElementById("root").classList.toggle("light",mode==="light")
      document.getElementById("theme-btn").innerText=mode==="dark"?"🌙 Dark":"🌞 Light"
      localStorage.setItem("mode",mode)
    }}

    </script>
    </body>
    </html>
    """

    return HTMLResponse(html)


if __name__ == '__main__':
    pass
