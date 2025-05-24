from common import (
    const, utils
)
from services import signature


def stencil_plate(
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