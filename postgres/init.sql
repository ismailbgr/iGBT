-- Adminer 4.8.1 PostgreSQL 16.1 (Debian 16.1-1.pgdg120+1) dump

CREATE TABLE "public"."Task" (
    "task_id" text NOT NULL,
    "result" text,
    "thumbnail" text,
    CONSTRAINT "Task_task_id" PRIMARY KEY ("task_id")
) WITH (oids = false);


CREATE TABLE "public"."UserTask" (
    "user_id" integer NOT NULL,
    "task_id" text NOT NULL
) WITH (oids = false);


CREATE SEQUENCE user_user_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;

CREATE TABLE "public"."user" (
    "user_id" bigint DEFAULT nextval('user_user_id_seq') NOT NULL,
    "ad" text NOT NULL,
    "soyad" text NOT NULL,
    "email" text NOT NULL,
    "telefon" text,
    "saltedpassword" text NOT NULL,
    "is_admin" boolean NOT NULL,
    CONSTRAINT "user_pkey" PRIMARY KEY ("user_id")
) WITH (oids = false);


ALTER TABLE ONLY "public"."UserTask" ADD CONSTRAINT "UserTask_task_id_fkey" FOREIGN KEY (task_id) REFERENCES "Task"(task_id) ON DELETE CASCADE NOT DEFERRABLE;
ALTER TABLE ONLY "public"."UserTask" ADD CONSTRAINT "UserTask_user_id_fkey" FOREIGN KEY (user_id) REFERENCES "user"(user_id) ON DELETE CASCADE NOT DEFERRABLE;

-- 2023-12-14 12:57:12.170905+00
