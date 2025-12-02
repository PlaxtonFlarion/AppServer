#   ____                _ _     _       _
#  / ___|__ _ _ __   __| (_) __| | __ _| |_ ___
# | |   / _` | '_ \ / _` | |/ _` |/ _` | __/ _ \
# | |__| (_| | | | | (_| | | (_| | (_| | ||  __/
#  \____\__,_|_| |_|\__,_|_|\__,_|\__,_|\__\___|
#

import typing
from schemas import heal


def generate_candidates(
    old: "heal.Locator",
    elements: list["heal.ElementNode"]
) -> typing.Generator[dict, None, None]:

    for el in elements:
        if el.class_name != old["by"] and el.class_name != "android.widget.TextView":
            continue

        yield {
            "resource_id" : el.resource_id,
            "text"        : el.text,
            "bounds"      : el.bounds,
            "class_name"  : el.class_name
        }


if __name__ == '__main__':
    pass
