--
-- PostgreSQL database dump (cleaned for PG 17)
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';

CREATE FUNCTION public.update_job_applications_count() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE jobs SET applications_count = applications_count + 1 WHERE id = NEW.job_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE jobs SET applications_count = applications_count - 1 WHERE id = OLD.job_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$;

ALTER FUNCTION public.update_job_applications_count() OWNER TO postgres;

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

ALTER FUNCTION public.update_updated_at_column() OWNER TO postgres;

SET default_tablespace = '';
SET default_table_access_method = heap;

CREATE TABLE public.applications (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    job_id uuid NOT NULL,
    job_seeker_id uuid NOT NULL,
    cover_letter text,
    status character varying(50) DEFAULT 'pending'::character varying,
    notes text,
    reviewed_by uuid,
    reviewed_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT applications_status_check CHECK (((status)::text = ANY ((ARRAY['pending'::character varying, 'reviewed'::character varying, 'interview'::character varying, 'accepted'::character varying, 'rejected'::character varying])::text[])))
);

ALTER TABLE public.applications OWNER TO postgres;

CREATE TABLE public.companies (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    website character varying(255),
    industry character varying(100),
    size character varying(50),
    location character varying(255),
    logo_url character varying(500),
    is_verified boolean DEFAULT false,
    verified_by uuid,
    verified_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    verification_status character varying(20) DEFAULT 'pending'::character varying,
    verification_documents text,
    CONSTRAINT companies_size_check CHECK (((size)::text = ANY ((ARRAY['1-10'::character varying, '11-50'::character varying, '51-200'::character varying, '201-500'::character varying, '500+'::character varying])::text[])))
);

ALTER TABLE public.companies OWNER TO postgres;

CREATE TABLE public.jobs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    employer_id uuid NOT NULL,
    company_id uuid NOT NULL,
    title character varying(255) NOT NULL,
    description text NOT NULL,
    location character varying(255),
    job_type character varying(50) NOT NULL,
    salary_range character varying(100),
    requirements text[],
    benefits text[],
    is_active boolean DEFAULT true,
    views_count integer DEFAULT 0,
    applications_count integer DEFAULT 0,
    expires_at timestamp without time zone DEFAULT (CURRENT_TIMESTAMP + '30 days'::interval),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT jobs_job_type_check CHECK (((job_type)::text = ANY ((ARRAY['full_time'::character varying, 'part_time'::character varying, 'remote'::character varying, 'hybrid'::character varying, 'contract'::character varying, 'internship'::character varying])::text[])))
);

ALTER TABLE public.jobs OWNER TO postgres;

CREATE TABLE public.notifications (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid,
    message text NOT NULL,
    is_read boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE public.notifications OWNER TO postgres;

CREATE TABLE public.profiles (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    bio text,
    skills text[],
    phone character varying(50),
    location character varying(255),
    years_experience integer,
    education text[],
    certifications text[],
    github_url character varying(255),
    linkedin_url character varying(255),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT profiles_years_experience_check CHECK ((years_experience >= 0))
);

ALTER TABLE public.profiles OWNER TO postgres;

CREATE TABLE public.saved_jobs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    job_id uuid NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE public.saved_jobs OWNER TO postgres;

CREATE TABLE public.skills (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying(100) NOT NULL,
    category character varying(100),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE public.skills OWNER TO postgres;

CREATE TABLE public.users (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    email character varying(255) NOT NULL,
    password_hash character varying(255) NOT NULL,
    full_name character varying(255) NOT NULL,
    user_type character varying(20) NOT NULL,
    is_active boolean DEFAULT true,
    last_login timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    plan character varying(20) DEFAULT 'free'::character varying,
    jobs_posted_this_month integer DEFAULT 0,
    plan_month_start date DEFAULT CURRENT_DATE,
    payment_status character varying(20) DEFAULT 'pending'::character varying,
    payment_date timestamp without time zone,
    is_admin boolean DEFAULT false,
    CONSTRAINT users_user_type_check CHECK (((user_type)::text = ANY ((ARRAY['job_seeker'::character varying, 'employer'::character varying, 'admin'::character varying])::text[])))
);

ALTER TABLE public.users OWNER TO postgres;

COPY public.applications (id, job_id, job_seeker_id, cover_letter, status, notes, reviewed_by, reviewed_at, created_at, updated_at) FROM stdin;
\.

COPY public.companies (id, name, description, website, industry, size, location, logo_url, is_verified, verified_by, verified_at, created_at, updated_at, verification_status, verification_documents) FROM stdin;
15b5ec56-a136-46ac-a8da-787efb80c201	مطعم كرار بركر			\N	\N	النجف	\N	f	\N	2026-06-30 12:25:34.484288	2026-06-30 12:25:17.372829	2026-06-30 12:25:34.484288	verified	المالك: احمد\nرقم الهوية: 567987654
b0c7dbd2-f7ad-422b-96e7-310ff2e36a29	mgg			\N	\N	444	\N	f	\N	2026-06-30 13:07:34.634844	2026-06-30 13:07:22.561011	2026-06-30 13:07:34.634844	verified	المالك: gmg\nرقم الهوية: 3432535
\.

COPY public.jobs (id, employer_id, company_id, title, description, location, job_type, salary_range, requirements, benefits, is_active, views_count, applications_count, expires_at, created_at, updated_at) FROM stdin;
\.

COPY public.notifications (id, user_id, message, is_read, created_at) FROM stdin;
94e652a8-6886-433e-8347-572926592395	4717d011-f88d-47bc-b271-65a6d7760868	تهانينا! تم قبولك في "m"	t	2026-06-28 11:25:51.211211
c7890387-ee27-484c-a541-143d3ac82899	4717d011-f88d-47bc-b271-65a6d7760868	تهانينا! تم قبولك في "m"	t	2026-06-28 11:26:10.695682
98cfc033-0baa-49e5-865f-26b6b7a74fe3	4717d011-f88d-47bc-b271-65a6d7760868	تهانينا! تم قبولك في "ة"	t	2026-06-28 12:07:04.247516
3888aa70-1771-4a04-9579-3fee319b8cc3	4717d011-f88d-47bc-b271-65a6d7760868	تهانينا! تم قبولك في "m"	f	2026-06-29 05:09:13.930043
81c433ec-2026-4268-9a1f-7dacec16fd89	4c77a195-2d4a-45d5-beb0-d2479642a885	تهانينا! تم قبولك في "m"	t	2026-06-28 11:19:07.82032
\.

COPY public.profiles (id, user_id, bio, skills, phone, location, years_experience, education, certifications, github_url, linkedin_url, created_at, updated_at) FROM stdin;
4d28b5f0-8e06-4dc7-bf23-4c3ea87d35b7	4c77a195-2d4a-45d5-beb0-d2479642a885	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-28 11:04:04.971494	2026-06-28 11:04:04.971494
b80869f3-b009-42d5-af9b-be34e3425187	4717d011-f88d-47bc-b271-65a6d7760868	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-28 11:25:06.274813	2026-06-28 11:25:06.274813
\.

COPY public.saved_jobs (id, user_id, job_id, created_at) FROM stdin;
\.

COPY public.skills (id, name, category, created_at) FROM stdin;
\.

COPY public.users (id, email, password_hash, full_name, user_type, is_active, last_login, created_at, updated_at, plan, jobs_posted_this_month, plan_month_start, payment_status, payment_date, is_admin) FROM stdin;
4c77a195-2d4a-45d5-beb0-d2479642a885	wanawaf482@brixozu.com	scrypt:32768:8:1$cZFy9rw6WvB53RUa$f09eae0cbbf2308a6e2e643dd78cec9a1d3af0bddd53de4596e4d1dd7065f04c9e92b5d7438ebc9c4509b47c734e2259b4b3a4ef303e2aa670992283772b4f51	m	job_seeker	t	2026-06-30 11:48:15.298765	2026-06-28 11:04:04.971494	2026-06-30 11:48:15.298765	free	0	2026-06-29	pending	\N	f
f4f637bb-d25f-437f-b891-f8e6d2ce3936	m@gmail.com	scrypt:32768:8:1$0cQM4HwlQMhAIyos$afe75d8ffd5380d0689e88471df07321031d2e480323983ffcf5c66109f2487bbe7ed163e14c3f9bd00d1030822c0043fbd7d0ffa971452f07e70df0ce785a2d	iii	employer	t	2026-06-29 04:07:48.905332	2026-06-29 04:07:39.619962	2026-06-29 04:07:48.905332	free	0	2026-06-29	pending	\N	f
532c01cf-517b-41a7-91a9-d87d17f55b73	carekev655@divahd.com	scrypt:32768:8:1$0A6Fu89LzocG8kJl$799577df3a0ffe6fa5153be2716d0b81f4811108597ac25669467a0b026d1f73d73a627d025ec83782150ab8495ce571d30eff87478d833c7113a981f6f3653d	muq	employer	t	2026-06-30 10:47:31.117774	2026-06-30 10:35:36.126365	2026-06-30 10:47:31.117774	free	0	2026-06-30	pending	\N	f
4717d011-f88d-47bc-b271-65a6d7760868	muktadasalam1111@gmail.com	scrypt:32768:8:1$QppxCsdYGplhVGZg$bb749358bffd07a0154a04cde18dd2d2158191eabc9c5e2b37e5d2bcf586c896b0a13b1f1f14b11835c172a40c027bbd458e32cfef61d998ef79e70f5479aacd	n	job_seeker	t	2026-06-30 11:51:41.697727	2026-06-28 11:25:06.274813	2026-06-30 11:51:41.697727	free	0	2026-06-29	pending	\N	f
d9cd6f66-88a5-495d-a6b8-a27b5cea4f55	seeker@mehna.com	scrypt:32768:8:1$H0I413cdanan2Ull$a7d7dbd35fe0e8e23cc58d5c0c506114c7ea98c6526ab5af208ff96e557418ad69b615bfac94d7a00e73b938ac6d68546dae6e688b9a664c820cc76a68e578fa	علي حسين	job_seeker	t	\N	2026-06-28 10:25:17.081787	2026-06-30 11:01:03.41629	free	0	2026-06-29	pending	\N	f
e6f4709f-976e-4562-96a8-277ecb07e86e	employer@mehna.com	scrypt:32768:8:1$H0I413cdanan2Ull$a7d7dbd35fe0e8e23cc58d5c0c506114c7ea98c6526ab5af208ff96e557418ad69b615bfac94d7a00e73b938ac6d68546dae6e688b9a664c820cc76a68e578fa	أحمد محمد	admin	t	2026-06-30 13:04:27.600723	2026-06-28 10:25:17.07333	2026-06-30 13:04:27.600723	free	0	2026-06-29	pending	\N	t
dbde562e-1829-4182-b1fe-bb00a13eb855	bipej67781@divahd.com	scrypt:32768:8:1$GpQ1gY6GGVsFoqX8$9dc4fbb7e75c90af3b96b2a4d3d3e212563a89b84e799829851969795265874857a101ace981ef3cc36a61a3398d654abb6611f4a699ade68ec3b17a629d9493	q	employer	t	2026-06-30 13:07:06.704893	2026-06-28 11:04:29.571178	2026-06-30 13:07:06.704893	free	0	2026-06-29	pending	\N	f
\.

ALTER TABLE ONLY public.applications
    ADD CONSTRAINT applications_job_id_job_seeker_id_key UNIQUE (job_id, job_seeker_id);

ALTER TABLE ONLY public.applications
    ADD CONSTRAINT applications_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.profiles
    ADD CONSTRAINT profiles_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.profiles
    ADD CONSTRAINT profiles_user_id_key UNIQUE (user_id);

ALTER TABLE ONLY public.saved_jobs
    ADD CONSTRAINT saved_jobs_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.saved_jobs
    ADD CONSTRAINT saved_jobs_user_id_job_id_key UNIQUE (user_id, job_id);

ALTER TABLE ONLY public.skills
    ADD CONSTRAINT skills_name_key UNIQUE (name);

ALTER TABLE ONLY public.skills
    ADD CONSTRAINT skills_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);

CREATE INDEX idx_applications_created_at ON public.applications USING btree (created_at DESC);
CREATE INDEX idx_applications_job_id ON public.applications USING btree (job_id);
CREATE INDEX idx_applications_job_seeker_id ON public.applications USING btree (job_seeker_id);
CREATE INDEX idx_applications_status ON public.applications USING btree (status);
CREATE INDEX idx_companies_industry ON public.companies USING btree (industry);
CREATE INDEX idx_companies_is_verified ON public.companies USING btree (is_verified);
CREATE INDEX idx_companies_name ON public.companies USING btree (name);
CREATE INDEX idx_jobs_company_id ON public.jobs USING btree (company_id);
CREATE INDEX idx_jobs_created_at ON public.jobs USING btree (created_at DESC);
CREATE INDEX idx_jobs_employer_id ON public.jobs USING btree (employer_id);
CREATE INDEX idx_jobs_expires_at ON public.jobs USING btree (expires_at);
CREATE INDEX idx_jobs_is_active ON public.jobs USING btree (is_active);
CREATE INDEX idx_jobs_job_type ON public.jobs USING btree (job_type);
CREATE INDEX idx_jobs_location ON public.jobs USING btree (location);
CREATE INDEX idx_jobs_title ON public.jobs USING gin (to_tsvector('english'::regconfig, (title)::text));
CREATE INDEX idx_profiles_skills ON public.profiles USING gin (skills);
CREATE INDEX idx_profiles_user_id ON public.profiles USING btree (user_id);
CREATE INDEX idx_saved_jobs_job_id ON public.saved_jobs USING btree (job_id);
CREATE INDEX idx_saved_jobs_user_id ON public.saved_jobs USING btree (user_id);
CREATE INDEX idx_skills_name ON public.skills USING btree (name);
CREATE INDEX idx_users_email ON public.users USING btree (email);
CREATE INDEX idx_users_user_type ON public.users USING btree (user_type);

CREATE TRIGGER update_applications_updated_at BEFORE UPDATE ON public.applications FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON public.companies FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER update_job_applications_count_after_delete AFTER DELETE ON public.applications FOR EACH ROW EXECUTE FUNCTION public.update_job_applications_count();
CREATE TRIGGER update_job_applications_count_after_insert AFTER INSERT ON public.applications FOR EACH ROW EXECUTE FUNCTION public.update_job_applications_count();
CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON public.jobs FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON public.profiles FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE ONLY public.applications
    ADD CONSTRAINT applications_job_id_fkey FOREIGN KEY (job_id) REFERENCES public.jobs(id) ON DELETE CASCADE;
ALTER TABLE ONLY public.applications
    ADD CONSTRAINT applications_job_seeker_id_fkey FOREIGN KEY (job_seeker_id) REFERENCES public.users(id) ON DELETE CASCADE;
ALTER TABLE ONLY public.applications
    ADD CONSTRAINT applications_reviewed_by_fkey FOREIGN KEY (reviewed_by) REFERENCES public.users(id) ON DELETE SET NULL;
ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_verified_by_fkey FOREIGN KEY (verified_by) REFERENCES public.users(id) ON DELETE SET NULL;
ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;
ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_employer_id_fkey FOREIGN KEY (employer_id) REFERENCES public.users(id) ON DELETE CASCADE;
ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;
ALTER TABLE ONLY public.profiles
    ADD CONSTRAINT profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;
ALTER TABLE ONLY public.saved_jobs
    ADD CONSTRAINT saved_jobs_job_id_fkey FOREIGN KEY (job_id) REFERENCES public.jobs(id) ON DELETE CASCADE;
ALTER TABLE ONLY public.saved_jobs
    ADD CONSTRAINT saved_jobs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;
