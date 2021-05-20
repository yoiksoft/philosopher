-- upgrade --
CREATE TABLE IF NOT EXISTS "relationship" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "author_one_id" VARCHAR(40) NOT NULL,
    "author_two_id" VARCHAR(40) NOT NULL,
    "status" SMALLINT NOT NULL,
    "action_id" VARCHAR(40) NOT NULL,
    CONSTRAINT "uid_relationshi_author__18755a" UNIQUE ("author_one_id", "author_two_id")
);
COMMENT ON TABLE "relationship" IS 'Relationship model';
-- downgrade --
DROP TABLE IF EXISTS "relationship";
