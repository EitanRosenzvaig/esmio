-- SEQUENCE: public.core_event_id_seq

-- DROP SEQUENCE public.core_event_id_seq;

CREATE SEQUENCE public.core_event_id_seq;

ALTER SEQUENCE public.core_event_id_seq
    OWNER TO saleor;

-- Table: public.core_event

-- DROP TABLE public.core_event;

CREATE TABLE public.core_event
(
	id integer NOT NULL DEFAULT nextval('core_event_id_seq'::regclass),
    event character varying(255) COLLATE pg_catalog."default" NOT NULL,
    url text COLLATE pg_catalog."default" NOT NULL,
    referrer text COLLATE pg_catalog."default",
    created_at timestamp without time zone NOT NULL,
    visitor_id character varying(10) COLLATE pg_catalog."default",
    data json,
    CONSTRAINT tracking_event_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.core_event
    OWNER to saleor;