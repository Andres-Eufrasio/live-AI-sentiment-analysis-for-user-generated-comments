-- ------------------------------------------------------------
-- Test values
-- ------------------------------------------------------------
INSERT INTO "user" (id, username, created_at, banned)
VALUES
    ('id1', 'test',   now(), false),
    ('id2', 'alice',   now(), false),
    ('id3', 'bob',     now(), false),
    ('id4', 'charlie', now(), false),
    ('id5', 'diana',    now(), false),
    (g'id6', 'eve',     now(), true);

INSERT INTO post(id, content, author_id)
VALUES
    ('16c05c49-419b-48b8-9813-b573d7f6cb99', 'This is a post', 'id1')
