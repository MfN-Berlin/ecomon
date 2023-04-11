  lala = ("daily_summary_query",
    """
    SELECT
        YEAR(all_dates.date) AS year,
        MONTH(all_dates.date) AS month,
        DAY(all_dates.date) AS day,
        COALESCE(COUNT(DISTINCT BIRDNET_WALLBERGE_2019_records.id), 0) AS record_count,
        COALESCE(SUM(BIRDNET_WALLBERGE_2019_records.duration), 0) AS total_duration,
        COALESCE(COUNT(BIRDNET_WALLBERGE_2019_predictions.id), 0) AS prediction_count
    FROM (
        SELECT date(record_datetime) as date
        FROM BIRDNET_WALLBERGE_2019_records
        WHERE record_datetime >= '2019-01-01' AND record_datetime <= '2019-12-31'
        GROUP BY date(record_datetime)
    ) AS all_dates
    LEFT JOIN BIRDNET_WALLBERGE_2019_records ON date(BIRDNET_WALLBERGE_2019_records.record_datetime) = all_dates.date
    LEFT JOIN BIRDNET_WALLBERGE_2019_predictions ON BIRDNET_WALLBERGE_2019_records.id = BIRDNET_WALLBERGE_2019_predictions.record_id
    GROUP BY year, month, day
    ORDER BY year, month, day;
    """)


SELECT YEAR(BIRDNET_WALLBERGE_2019.record_datetime) AS year, MONTH(BIRDNET_WALLBERGE_2019.record_datetime), DAY(BIRDNET_WALLBERGE_2019.record_datetime) AS day, COUNT(DISTINCT BIRDNET_WALLBERGE_2019.id) AS record_count, SUM(BIRDNET_WALLBERGE_2019.duration) AS total_duration, COUNT(BIRDNET_WALLBERGE_2019_predictions.id) AS prediction_count
                FROM BIRDNET_WALLBERGE_2019
                LEFT JOIN BIRDNET_WALLBERGE_2019_predictions ON BIRDNET_WALLBERGE_2019.id = BIRDNET_WALLBERGE_2019_predictions.record_id
                GROUP BY YEAR(BIRDNET_WALLBERGE_2019.record_datetime), MONTH(BIRDNET_WALLBERGE_2019.record_datetime), DAY(BIRDNET_WALLBERGE_2019.record_datetime);
