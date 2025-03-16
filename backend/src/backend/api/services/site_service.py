from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.shared.models.db.models import SiteDirectories


class SiteService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def are_all_directories_part_of_site(
        self, site_id: int, directories: list[str]
    ) -> bool:
        """
        Check if all directories in the list are part of the site directories

        Args:
            site_id: The ID of the site
            directories: A list of directory paths to check

        Returns:
            bool: True if all directories are part of the site, False otherwise
        """
        print(f"Checking if all directories {directories} are part of site {site_id}")
        async with self.db.begin():
            for directory in directories:
                result = await self.db.execute(
                    select(SiteDirectories).filter(
                        SiteDirectories.site_id == site_id,
                        SiteDirectories.directory == directory,
                    )
                )
                if result.scalar_one_or_none() is None:
                    return False
            return True

    async def get_directories_for_site(self, site_id: int) -> list[str]:
        async with self.db.begin():
            result = await self.db.execute(
                select(SiteDirectories).filter(SiteDirectories.site_id == site_id)
            )
            return [row.directory for row in result.scalars()]
