import asyncio
import aiohttp
import csv
import io
import tld
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
from collections import Counter
from typing import Optional

app = FastAPI()

PHISHTANK_URL = "http://data.phishtank.com/data/online-valid.csv"
CSV_FILE = "verified_online.csv"
phish_data = []


class DownloadReportRequest(BaseModel):
    from_time: str
    to_time: Optional[str] = None


def iso_to_utc(iso_date: str, include_day: bool = False) -> datetime:
    dt = datetime.fromisoformat(iso_date)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)

    time_not_specified = ':' not in iso_date

    if include_day and time_not_specified:
        dt += timedelta(hours=23, minutes=59, seconds=59)

    return dt


def load_local_csv() -> list:
    try:
        with open(CSV_FILE, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            return list(reader)
    except IOError as e:
        print(f"Error reading local CSV file: {e}")
        return []


async def fetch_phishtank_data():
    global phish_data
    headers = {
        "User-Agent": "phishtank[zancato.t]"
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(PHISHTANK_URL) as response:
            if response.status == 200:
                content = await response.text()
                reader = csv.DictReader(io.StringIO(content))
                phish_data = list(reader)
            else:
                raise aiohttp.ClientError(
                    f"Failed to fetch data: HTTP {response.status}"
                )


async def update_phish_data():
    global phish_data

    try:
        await fetch_phishtank_data()
    except aiohttp.ClientError as e:
        print(e)
        print(f"Using {CSV_FILE} file instead")
        phish_data = load_local_csv()
    finally:
        print(f"Fetched {len(phish_data)} records from Phishtank")


async def scheduled_fetch():
    while True:
        await update_phish_data()
        await asyncio.sleep(3600)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(scheduled_fetch())


@app.get("/download_report", response_class=JSONResponse)
async def download_report(request: DownloadReportRequest):
    try:
        from_datetime = iso_to_utc(request.from_time)

        if from_datetime > datetime.now(timezone.utc):
            raise ValueError("from_time cannot be in the future.")

        if request.to_time:
            to_datetime = iso_to_utc(request.to_time, include_day=True)
        else:
            datetime.now(timezone.utc)

        if from_datetime > to_datetime:
            raise ValueError("from_time cannot be bigger than to_time.")

        tld_counter = Counter()
        urls = []

        for entry in phish_data:

            url = entry["url"]

            submission_time = datetime.fromisoformat(entry["submission_time"])
            if not from_datetime <= submission_time <= to_datetime:
                continue

            urls.append(url)

            try:
                parsed_tld = tld.get_tld(url)
            except tld.exceptions.TldDomainNotFound:
                continue

            tld_counter[parsed_tld] += 1

        return JSONResponse({
            "total_results": len(urls),
            "urls": urls,
            "tlds": tld_counter.most_common(),
        })

    except ValueError as e:
        raise HTTPException(
            status_code=400, detail=f"Invalid date format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


@app.get("/search_domain/{domain}", response_class=JSONResponse)
async def search_domain(domain: str):
    matching_entries = [
        entry['phish_detail_url'] for entry in phish_data
        if domain.lower() in entry['url'].lower()
    ]

    if not matching_entries:
        raise HTTPException(status_code=404, detail="Domain not found")

    return JSONResponse({"matching_urls": matching_entries})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
