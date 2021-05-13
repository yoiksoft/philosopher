-- upgrade --
ALTER TABLE "quote" ALTER COLUMN "author_id" TYPE VARCHAR(40) USING "author_id"::VARCHAR(40);
-- downgrade --
ALTER TABLE "quote" ALTER COLUMN "author" TYPE VARCHAR(40) USING "author"::VARCHAR(40);
