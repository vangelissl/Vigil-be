import psycopg2
from psycopg2.extras import RealDictCursor
import json
import os
from datetime import datetime, UTC


class VideoDatabase:
    def __init__(self):
        self.conn_string = os.environ["DATABASE_URL"]

    def get_video_path(self, analysis_id: str) -> str | None:
        """Fetch video minio_path given analysis_id"""
        with psycopg2.connect(self.conn_string) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT v.minio_path
                    FROM analyses a
                    JOIN videos v ON a.video_id = v.id
                    WHERE a.id = %s
                """, (analysis_id,))
                result = cur.fetchone()
                return result["minio_path"] if result else None

    def write_result(self, analysis_id: str, status: str, result: dict | None):
        """Update analysis with result and status"""
        with psycopg2.connect(self.conn_string) as conn:
            with conn.cursor() as cur:
                # Serialize result to JSON if provided
                result_json = json.dumps(result) if result else None

                cur.execute("""
                    UPDATE analyses
                    SET status = %s, classification_result = %s, completed_at = %s
                    WHERE id = %s
                """, (status, result_json, datetime.now(UTC), analysis_id))
                conn.commit()
