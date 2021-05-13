-- upgrade --
ALTER TABLE "meaning" ALTER COLUMN "author_id" DROP NOT NULL;
-- downgrade --
ALTER TABLE "meaning" ALTER COLUMN "author_id" SET NOT NULL;
