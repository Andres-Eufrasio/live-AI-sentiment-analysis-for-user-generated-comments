-- ------------------------------------------------------------
-- Moderation system Schema by Andres Eufrasio Tinajero
-- ------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS "pgcrypto";  

-- ------------------------------------------------------------
-- User
-- ------------------------------------------------------------
CREATE TABLE "user" (
    id          TEXT        PRIMARY KEY,
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
    name        TEXT    PRIMARY KEY,
    labels       TEXT[]    NOT NULL,
    active BOOLEAN NOT NULL DEFAULT FALSE
);

-- ------------------------------------------------------------
-- Post
-- ------------------------------------------------------------
CREATE TABLE post (
    id          TEXT        PRIMARY KEY,
    content     TEXT        NOT NULL,
    author_id   TEXT        NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    posted_time TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ------------------------------------------------------------
-- Comment
-- ------------------------------------------------------------
CREATE TABLE comment (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    content             TEXT        NOT NULL,
    author_id           TEXT        REFERENCES "user"(id) ON DELETE CASCADE,
    post_id             TEXT        REFERENCES post(id) ON DELETE CASCADE,
    parent_comment_id   UUID        REFERENCES comment(id) ON DELETE SET NULL,
    posted_time         TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ------------------------------------------------------------
-- User_report
-- ------------------------------------------------------------
CREATE TABLE user_report (
    id          UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     TEXT    NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    comment_id  UUID    NOT NULL REFERENCES comment(id) ON DELETE CASCADE,
    reason      TEXT    NOT NULL,
    category    TEXT    NOT NULL,
    time_stamp      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ------------------------------------------------------------
-- Flag
-- ------------------------------------------------------------
CREATE TABLE flag (
    id                  UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    comment_id          UUID    NOT NULL REFERENCES comment(id) ON DELETE CASCADE,
    user_report_id      UUID    REFERENCES user_report(id) ON DELETE SET NULL,
    active              BOOLEAN NOT NULL
);

-- ------------------------------------------------------------
-- Prediction
-- ------------------------------------------------------------
CREATE TABLE prediction (
    id          UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    flag_id     UUID    REFERENCES flag(id) ON DELETE CASCADE,
    model_id    TEXT    NOT NULL REFERENCES model(name) ON DELETE RESTRICT,
    confidence  FLOAT[]   NOT NULL
);

-- ------------------------------------------------------------
-- Moderation_decision
-- ------------------------------------------------------------
CREATE TABLE moderation_decision (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    comment_id      UUID        NOT NULL REFERENCES comment(id) ON DELETE CASCADE,
    moderator_id    UUID        NOT NULL REFERENCES moderator(id) ON DELETE RESTRICT,
    flag_id         UUID        NOT NULL REFERENCES flag(id) ON DELETE RESTRICT,
    prediction_id   UUID        REFERENCES prediction(id) ON DELETE SET NULL,
    decision        BOOLEAN     NOT NULL,  
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
-- Rules
-- ------------------------------------------------------------

CREATE UNIQUE INDEX active_model
    ON model (active)
    WHERE active = TRUE;

-- ------------------------------------------------------------
-- views
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW unreviewed_flags AS
SELECT
    f.id,
    f.comment_id,
    c.content,

    c.author_id,
    u.username AS author_username,

    p.id AS prediction_id,
    p.model_id AS model_name,

    -- All labels and their corresponding confidence scores
    m.labels AS prediction_labels,
    p.confidence AS prediction_scores

FROM flag f

JOIN comment c
    ON c.id = f.comment_id

JOIN "user" u
    ON u.id = c.author_id

LEFT JOIN prediction p
    ON p.flag_id = f.id

LEFT JOIN model m
    ON m.name = p.model_id

WHERE NOT EXISTS (
    SELECT 1
    FROM moderation_decision md
    WHERE md.flag_id = f.id
);

CREATE OR REPLACE VIEW current_model AS
SELECT
    name, labels
FROM model
WHERE active = TRUE;


-- ------------------------------------------------------------
-- Test values
-- ------------------------------------------------------------
INSERT INTO "moderator" (id, username, password_hash)
VALUES
('8410a16f-032d-4ebf-a128-c0bfbb4e7df4', 'admin', 'hash');

INSERT INTO "user" (id, username, created_at, banned)
VALUES
    ('user1', 'test',   now(), false),
    (gen_random_uuid(), 'alice',   now(), false),
    (gen_random_uuid(), 'bob',     now(), false),
    (gen_random_uuid(), 'charlie', now(), false),
    (gen_random_uuid(), 'diana',    now(), false),
    (gen_random_uuid(), 'eve',     now(), true);

INSERT INTO post (id, content, author_id)
VALUES
    ('16c05c49-419b-48b8-9813-b573d7f6cb99', 'This is a post', 'user1');

INSERT INTO model (name, labels)
VALUES
    ('unitary/toxic-bert', ARRAY['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']);
