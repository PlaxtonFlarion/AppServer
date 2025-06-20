#    ____                       _       _
#   / ___|_ __ ___  _ __       | | ___ | |__
#  | |   | '__/ _ \| '_ \   _  | |/ _ \| '_ \
#  | |___| | | (_) | | | | | |_| | (_) | |_) |
#   \____|_|  \___/|_| |_|  \___/ \___/|_.__/
#

import httpx
import typing
from loguru import logger
from common import (
    utils, const
)

env = utils.current_env(
    const.CRON_JOB_URL, const.CRON_JOB_KEY
)

cron_job_url = env[const.CRON_JOB_URL]
cron_job_key = env[const.CRON_JOB_KEY]

HEADERS = {
    "Authorization": f"Bearer {cron_job_key}",
    "Content-Type": "application/json"
}


async def send(
        client: "httpx.AsyncClient", method: str, url: str, *args, **kwargs
) -> typing.Optional["httpx.Response"]:

    try:
        response = await client.request(method, url, *args, **kwargs)
        response.raise_for_status()
        return response

    except httpx.HTTPStatusError as e:
        logger.error(f"❌ {e.response.status_code} {e.response.text}")


async def update_keep_alive_jobs(client: "httpx.AsyncClient") -> typing.Coroutine | typing.Any:
    response = await send(client, "get", f"{cron_job_url}/jobs")

    for job in [job for job in response.json()["jobs"] if job["folderId"] == const.FOLDER_ID]:

        json = {
            "job": {
                "folderId": const.FOLDER_ID,
                'schedule': {
                    'timezone': utils.fake.timezone(),
                },
                "extendedData": {
                    "headers": {
                        "User-Agent": utils.fake.user_agent(),
                    }
                }
            }
        }
        resp = await send(
            client, "patch", f"{cron_job_url}/jobs/{(job_id := job['jobId'])}", json=json
        )
        logger.info(f"update {job_id} -> [{resp.status_code}]")

    return {"status": "cron jobs update"}


async def update_cron_jobs() -> typing.Coroutine | typing.Any:
    async with httpx.AsyncClient(headers=HEADERS, timeout=10) as client:
        return await update_keep_alive_jobs(client)


if __name__ == '__main__':
    pass
