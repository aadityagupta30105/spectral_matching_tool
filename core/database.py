import spectral
from core.config import DB_PATH


class SpectralDatabase:

    def __init__(self, db_path):
        self.db = spectral.USGSDatabase(str(db_path))

    def get_all_minerals(self):
        sql = """
        SELECT LibName, SampleID, Description
        FROM Samples
        WHERE Chapter LIKE '%ChapterM_Minerals%'
        """
        return list(self.db.query(sql))

    def search(self, keyword):
        sql = """
        SELECT LibName, SampleID, Description
        FROM Samples
        WHERE Description LIKE ?
        """
        return list(self.db.query(sql, (f"%{keyword}%",)))
