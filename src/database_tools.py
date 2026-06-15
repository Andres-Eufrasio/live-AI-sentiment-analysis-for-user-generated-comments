import psycopg2
import os
from uuid import UUID


class DatabaseCon():
    #Use docker variables
    def __init__(self):
        self.user = os.environ.get("POSTGRES_USER")
        self.password = os.environ.get("POSTGRES_PASSWORD")
        self.database = os.environ.get("POSTGRES_DB")

        if not self.user or not self.password or not self.database:
            raise ValueError("Missing required PostgreSQL environment variables")
    

    def __enter__(self):
        self.conn = psycopg2.connect(
            database=self.database,
            user=self.user,
            password=self.password,
            host='db',
            port='5432'
        )
        return self.conn
    
    # Auto close the connection
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            if exc_type is not None:
                self.conn.rollback() 
            else:
                self.conn.commit()

            self.conn.close()


class DatabaseTools:
    def __init__(self, conn):
        self.conn = conn

    def get_unreviewed_flags(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT * FROM unreviewed_flags;")
            return cur.fetchall()
        
    def create_comment(
        self,
        content: str,
        post_id: UUID,
        author_id: UUID | None = None,
        parent_comment_id: UUID | None = None,
        context: str | None = None,
    ):
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO comment (
                        content,
                        author_id,
                        post_id,
                        parent_comment_id,
                        context
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id, posted_time;
                    """,
                    (content, author_id, post_id, parent_comment_id, context),
                )

                result = cur.fetchone()
                self.conn.commit()
                return {"id": result[0], "posted_time": result[1]}

        except Exception:
            self.conn.rollback()
            raise
        


