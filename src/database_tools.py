import psycopg2
from psycopg2 import pool
import psycopg2.extras
import os
from datetime import datetime
from uuid import UUID


psycopg2.extras.register_uuid()
"""
Notes add some comments on the tooling
add runtime errors to raise
"""

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

    # use as --- DatabaseCon() as connection to pool
    def __enter__(self):
        self._conn = self.get_conn()
        return self._conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.put_conn(self._conn)
        return False


def tuples_to_dict(rows, columns, key: str):
    return {
        row[columns.index(key)]: dict(zip(columns, row))
        for row in rows
    }

class DatabaseTools:
    def __init__(self, conn):
        self.conn = conn
    """
    Gets
    """
    def get_unreviewed_flags(self) -> dict:
        with self.conn.cursor() as cur:
            cur.execute("SELECT * FROM unreviewed_flags;")
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            return tuples_to_dict(rows, columns, "id")
        
        

    def get_active_model(self) -> str:
        with self.conn.cursor() as cur:
            #Returns either 1 or 0 indexes
            cur.execute("SELECT name FROM model WHERE active = TRUE;")
            result = cur.fetchone()
        if result is None:
            return ""
        else:
            return result[0]
    
    def get_active_model_labels(self) -> list:
        with self.conn.cursor() as cur:
            #Returns either 1 or 0 indexes
            cur.execute("SELECT labels FROM model WHERE active = TRUE;")
            result = cur.fetchall()
        if not result:
            return []
        else:
            return result[0][0]
    

    """
    Inserts/creations
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

        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"Failed to create comment: {e}")  

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

        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"Failed to create user: {e}")  

    def create_post(
        self,
        id: str,
        content: str,
        author_id: str,
        posted_time: datetime | None = None,
        
    ): 
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO post (
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

        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"Failed to create post: {e}")  

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
            
        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"Failed to create model: {e}")  

    def create_flag(
        self,
        comment_id: list[str],
        user_report_id: UUID | None = None,
        active: bool | None = True
    ):
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO flag (
                        comment_id,
                        user_report_id,
                        active
                    )
                    VALUES (%s, %s, %s)
                    RETURNING id;
                    """,
                    (comment_id, user_report_id, active),
                )
                result = cur.fetchone()
                self.conn.commit()
                return {"id": result[0]}
            
        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"Failed to create flag: {e}")  

    def create_prediction(
        self,
        model_id: str,
        confidence: list[float],
        flag_id: UUID | None = None,
    ):
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO prediction (
                        flag_id,
                        model_id,
                        confidence
                    )
                    VALUES (%s, %s, %s)
                    RETURNING id;
                    """,
                    (flag_id, model_id, confidence),
                )

                result = cur.fetchone()
                self.conn.commit()

                return {"id": result[0]}

        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(
                f"Failed to create prediction: {e}"
            ) from e

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

        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"Failed to create moderation decision: {e}")
        
    def deactivate_flag(
        self,
        flag_id: UUID,
    ):
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE flag
                    SET active = FALSE
                    WHERE id = %s
                    RETURNING id, active;
                    """,
                    (flag_id,),
                )

                result = cur.fetchone()
                self.conn.commit()

                if result is None:
                    return {"updated": False, "message": "Flag not found"}

                return {
                    "updated": True,
                    "id": result[0],
                    "active": result[1],
                }

        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"Failed to deactivate flag: {e}")

    def get_flagged_users(self):
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 
                        u.id,
                        u.username,
                        u.banned,
                        COUNT(f.id) AS flag_count
                    FROM "user" u
                    JOIN flag f ON f.user_id = u.id
                    GROUP BY u.id, u.username, u.banned
                    ORDER BY flag_count DESC;
                    """
                )

                rows = cur.fetchall()

                return [
                    {
                        "user_id": r[0],
                        "username": r[1],
                        "banned": r[2],
                        "flag_count": r[3],
                    }
                    for r in rows
                ]

        except Exception as e:
            raise RuntimeError(f"Failed to fetch flagged users: {e}")
        
        



    def get_audit_log(self):
        """
        Returns the complete audit history as separate events.

        Event types:
        - comment: Comment/flag/prediction activity
        - moderation: Moderator decision
        """

        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT *
                    FROM (
                        -- ==========================================
                        -- COMMENT / FLAG / PREDICTION EVENT
                        -- ==========================================
                        SELECT
                            'comment' AS event_type,

                            f.id AS flag_id,
                            f.comment_id,

                            c.content AS comment_content,
                            c.posted_time AS comment_timestamp,

                            author.username AS author_username,

                            p.id AS prediction_id,
                            p.model_id AS model_name,
                            p.confidence AS prediction_scores,

                            NULL::UUID AS moderation_decision_id,
                            NULL::BOOLEAN AS decision,
                            NULL::TIMESTAMPTZ AS moderation_timestamp,

                            NULL::UUID AS moderator_id,
                            NULL::TEXT AS moderator_username

                        FROM flag f

                        JOIN comment c
                            ON c.id = f.comment_id

                        LEFT JOIN "user" author
                            ON author.id = c.author_id

                        LEFT JOIN prediction p
                            ON p.flag_id = f.id


                        UNION ALL


                        -- ==========================================
                        -- MODERATOR DECISION EVENT
                        -- ==========================================
                        SELECT
                            'moderation' AS event_type,

                            f.id AS flag_id,
                            f.comment_id,

                            c.content AS comment_content,
                            c.posted_time AS comment_timestamp,

                            author.username AS author_username,

                            p.id AS prediction_id,
                            p.model_id AS model_name,
                            p.confidence AS prediction_scores,

                            md.id AS moderation_decision_id,
                            md.decision AS decision,
                            md.time_stamp AS moderation_timestamp,

                            m.id AS moderator_id,
                            m.username AS moderator_username

                        FROM moderation_decision md

                        JOIN flag f
                            ON f.id = md.flag_id

                        JOIN comment c
                            ON c.id = f.comment_id

                        LEFT JOIN "user" author
                            ON author.id = c.author_id

                        LEFT JOIN prediction p
                            ON p.flag_id = f.id

                        LEFT JOIN moderator m
                            ON m.id = md.moderator_id
                    ) AS audit_events

                    ORDER BY
                        COALESCE(
                            moderation_timestamp,
                            comment_timestamp
                        ) DESC;
                    """
                )

                rows = cur.fetchall()

                return [
                    {
                        "type": row[0],

                        "flag_id": row[1],
                        "comment_id": row[2],

                        "comment_content": row[3],
                        "comment_timestamp": row[4],

                        "author_username": row[5],

                        "prediction_id": row[6],
                        "model_name": row[7],
                        "prediction_scores": row[8],

                        "moderation_decision_id": row[9],
                        "decision": row[10],
                        "moderation_timestamp": row[11],

                        "moderator_id": row[12],
                        "moderator_username": row[13],
                    }
                    for row in rows
                ]

        except Exception as e:
            raise RuntimeError(
                f"Failed to fetch audit log: {e}"
            ) from e



    def switch_model(
        self,
        model_name: str,
        labels: list | None = None
    ) -> dict:
        """
        Switch the active AI model.

        If the model doesn't already exist, register it.
        If it exists, update its labels.
        Only one model can be active at a time.
        """

        if labels is None:
            labels = []

        try:
            with self.conn.cursor() as cur:

                # Check whether model exists
                cur.execute(
                    """
                    SELECT name, labels
                    FROM model
                    WHERE name = %s;
                    """,
                    (model_name,)
                )

                model = cur.fetchone()

                if model is None:
                    # Register new model
                    cur.execute(
                        """
                        INSERT INTO model (name, labels, active)
                        VALUES (%s, %s, FALSE)
                        RETURNING name, labels;
                        """,
                        (model_name, labels),
                    )
                    model = cur.fetchone()

                else:
                    # Model already exists:
                    # update its labels
                    cur.execute(
                        """
                        UPDATE model
                        SET labels = %s
                        WHERE name = %s
                        RETURNING name, labels;
                        """,
                        (labels, model_name),
                    )
                    model = cur.fetchone()

                # Deactivate current model
                cur.execute(
                    """
                    UPDATE model
                    SET active = FALSE
                    WHERE active = TRUE;
                    """
                )

                # Activate requested model
                cur.execute(
                    """
                    UPDATE model
                    SET active = TRUE
                    WHERE name = %s;
                    """,
                    (model_name,)
                )

                self.conn.commit()

                return {
                    "name": model[0],
                    "labels": model[1],
                    "active": True
                }

        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(
                f"Failed to switch model: {e}"
            ) from e


  


