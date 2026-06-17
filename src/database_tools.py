import psycopg2
from psycopg2 import pool
import psycopg2.extras
import os
from datetime import datetime
from uuid import UUID

psycopg2.extras.register_uuid()

"""
Pooled database connection
"""
class DatabaseCon:
    _pool = None

    @classmethod
    def init_pool(cls):
        #Uses docker enviroment info
        user = os.environ.get("POSTGRES_USER")
        password = os.environ.get("POSTGRES_PASSWORD")
        database = os.environ.get("POSTGRES_DB")

        if not user or not password or not database:
            raise ValueError("Missing required PostgreSQL environment variables")

        cls._pool = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=5,
            database=database,
            user=user,
            password=password,
            host='db',
            port='5432'
        )

    @classmethod
    def get_conn(cls):
        if cls._pool is None:
            cls.init_pool()
        return cls._pool.getconn()

    @classmethod
    def put_conn(cls, conn):
        cls._pool.putconn(conn)

    @classmethod
    def close_pool(cls):
        cls._pool.closeall()

    # use as --- DatabaseCon() as conn
    def __enter__(self):
        self._conn = self.get_conn()
        return self._conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.put_conn(self._conn)
        return False


class DatabaseTools:
    def __init__(self, conn):
        self.conn = conn
    """
    Gets
    """
    def get_unreviewed_flags(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT * FROM unreviewed_flags;")
            return cur.fetchall()

    def get_active_model(self):
        with self.conn.cursor() as cur:
            #Returns either 1 or 0 indexes
            cur.execute("SELECT name FROM model WHERE active = TRUE;")
            result = cur.fetchall()
        if result is None:
            return ""
        else:
            return result[0]
    

    """
    Inserts
    """
    def create_comment(
        self,
        content: str,
        post_id: UUID,
        author_id: UUID | None = None,
        parent_comment_id: UUID | None = None,
    ):
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO comment (
                        content,
                        author_id,
                        post_id,
                        parent_comment_id
                    )
                    VALUES (%s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (content, author_id, post_id, parent_comment_id),
                )

                result = cur.fetchone()
                self.conn.commit()
                return {"id": result[0]}

        except Exception:
            self.conn.rollback()
            raise

    def create_user(
        self,
        id: str,
        username: str,
        created_at: datetime | None = None,
        banned: bool = False
    ): 
        try:
            with self.conn.cursor() as cur:
                if created_at:
                    cur.execute(
                        """
                        INSERT INTO "user" (
                            id,
                            username,
                            created_at,
                            banned
                        )
                        VALUES (%s, %s, %s, %s)
                        RETURNING id;
                        """,
                        (id, username, created_at, banned),
                    )
                    result = cur.fetchone()
                    self.conn.commit()
                    return {"id": result[0]}
                else:
                    cur.execute(
                        """
                        INSERT INTO "user" (
                            id,
                            username,
                            banned
                        )
                        VALUES (%s, %s, %s)
                        RETURNING id;
                        """,
                        (id, username, banned),
                    )
                    result = cur.fetchone()
                    self.conn.commit()
                    return {"id": result[0]}

        except Exception:
            self.conn.rollback()
            raise

    def create_post(
        self,
        content: str,
        author_id: str,
        posted_time: datetime | None = None,
        id: UUID | None = None
    ): 
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO comment (
                        id,
                        content,
                        author_id,
                        posted_time
                    )
                    VALUES (%s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (id, content, author_id, posted_time),
                )
                result = cur.fetchone()
                self.conn.commit()
                return {"id": result[0]}

        except Exception:
            self.conn.rollback()
            raise

    def create_model(
        self,
        name: str,
        labels: list[str],
        active: bool | None = False
    ):
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO model (
                        name,
                        labels,
                        active,
                    )
                    VALUES (%s, %s, %s)
                    RETURNING name;
                    """,
                    (name, labels, active),
                )
                result = cur.fetchone()
                self.conn.commit()
                return {"name": result[0]}
            
        except Exception:
            self.conn.rollback()
            raise  

    def create_flag(
        self,
        comment_id: list[str],
        user_report_id: UUID | None = None
    ):
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO flag (
                        comment_id,
                        user_report_id,
                    )
                    VALUES (%s, %s)
                    RETURNING id;
                    """,
                    (comment_id, user_report_id),
                )
                result = cur.fetchone()
                self.conn.commit()
                return {"id": result[0]}
            
        except Exception:
            self.conn.rollback()
            raise  

    def create_prediction(
        self,
        model_id: str,
        confidence: list[float],
        flag_id : UUID | None = None,
    ):
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO model (
                        flag_id,
                        model_id,
                        confidence,
                    )
                    VALUES (%s, %s, %s)
                    RETURNING name;
                    """,
                    (flag_id, model_id, confidence),
                )
                result = cur.fetchone()
                self.conn.commit()
                return {"name": result[0]}
            
        except Exception:
            self.conn.rollback()
            raise  


    def create_moderation_decision(
        self,
        comment_id: UUID,
        moderator_id: UUID,
        flag_id: UUID,
        decision: bool,
        prediction_id: UUID | None = None,
    ):
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO moderation_decision (
                        comment_id,
                        moderator_id,
                        flag_id,
                        prediction_id,
                        decision
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (comment_id, moderator_id, flag_id, prediction_id, decision),
                )
                result = cur.fetchone()
                self.conn.commit()
                return {"id": result[0]}

        except Exception:
            self.conn.rollback()
            raise


        
    
        



