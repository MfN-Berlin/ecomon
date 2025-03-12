import os
import time
import numpy as np

import soundfile as sf
from pathlib import Path
from datetime import datetime, timedelta
from celery.utils.log import get_task_logger
from celery import states

from backend.worker.app import app
from backend.shared.models.db.models import Records, SiteReports, Sites


from backend.worker.settings import WorkerSettings
from backend.worker.services.job_service import JobService
from backend.worker.database import db_session
from backend.worker.tasks.base_task import BaseTask
from backend.shared.consts import task_topic
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import JSONB

logger = get_task_logger(__name__)
settings = WorkerSettings()

# Configure logger level from settings
logger.setLevel(settings.log_level)


@app.task(
    name=f"{task_topic.CREATE_SITE_DATA_REPORT.value}",
    bind=True,
    base=BaseTask,
    track_started=True,
)
def create_site_data_report_task(self, site_id: int):
    job_id = self.request.id
    session = db_session()

    try:
        JobService.set_job_running(session, job_id)
        session.commit()

        logger.info(f"Creating site data report for site {site_id}")
        # query first and last reocord
        (
            first_record_date,
            last_record_date,
            records_count,
            record_duration,
            corrupted_files_array,
        ) = calc_basic_report_data(site_id, session)

        duration_histogram = calc_duration_histogram(session)

        daily_histogram = calc_daily_historgram(
            session, first_record_date, last_record_date
        )

        monthly_histogram = calc_monthly_histogram(
            session, first_record_date, last_record_date
        )

        # Create expected record array using recording regime
        records_heatmap = calc_records_heatmap(
            site_id,
            session,
            first_record_date.replace(month=1, day=1),
            last_record_date.replace(month=12, day=31),
        )

        # Add the new instance to the session
        # Create a new SiteReports instance
        new_site_report = SiteReports(
            site_id=site_id,
            first_record_date=first_record_date,
            last_record_date=last_record_date,
            records_count=records_count,
            record_duration=record_duration,
            corrupted_files=corrupted_files_array,  # Store as array of JSON objects
            duration_histogram=duration_histogram,
            daily_histogram=daily_histogram,
            monthly_histogram=monthly_histogram,
            records_heatmap=records_heatmap,
        )
        session.add(new_site_report)
        session.commit()
    except Exception as e:
        session.rollback()
        JobService.set_job_error(session, job_id, str(e))
        raise e

    return {
        "status": "success",
        "message": f"Successfully created site data report for site {site_id}",
    }


def calc_monthly_histogram(session, first_record_date, last_record_date):
    # Get the earliest and latest record datetime from the records.
    first_record_date = first_record_date
    last_record_date = last_record_date

    # If there are no records, return empty data.
    if first_record_date is None or last_record_date is None:
        return {"dates": [], "counts": []}

    # Define the range to start at January of first_record_date.year
    # and end at December of last_record_date.year
    start_date = first_record_date.replace(month=1, day=1)
    end_date = last_record_date.replace(
        month=12, day=1
    )  # day is set as 1 for iteration

    # Generate a continuous list of month keys for the histogram in "MM/YYYY" format.
    month_keys = []
    current_year = start_date.year
    current_month = start_date.month
    while (current_year < end_date.year) or (
        current_year == end_date.year and current_month <= end_date.month
    ):
        month_key = f"{current_month:02d}/{current_year}"
        month_keys.append(month_key)

        # Move to the next month.
        if current_month == 12:
            current_month = 1
            current_year += 1
        else:
            current_month += 1

    # Obtain the aggregated record counts per month using the "MM/YYYY" format.
    aggregated = (
        session.query(
            func.to_char(Records.record_datetime, "MM/YYYY").label("date"),
            func.count().label("count"),
        )
        .group_by("date")
        .order_by("date")
        .all()
    )

    # Convert the query results to a dictionary for lookup.
    agg_dict = {row.date: int(row.count) for row in aggregated}

    # Build the histogram lists. If a month is missing in the query, assign a count of 0.
    dates = month_keys
    counts = [agg_dict.get(month, 0) for month in month_keys]

    return {"dates": dates, "counts": counts}


def calc_daily_historgram(session, first_record_date, last_record_date):
    # If there are no records, return empty data.
    if first_record_date is None or last_record_date is None:
        return {"dates": [], "counts": []}

    # Define the full range:
    # Start with January 1 of first_record's year and end with December 31 of last_record's year.
    start_date = first_record_date.replace(month=1, day=1)
    end_date = last_record_date.replace(month=12, day=31)

    # Generate a continuous list of day keys in "DD/MM/YYYY" format.
    day_keys = []
    current_date = start_date
    while current_date <= end_date:
        day_keys.append(current_date.strftime("%d/%m/%Y"))
        current_date += timedelta(days=1)

    # Obtain the aggregated record counts per day using the "DD/MM/YYYY" format.
    aggregated = (
        session.query(
            func.to_char(Records.record_datetime, "DD/MM/YYYY").label("date"),
            func.count().label("count"),
        )
        .filter(
            Records.record_datetime >= start_date, Records.record_datetime <= end_date
        )
        .group_by("date")
        .order_by("date")
        .all()
    )

    # Convert the query results to a dictionary for lookup.
    agg_dict = {row.date: int(row.count) for row in aggregated}

    # Build the histogram lists. If a day is missing in the aggregated query, assign a count of 0.
    dates = day_keys
    counts = [agg_dict.get(day, 0) for day in day_keys]

    return {"dates": dates, "counts": counts}


def calc_duration_histogram(session):
    """
    Calculates a histogram of duration grouped by year.

    Returns a list of dictionaries with the following structure:
    [
      {
        "year": <year>,
        "duration_range": [list of floor durations],
        "count": [corresponding counts]
      },
      ...
    ]
    """
    # Query aggregating by year and duration range.
    aggregated = (
        session.query(
            func.extract("year", Records.record_datetime).label("year"),
            func.floor(Records.duration).label("duration_range"),
            func.count().label("count"),
        )
        .group_by("year", func.floor(Records.duration))
        .order_by("year", func.floor(Records.duration))
        .all()
    )

    # Organize results by year.
    result = {}
    for row in aggregated:
        year_val = int(row.year)  # Convert year to an integer
        if year_val not in result:
            result[year_val] = {"year": year_val, "duration_range": [], "count": []}
        result[year_val]["duration_range"].append(int(row.duration_range))
        result[year_val]["count"].append(int(row.count))

    return list(result.values())


def calc_basic_report_data(site_id, session):
    first_record = (
        session.query(Records)
        .filter(Records.site_id == site_id)
        .order_by(Records.record_datetime.asc())
        .limit(1)
        .first()
    )
    last_record = (
        session.query(Records)
        .filter(Records.site_id == site_id)
        .order_by(Records.record_datetime.desc())
        .limit(1)
        .first()
    )
    records_count = session.query(Records).filter(Records.site_id == site_id).count()
    # get complete recrord duration
    record_duration = (
        session.query(func.sum(Records.duration))
        .filter(Records.site_id == site_id)
        .scalar()
    )
    corrupted_files = (
        session.query(
            func.jsonb_build_object("id", Records.id, "errors", Records.errors)
        )
        .filter(Records.site_id == site_id)
        .filter(Records.errors != None)
        .all()
    )

    corrupted_files_array = [file[0] for file in corrupted_files]

    return (
        first_record.record_datetime.date(),
        last_record.record_datetime.date(),
        records_count,
        record_duration,
        corrupted_files_array,
    )


def calc_records_heatmap(site_id, session, first_record_date, last_record_date):
    site = session.query(Sites).filter(Sites.id == site_id).first()
    cycle_duration = (
        site.record_regime_recording_duration + site.record_regime_pause_duration
    )

    records_per_day = 60 * 60 * 24 / cycle_duration
    recorded_days = (last_record_date - first_record_date).days + 1

    records_heatmap = None
    # if records_per_day is not an integer it is not possible to create an expected record array
    if records_per_day == records_per_day.to_integral_value():

        # Create a NumPy array with dimensions recorded_days * records_per_day, initialized with 0
        records_heatmap = np.full((recorded_days, int(records_per_day)), 0, dtype=int)

        # Define pagination parameters
        page_size = 1000
        offset = 0

        while True:
            # Fetch a batch of records for the site_id with record_datetime and errors
            records_batch = (
                session.query(Records.record_datetime, Records.errors)
                .filter(Records.site_id == site_id)
                .order_by(Records.id)
                .offset(offset)
                .limit(page_size)
                .all()
            )

            if not records_batch:
                break  # Exit the loop if no more records are fetched

            for record in records_batch:
                # Calculate the day index and the slot index
                day_index = (record.record_datetime.date() - first_record_date).days

                time_since_midnight = (
                    record.record_datetime
                    - datetime.combine(
                        record.record_datetime.date(), datetime.min.time()
                    )
                ).seconds
                slot_index = int(time_since_midnight // cycle_duration)

                # Set the corresponding slot to -1 if there's an error, otherwise +1
                if record.errors is not None:
                    records_heatmap[day_index, slot_index] = -1
                else:
                    records_heatmap[day_index, slot_index] = 1

            offset += page_size  # Move to the next batch

    return records_heatmap.tolist()
