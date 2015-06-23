CREATE DATABASE app
  WITH OWNER = postgres
       ENCODING = 'UTF8'
       TABLESPACE = pg_default
       LC_COLLATE = 'en_US.UTF-8'
       LC_CTYPE = 'en_US.UTF-8'
       CONNECTION LIMIT = -1;

CREATE TYPE sub_frequency AS ENUM (‘never','asis','daily','week');
CREATE TYPE stat_option AS ENUM ('active','delete','inactive');
CREATE TYPE met_type AS ENUM (‘factor’,’character');

CREATE TABLE tarif (
  id serial NOT NULL,
  month_cost money,
  year_cost money,
  CONSTRAINT pk_tarif PRIMARY KEY (id)
) WITH (OIDS=FALSE);

CREATE TABLE "user" (
  id serial NOT NULL,
  tarif_id serial NOT NULL,
  name character varying(50),
  email character varying(50),
  subscribe sub_frequency,
  passwd character varying(32),
  CONSTRAINT pk_user PRIMARY KEY (id),
  CONSTRAINT pk_user2tarif FOREIGN KEY (tarif_id)
      REFERENCES tarif (id) MATCH SIMPLE
      ON UPDATE SET DEFAULT ON DELETE NO ACTION
) WITH (OIDS=FALSE);

CREATE TABLE project (
  id serial NOT NULL,
  user_id serial NOT NULL,
  name character varying(50),
  desctiption text,
  picture_path character varying(60),
  status stat_option,
  CONSTRAINT pk_project PRIMARY KEY (id),
  CONSTRAINT pk_project2user FOREIGN KEY (user_id)
      REFERENCES "user" (id) MATCH SIMPLE
      ON UPDATE SET DEFAULT ON DELETE NO ACTION
) WITH (OIDS=FALSE);

CREATE TABLE research (
  id serial NOT NULL,
  name character varying(50),
  project_id serial NOT NULL,
  user_id serial NOT NULL,
  status stat_option,
  CONSTRAINT pk_research PRIMARY KEY (id),
  CONSTRAINT pk_research2project FOREIGN KEY (project_id)
      REFERENCES project (id) MATCH SIMPLE
      ON UPDATE SET DEFAULT ON DELETE NO ACTION,
  CONSTRAINT pk_research2user FOREIGN KEY (user_id)
      REFERENCES "user" (id) MATCH SIMPLE
      ON UPDATE SET DEFAULT ON DELETE NO ACTION
) WITH (OIDS=FALSE);

CREATE TABLE method (
  id serial NOT NULL,
  parent_id serial NOT NULL,
  user_id serial NOT NULL,
  name character varying(50),
  description text,
  type met_type,
  tester tester_type,
  CONSTRAINT pk_method PRIMARY KEY (id),
  CONSTRAINT pk_method2parent FOREIGN KEY (parent_id)
      REFERENCES method (id) MATCH SIMPLE
      ON UPDATE SET DEFAULT ON DELETE NO ACTION,
  CONSTRAINT pk_method2user FOREIGN KEY (user_id)
      REFERENCES "user" (id) MATCH SIMPLE
      ON UPDATE SET DEFAULT ON DELETE NO ACTION
) WITH (OIDS=FALSE);

CREATE TABLE user2pay (
  id serial NOT NULL,
  user_id serial NOT NULL,
  tarif_id serial NOT NULL,
  cost money,
  data date,
  status stat_option,
  CONSTRAINT pk_user2pay PRIMARY KEY (id),
  CONSTRAINT pk_user2pay2tarif FOREIGN KEY (tarif_id)
      REFERENCES tarif (id) MATCH SIMPLE
      ON UPDATE SET DEFAULT ON DELETE NO ACTION,
  CONSTRAINT pk_user2pay2user FOREIGN KEY (user_id)
      REFERENCES "user" (id) MATCH SIMPLE
      ON UPDATE SET DEFAULT ON DELETE NO ACTION
) WITH (OIDS=FALSE);

CREATE TABLE user2research (
  id serial NOT NULL,
  user_id serial NOT NULL,
  invited_id serial NOT NULL,
  research_id serial NOT NULL,
  data date,
  status stat_option,
  CONSTRAINT pk_user2research PRIMARY KEY (id),
  CONSTRAINT pk_user2research2invited FOREIGN KEY (invited_id)
      REFERENCES "user" (id) MATCH SIMPLE
      ON UPDATE SET DEFAULT ON DELETE NO ACTION,
  CONSTRAINT pk_user2research2research FOREIGN KEY (research_id)
      REFERENCES research (id) MATCH SIMPLE
      ON UPDATE SET DEFAULT ON DELETE NO ACTION,
  CONSTRAINT pk_user2research2user FOREIGN KEY (user_id)
      REFERENCES "user" (id) MATCH SIMPLE
      ON UPDATE SET DEFAULT ON DELETE NO ACTION
) WITH (OIDS=FALSE);