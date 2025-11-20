# Cache management script for records materialized views
# Used in dashboard heatmap generation
# Each cached table holds records for a specific site and year
#
#  Usage examples:
#
# Setup the database function (run once)
# python manage_records_cache.py setup
#
# Refresh cache for site 1, year 2024
# python manage_records_cache.py refresh 1 2024
#
# List all caches
# python manage_records_cache.py list
#
# Get statistics for a specific cache
# python manage_records_cache.py stats 1 2024
#
# Refresh all years for a site
# python manage_records_cache.py refresh-site 1 --start-year 2020 --end-year 2024
#
# Drop a specific cache
# python manage_records_cache.py drop 1 2024
#
# Drop all caches
# python manage_records_cache.py drop-all

import os
import sys
import argparse
import psycopg2
from psycopg2 import sql
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RecordsCacheManager:
    """Manage materialized views for caching records by site and year."""

    def __init__(self):
        """Initialize database connection from environment variables."""
        # Retrieve database connection details from environment variables
        db_username = os.getenv("DB_USERNAME")
        db_password = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME")

        # Validate required environment variables
        if not all([db_username, db_password, db_host, db_name]):
            raise ValueError(
                "Missing required environment variables. "
                "Please ensure DB_USERNAME, DB_PASSWORD, DB_HOST, and DB_NAME are set."
            )

        self.conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_username,
            password=db_password
        )
        self.conn.autocommit = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def create_refresh_function(self):
        """Create the PostgreSQL function to manage materialized views."""
        sql_function = """
        CREATE OR REPLACE FUNCTION refresh_records_cache(
            p_site_id INTEGER,
            p_year INTEGER
        ) RETURNS TEXT AS $$
        DECLARE
            view_name TEXT;
            start_date TEXT;
            end_date TEXT;
        BEGIN
            view_name := 'mv_records_site_' || p_site_id || '_year_' || p_year;
            start_date := p_year || '-01-01T00:00:00';
            end_date := (p_year + 1) || '-01-01T00:00:00';

            -- Drop existing view if it exists
            EXECUTE 'DROP MATERIALIZED VIEW IF EXISTS ' || view_name;

            -- Create materialized view
            EXECUTE format('
                CREATE MATERIALIZED VIEW %I AS
                SELECT id, record_datetime, site_id
                FROM records
                WHERE site_id = %L
                  AND record_datetime >= %L
                  AND record_datetime < %L
                ORDER BY record_datetime ASC
            ', view_name, p_site_id, start_date, end_date);

            -- Create index
            EXECUTE format('
                CREATE INDEX idx_%I_id ON %I(id)
            ', view_name, view_name);

            -- Create datetime index for faster queries
            EXECUTE format('
                CREATE INDEX idx_%I_datetime ON %I(record_datetime)
            ', view_name, view_name);

            RAISE NOTICE 'Created materialized view: %', view_name;

            RETURN view_name;
        END;
        $$ LANGUAGE plpgsql;
        """

        try:
            with self.conn.cursor() as cur:
                cur.execute(sql_function)
                self.conn.commit()
                logger.info("Successfully created refresh_records_cache function")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to create function: {e}")
            raise

    def refresh_cache(self, site_id, year):
        """Create or refresh a materialized view for a specific site and year."""
        view_name = f"mv_records_site_{site_id}_year_{year}"

        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT refresh_records_cache(%s, %s)", (site_id, year))
                result = cur.fetchone()[0]
                self.conn.commit()
                logger.info(f"Successfully refreshed cache: {result}")
                return result
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to refresh cache for site {site_id}, year {year}: {e}")
            raise

    def list_caches(self):
        """List all existing record cache materialized views."""
        query = """
        SELECT schemaname, matviewname,
               pg_size_pretty(pg_total_relation_size(schemaname||'.'||matviewname)) as size
        FROM pg_matviews
        WHERE matviewname LIKE 'mv_records_site_%'
        ORDER BY matviewname;
        """

        try:
            with self.conn.cursor() as cur:
                cur.execute(query)
                results = cur.fetchall()

                if not results:
                    logger.info("No record caches found")
                    return []

                logger.info(f"Found {len(results)} record caches:")
                for schema, name, size in results:
                    logger.info(f"  - {schema}.{name} ({size})")

                return results
        except Exception as e:
            logger.error(f"Failed to list caches: {e}")
            raise

    def drop_cache(self, site_id, year):
        """Drop a specific materialized view cache."""
        view_name = f"mv_records_site_{site_id}_year_{year}"

        try:
            with self.conn.cursor() as cur:
                cur.execute(sql.SQL("DROP MATERIALIZED VIEW IF EXISTS {}").format(
                    sql.Identifier(view_name)
                ))
                self.conn.commit()
                logger.info(f"Successfully dropped cache: {view_name}")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to drop cache {view_name}: {e}")
            raise

    def drop_all_caches(self):
        """Drop all record cache materialized views."""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT matviewname
                    FROM pg_matviews
                    WHERE matviewname LIKE 'mv_records_site_%'
                """)
                views = cur.fetchall()

                for (view_name,) in views:
                    cur.execute(sql.SQL("DROP MATERIALIZED VIEW IF EXISTS {}").format(
                        sql.Identifier(view_name)
                    ))
                    logger.info(f"Dropped cache: {view_name}")

                self.conn.commit()
                logger.info(f"Successfully dropped {len(views)} caches")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to drop all caches: {e}")
            raise

    def get_cache_stats(self, site_id, year):
        """Get statistics about a specific cache."""
        view_name = f"mv_records_site_{site_id}_year_{year}"

        query = """
        SELECT
            COUNT(*) as record_count,
            MIN(record_datetime) as earliest_record,
            MAX(record_datetime) as latest_record,
            pg_size_pretty(pg_total_relation_size(%s)) as size
        FROM {}
        """.format(sql.Identifier(view_name))

        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    sql.SQL(query).format(sql.Identifier(view_name)),
                    (view_name,)
                )
                result = cur.fetchone()

                if result:
                    stats = {
                        'view_name': view_name,
                        'record_count': result[0],
                        'earliest_record': result[1],
                        'latest_record': result[2],
                        'size': result[3]
                    }
                    logger.info(f"Cache stats for {view_name}:")
                    for key, value in stats.items():
                        logger.info(f"  {key}: {value}")
                    return stats
                else:
                    logger.warning(f"No data found for {view_name}")
                    return None
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            raise

    def refresh_all_for_site(self, site_id, start_year=None, end_year=None):
        """Refresh all caches for a site across a range of years."""
        if start_year is None:
            start_year = 2020  # Default start year
        if end_year is None:
            end_year = datetime.now().year

        logger.info(f"Refreshing caches for site {site_id}, years {start_year}-{end_year}")

        for year in range(start_year, end_year + 1):
            try:
                self.refresh_cache(site_id, year)
            except Exception as e:
                logger.error(f"Failed to refresh cache for site {site_id}, year {year}: {e}")
                continue


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description='Manage materialized view caches for records'
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Setup command
    subparsers.add_parser('setup', help='Create the refresh function in the database')

    # Refresh command
    refresh_parser = subparsers.add_parser('refresh', help='Refresh a cache')
    refresh_parser.add_argument('site_id', type=int, help='Site ID')
    refresh_parser.add_argument('year', type=int, help='Year')

    # List command
    subparsers.add_parser('list', help='List all caches')

    # Drop command
    drop_parser = subparsers.add_parser('drop', help='Drop a specific cache')
    drop_parser.add_argument('site_id', type=int, help='Site ID')
    drop_parser.add_argument('year', type=int, help='Year')

    # Drop all command
    subparsers.add_parser('drop-all', help='Drop all caches')

    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Get cache statistics')
    stats_parser.add_argument('site_id', type=int, help='Site ID')
    stats_parser.add_argument('year', type=int, help='Year')

    # Refresh site command
    refresh_site_parser = subparsers.add_parser('refresh-site', help='Refresh all caches for a site')
    refresh_site_parser.add_argument('site_id', type=int, help='Site ID')
    refresh_site_parser.add_argument('--start-year', type=int, help='Start year (default: 2020)')
    refresh_site_parser.add_argument('--end-year', type=int, help='End year (default: current year)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        with RecordsCacheManager() as manager:
            if args.command == 'setup':
                manager.create_refresh_function()

            elif args.command == 'refresh':
                manager.refresh_cache(args.site_id, args.year)

            elif args.command == 'list':
                manager.list_caches()

            elif args.command == 'drop':
                manager.drop_cache(args.site_id, args.year)

            elif args.command == 'drop-all':
                confirm = input("Are you sure you want to drop ALL caches? (yes/no): ")
                if confirm.lower() == 'yes':
                    manager.drop_all_caches()
                else:
                    logger.info("Operation cancelled")

            elif args.command == 'stats':
                manager.get_cache_stats(args.site_id, args.year)

            elif args.command == 'refresh-site':
                manager.refresh_all_for_site(
                    args.site_id,
                    args.start_year,
                    args.end_year
                )

        logger.info("Operation completed successfully")

    except Exception as e:
        logger.error(f"Operation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()