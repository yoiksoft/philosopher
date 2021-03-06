-- upgrade --
CREATE TABLE IF NOT EXISTS "quote" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "body" VARCHAR(140) NOT NULL,
    "author" VARCHAR(40),
    "published" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE "quote" IS 'Quote model';
CREATE TABLE IF NOT EXISTS "meaning" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "body" VARCHAR(240) NOT NULL,
    "author" VARCHAR(40),
    "published" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "quote_id" INT NOT NULL REFERENCES "quote" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "meaning" IS 'Meaning model';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(20) NOT NULL,
    "content" JSONB NOT NULL
);
