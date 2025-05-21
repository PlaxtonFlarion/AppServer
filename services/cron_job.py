import os
import httpx
import typing
from faker import Faker
from pathlib import Path
from dotenv import load_dotenv
from common import const

fake = Faker()

if (env_path := Path(__file__).resolve().parents[1] / ".env").exists():
    load_dotenv(env_path)
    cron_job_url = os.getenv(const.CRON_JOB_URL)
    cron_job_key = os.getenv(const.CRON_JOB_KEY)
else:
    cron_job_url = Path("/etc/secrets", const.CRON_JOB_URL).read_text().strip()
    cron_job_key = Path("/etc/secrets", const.CRON_JOB_KEY).read_text().strip()

# 校验是否正确加载
if not cron_job_url or not cron_job_key:
    raise EnvironmentError("环境变量未正确加载，请检查 .env 或 Render 配置。")

HEADERS = {
    "Authorization": f"Bearer {cron_job_key}", "Content-Type": "application/json"
}

fake.user_agent()


async def send(
        client: "httpx.AsyncClient", method: str, url: str, *args, **kwargs
) -> typing.Union["httpx.Response", None]:

    try:
        return await client.request(method, url, *args, **kwargs)
    except Exception as e:
        print(f"❌ 请求失败: {e}")


async def update_keep_alive_jobs(client: "httpx.AsyncClient"):
    response = await send(client, "get", f"{cron_job_url}/jobs")

    for job in [job for job in response.json()["jobs"] if job["folderId"] == 47245]:

        json = {
            "job": {
                "folderId": 47245,
                'schedule': {
                    'timezone': fake.timezone(),
                },
                "extendedData": {
                    "headers": {
                        "User-Agent": fake.user_agent(),
                    }
                }
            }
        }
        resp = await send(
            client, "patch", f"{cron_job_url}/jobs/{(job_id := job['jobId'])}", json=json
        )
        print(f"update {job_id} -> [{resp.status_code}]")


async def update_cron_jobs():
    async with httpx.AsyncClient(headers=HEADERS, timeout=10) as client:
        await update_keep_alive_jobs(client)


if __name__ == '__main__':
    pass
