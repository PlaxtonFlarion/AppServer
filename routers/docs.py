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
async def docs() -> "HTMLResponse":
    openapi_url = "/openapi.json"
    title       = "AppServerX API"
    logo        = "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8"/>
    <title>{title}</title>

    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css"/>
    <link href="https://cdn.jsdelivr.net/npm/jsoneditor@latest/dist/jsoneditor.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/jsoneditor@latest/dist/jsoneditor.min.js"></script>

    <style>
    /* theme */
    :root {{
      --bg:#0e0e0f; --fg:#f1f1f1; --panel:#171717; --border:#333; --code:#0e1117;
      --accent:#00e0ff; --ok:#28d07a; --err:#ff5566;
    }}
    .light {{
      --bg:#fafafa; --fg:#000; --panel:#fff; --border:#ddd; --code:#f6f8fa;
    }}
    body {{
      margin:0;display:flex;font-family:Inter,system-ui,sans-serif;
      background:var(--bg);color:var(--fg);
    }}

    /* Sidebar */
    .sidebar {{
      width:260px;background:var(--panel);height:100vh;position:fixed;
      border-right:1px solid var(--border);
      padding:22px;overflow-y:auto;
    }}
    .logo {{display:flex;align-items:center;gap:10px;font-size:18px;font-weight:700;margin-bottom:24px;}}
    input#search {{
      width:100%;padding:8px;border-radius:6px;margin-bottom:18px;
      background:var(--bg);color:var(--fg);border:1px solid var(--border);
    }}
    .section-title {{opacity:.6;font-size:12px;margin:14px 0 6px;font-weight:700}}
    .api-item {{
      cursor:pointer;font-size:14px;padding:6px;border-radius:6px;
    }}
    .api-item:hover {{background:rgba(255,255,255,.08)}}
    .method {{color:var(--accent);font-weight:700;font-size:11px;margin-right:4px;text-transform:uppercase}}

    /* Main */
    .content {{
      margin-left:260px;padding:40px 50px;
      width:calc(100vw - 260px);
    }}
    h2 {{margin-top:40px}}

    /* Schema Tree */
    .schema-box {{padding:10px;border-left:3px solid var(--accent);margin-bottom:16px;}}
    .schema-node {{margin:4px 0 4px 4px;}}
    .schema-node > summary {{
      cursor:pointer;font-size:13px;font-weight:600;list-style:none;
    }}
    .schema-node>summary::-webkit-details-marker{{display:none}}
    .schema-node>summary::before {{
      content:"▸";margin-right:4px;font-size:11px;display:inline-block;
      transition:.15s;
    }}
    .schema-node[open]>summary::before{{transform:rotate(90deg)}}
    .schema-leaf {{
      margin-left:18px;font-size:13px;padding:2px 0;
    }}
    .schema-type {{color:var(--accent);font-weight:bold;margin-left:6px;font-size:12px}}
    .schema-required {{color:var(--err);font-size:11px;margin-left:4px}}
    .schema-desc {{opacity:.7;margin-left:6px;font-size:12px}}

    /* JSON Editor */
    .json-box,.res-box {{
      height:240px;border:1px solid var(--border);border-radius:6px;margin-top:10px;
    }}

    .trybtn {{background:var(--accent);color:#000;padding:7px 13px;border-radius:6px;font-weight:700;
             cursor:pointer;display:inline-block;margin-top:10px}}
    .formatbtn {{background:#444;color:#fff;padding:6px 10px;border-radius:6px;margin-left:8px;cursor:pointer}}

    .btn-theme {{
      position:fixed;right:20px;top:20px;background:var(--panel);border:1px solid var(--border);
      padding:6px 12px;border-radius:6px;cursor:pointer;
    }}
    </style>
    </head>

    <body id="root">

    <div class="sidebar">
      <div class="logo"><img src="{logo}" height="26"/> {title}</div>
      <input id="search" placeholder="Search API..."/>
      <div id="menu"></div>
    </div>

    <div class="content">
      <h1>{title}</h1>
      <p style="opacity:.7;margin-top:-6px;">API Documentation • Schema • JSON Editor • Try API</p>
      <div id="api"></div>
    </div>

    <div id="theme" class="btn-theme">🌙 Dark</div>

    <script>
    const URL_OPENAPI="{openapi_url}";
    let spec=null,editors={{}};
    fetch(URL_OPENAPI).then(r=>r.json()).then(s=>{{spec=s;renderAPI();themeLoad();}});

    /* -------------------- Render API List -------------------- */
    function renderAPI(){{
      let groups={{}},paths=spec.paths;

      for(const [path,m] of Object.entries(paths))
      for(const [method,meta] of Object.entries(m))
        (groups[meta.tags?meta.tags[0]:"Others"] ??= []).push({{path,method,meta}});

      document.querySelector("#menu").innerHTML =
        Object.entries(groups).map(([tag,eps])=>`
          <div class='section-title'>${{tag}}</div>
          ${{eps.map(e=>`<div class="api-item" onclick="go('${{e.path}}')">
            <span class='method'>${{e.method}}</span> ${{e.path}}
          </div>`).join("")}}
        `).join("");

      document.querySelector("#api").innerHTML =
        Object.entries(groups).map(([tag,eps])=>`
          <h2>${{tag}}</h2>
          ${{eps.map(ep=>renderEndpoint(ep)).join("")}}
        `).join("");

      setTimeout(initEditors,200);
    }}

    /* -------------------- Endpoint Card -------------------- */
    function renderEndpoint(ep){{
      const req=ep.meta.requestBody?.content?.["application/json"]?.schema;
      const res=ep.meta.responses?.["200"]?.content?.["application/json"]?.schema;
      const id=btoa(ep.path+ep.method).replace(/=/g,"");

      return `
      <details>
        <summary>${{ep.method.toUpperCase()}} <b>${{ep.path}}</b></summary>
        <p style="opacity:.7;margin-top:6px">${{ep.meta.summary||"No description"}}</p>

        ${{req?`<b>📥 Request Schema</b><div class='schema-box'>${{schemaTree(req)}}</div>`:""}}
        ${{res?`<b>📤 Response Schema</b><div class='schema-box'>${{schemaTree(res)}}</div>`:""}}

        <b>📝 JSON Editor</b>
        <div id="editor-${{id}}" class="json-box"></div>
        <div class="formatbtn" onclick="formatJSON('${{id}}')">Format JSON</div>
        <div class="trybtn" onclick="send('${{ep.method}}','${{ep.path}}','${{id}}')">⚡ Try Request</div>

        <b style="display:block;margin-top:10px">📦 Response</b>
        <div id="resp-${{id}}" class="res-box"></div>
      </details>`;
    }}

    /* -------------------- Init Editor -------------------- */
    function initEditors(){{
      document.querySelectorAll("[id^='editor-']").forEach((box)=>{{
        const id=
    box.id.replace("editor-", "");
    editors[id] = new
    JSONEditor(box, {{mode: "code"}});
    editors[id].set({{"sample": "value"}});
    }});
    }}
    function formatJSON(id){{
      try{{editors[id].set(JSON.parse(editors[id].getText()));}}catch{{alert("JSON 格式错误")}}
    }}

    /* -------------------- Send Request -------------------- */
    async function send(method,path,id){{
      let body=null;
      try{{body=editors[id].get();}}catch{{}}
      let opt={{method:method.toUpperCase(),headers:{{"Content-Type":"application/json"}}}};
      if(body)opt.body=JSON.stringify(body);
      let r=await fetch(path,opt).catch(e=>({{error:e}}));
      try{{document.getElementById("resp-"+id).innerText=JSON.stringify(await r.json(),null,2)}}
      catch{{document.getElementById("resp-"+id).innerText=await r.text()}}
    }}

    /* -------------------- Schema Tree Renderer -------------------- */
    function schemaTree(s){{
      if(!s.properties)return"<i>No properties</i>";
      return Object.entries(s.properties).map(([k,f])=>{{
        const type=f.type||"object",desc=f.description||"",req=(s.required||[]).includes(k);
        return f.properties?`
          <details class='schema-node' open>
            <summary><b>${{k}}</b><span class='schema-type'>${{type}}</span>${{req?"<span class='schema-required'>required</span>":""}}${{desc?`<span class='schema-desc'>${{desc}}</span>`:""}}</summary>
            <div>${{schemaTree(f)}}</div>
          </details>
        `:`
          <div class='schema-leaf'>
            • <b>${{k}}</b><span class='schema-type'>${{type}}</span>${{req?"<span class='schema-required'>required</span>":""}}${{desc?`<span class='schema-desc'>${{desc}}</span>`:""}}
          </div>
        `;
      }}).join("");
    }}

    /* -------------------- Utilities -------------------- */
    function go(path){{document.querySelectorAll("details").forEach(d=>{{if(d.innerText.includes(path)){{d.open=true;d.scrollIntoView({{behavior:"smooth"}})}}}})}}
    function themeLoad(){{let m=localStorage.theme||"dark";apply(m);document.getElementById("theme").onclick=()=>{{apply(m=m=="dark"?"light":"dark")}};}}
    function apply(m){{document.body.classList.toggle("light",m=="light");
    document.getElementById("theme").innerText=m=="dark"?"🌙 Dark":"🌞 Light";localStorage.theme=m;}}

    document.querySelector("#search").oninput=function(){{
      let k=this.value.toLowerCase();
      document.querySelectorAll(".api-item").forEach(i=>i.style.display=i.innerText.toLowerCase().includes(k)?"":"none");
    }}
    </script>
    </body>
    </html>
    """

    return HTMLResponse(html)


if __name__ == '__main__':
    pass
