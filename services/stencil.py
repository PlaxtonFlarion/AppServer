import json
from common import (
    const, utils
)
from services import signature


async def stencil_meta(
        x_app_id: str,
        x_app_token: str,
        a: str,
        t: int,
        n: str,
) -> dict:
    app_name, app_desc, *_ = a.lower().strip(), a, t, n

    signature.verify_signature(
        x_app_id, x_app_token, public_key=f"{app_name}_{const.BASE_PUBLIC_KEY}"
    )

    version_file = utils.resolve_template_ver()
    return json.loads(version_file.read_text())


async def stencil_viewer(
        x_app_id: str,
        x_app_token: str,
        a: str,
        t: int,
        n: str,
        page: str,
) -> str:
    app_name, app_desc, *_ = a.lower().strip(), a, t, n

    signature.verify_signature(
        x_app_id, x_app_token, public_key=f"{app_name}_{const.BASE_PUBLIC_KEY}"
    )

    html_template = utils.resolve_template(page)
    return html_template.read_text(encoding=const.CHARSET)


if __name__ == '__main__':
    pass
