-- ------------------------------------------------------------
-- Moderation system Schema by Andres Eufrasio Tinajero
-- ------------------------------------------------------------
-- uuid
CREATE EXTENSION IF NOT EXISTS "pgcrypto";  

-- ------------------------------------------------------------
-- User
-- ------------------------------------------------------------
CREATE TABLE "user" (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    username    TEXT        NOT NULL UNIQUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    banned      BOOLEAN     NOT NULL DEFAULT false
);

-- ------------------------------------------------------------
-- Moderator
-- ------------------------------------------------------------
CREATE TABLE moderator (
    id              UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    username        TEXT    NOT NULL UNIQUE,
    password_hash   TEXT    NOT NULL
);

-- ------------------------------------------------------------
-- Model
-- ------------------------------------------------------------
CREATE TABLE model (
    id          UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT    NOT NULL,
    label       TEXT    NOT NULL,
    confidence  INT     NOT NULL CHECK (confidence BETWEEN 0 AND 100)
);

-- ------------------------------------------------------------
-- Post
-- ------------------------------------------------------------
CREATE TABLE post (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    content     TEXT        NOT NULL,
    author_id   UUID        NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    context     TEXT,
    posted_time TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ------------------------------------------------------------
-- Comment
-- ------------------------------------------------------------
CREATE TABLE comment (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    content             TEXT        NOT NULL,
    author_id           UUID        REFERENCES "user"(id) ON DELETE CASCADE,
    post_id             UUID        NOT NULL REFERENCES post(id) ON DELETE CASCADE,
    parent_comment_id   UUID        REFERENCES comment(id) ON DELETE SET NULL,
    context             TEXT,
    posted_time         TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ------------------------------------------------------------
-- User_report
-- Submitted by a user about a specific comment
-- ------------------------------------------------------------
CREATE TABLE user_report (
    id          UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID    NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    comment_id  UUID    NOT NULL REFERENCES comment(id) ON DELETE CASCADE,
    reason      TEXT    NOT NULL,
    category    TEXT    NOT NULL,
    time_stamp      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ------------------------------------------------------------
-- Flag
-- Aggregates a comment, an optional user report, and
-- an optional AI prediction score into a single review unit
-- ------------------------------------------------------------
CREATE TABLE flag (
    id                  UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    comment_id          UUID    NOT NULL REFERENCES comment(id) ON DELETE CASCADE,
    user_report_id      UUID    REFERENCES user_report(id) ON DELETE SET NULL,
    prediction_score    FLOAT   CHECK (prediction_score BETWEEN 0.0 AND 1.0)
);

-- ------------------------------------------------------------
-- Prediction
-- ------------------------------------------------------------
CREATE TABLE prediction (
    id          UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    flag_id     UUID    NOT NULL REFERENCES flag(id) ON DELETE CASCADE,
    model_id    UUID    NOT NULL REFERENCES model(id) ON DELETE RESTRICT,
    confidence  FLOAT   NOT NULL CHECK (confidence BETWEEN 0.0 AND 1.0),
    label       TEXT    NOT NULL
);

-- ------------------------------------------------------------
-- Moderation_decision
-- Human moderator's verdict on a flagged comment
-- ------------------------------------------------------------
CREATE TABLE moderation_decision (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    comment_id      UUID        NOT NULL REFERENCES comment(id) ON DELETE CASCADE,
    moderator_id    UUID        NOT NULL REFERENCES moderator(id) ON DELETE RESTRICT,
    flag_id         UUID        NOT NULL REFERENCES flag(id) ON DELETE RESTRICT,
    prediction_id   UUID        REFERENCES prediction(id) ON DELETE SET NULL,
    decision        BOOLEAN     NOT NULL,   -- true = remove, false = keep
    time_stamp      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- Indexes
-- ============================================================
CREATE INDEX idx_post_author        ON post(author_id);
CREATE INDEX idx_comment_author     ON comment(author_id);
CREATE INDEX idx_comment_post       ON comment(post_id);
CREATE INDEX idx_comment_parent     ON comment(parent_comment_id);
CREATE INDEX idx_user_report_user   ON user_report(user_id);
CREATE INDEX idx_user_report_comment ON user_report(comment_id);
CREATE INDEX idx_flag_comment       ON flag(comment_id);
CREATE INDEX idx_flag_user_report   ON flag(user_report_id);
CREATE INDEX idx_prediction_flag    ON prediction(flag_id);
CREATE INDEX idx_prediction_model   ON prediction(model_id);
CREATE INDEX idx_moddec_comment     ON moderation_decision(comment_id);
CREATE INDEX idx_moddec_moderator   ON moderation_decision(moderator_id);
CREATE INDEX idx_moddec_flag        ON moderation_decision(flag_id);

-- ------------------------------------------------------------
-- views
-- ------------------------------------------------------------
CREATE VIEW unreviewed_flags AS
SELECT f.id, f.comment_id, f.prediction_score, c.content
FROM flag f
JOIN comment c ON c.id = f.comment_id
WHERE f.id NOT IN (SELECT flag_id FROM Moderation_decision)