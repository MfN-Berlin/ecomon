SET check_function_bodies = false;
CREATE TYPE public.job_status AS ENUM (
    'running',
    'preparing',
    'finalizing',
    'done',
    'failed',
    'pending',
    'canceled'
);
CREATE TYPE public.job_type AS ENUM (
    'analyze_with_model',
    'import_site_records',
    'create_sample',
    'calc_bin_sizes',
    'calc_predictions',
    'calc_daily_histograms',
    'calc_activation',
    'create_voucher'
);

CREATE FUNCTION public.set_current_timestamp_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
  _new record;
BEGIN
  _new := NEW;
  _new."updated_at" = NOW();
  RETURN _new;
END;
$$;
CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ BEGIN NEW.updated_at = NOW();
RETURN NEW;
END;
$$;
CREATE TABLE public.events (
    id bigint NOT NULL,
    model_id bigint NOT NULL,
    record_id bigint NOT NULL,
    label_id bigint NOT NULL,
    start_time numeric(9,4) NOT NULL,
    end_time numeric(9,4) NOT NULL,
    channel text NOT NULL,
    confidence real NOT NULL
);
CREATE SEQUENCE public.events_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.events_id_seq OWNED BY public.events.id;
CREATE TABLE public.jobs (
    id bigint NOT NULL,
    topic text NOT NULL,
    status public.job_status DEFAULT 'running'::public.job_status NOT NULL,
    metadata jsonb,
    result jsonb,
    progress double precision DEFAULT 0 NOT NULL,
    error jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone
);
CREATE SEQUENCE public.jobs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.jobs_id_seq OWNED BY public.jobs.id;
CREATE TABLE public.labels (
    id integer NOT NULL,
    name text NOT NULL,
    english text,
    german text,
    gbif text,
    class text,
    "order" text
);
CREATE SEQUENCE public.labels_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.labels_id_seq OWNED BY public.labels.id;
CREATE TABLE public.locations (
    id bigint NOT NULL,
    name text NOT NULL,
    lat numeric(9,6),
    long numeric(9,6),
    remarks text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone
);
COMMENT ON TABLE public.locations IS 'Locations';
CREATE SEQUENCE public.location_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.location_id_seq OWNED BY public.locations.id;
CREATE TABLE public.model_inference_results (
    id bigint NOT NULL,
    record_id bigint NOT NULL,
    model_id integer NOT NULL,
    label_id integer NOT NULL,
    start_time numeric(9,4) NOT NULL,
    end_time numeric(9,4) NOT NULL,
    confidence real NOT NULL
);
CREATE SEQUENCE public.model_inference_results_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.model_inference_results_id_seq OWNED BY public.model_inference_results.id;
CREATE TABLE public.model_labels (
    model_id integer NOT NULL,
    label_id integer NOT NULL,
    id integer NOT NULL
);
COMMENT ON TABLE public.model_labels IS 'Contains all all labels a mode uses';
CREATE SEQUENCE public.model_labels_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.model_labels_id_seq OWNED BY public.model_labels.id;
CREATE TABLE public.models (
    id integer NOT NULL,
    name text NOT NULL,
    additional_docker_arguments text,
    additional_model_arguments text,
    window_size integer,
    step_size integer,
    remarks text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone
);
CREATE SEQUENCE public.models_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.models_id_seq OWNED BY public.models.id;
CREATE TABLE public.records (
    id bigint NOT NULL,
    site_id bigint NOT NULL,
    filepath text NOT NULL,
    filename text NOT NULL,
    record_datetime timestamp without time zone NOT NULL,
    duration numeric(9,4) NOT NULL,
    channels text NOT NULL,
    sample_rate integer NOT NULL,
    mime_type text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    errors jsonb
);
COMMENT ON TABLE public.records IS 'All records metdata and datapath';
CREATE SEQUENCE public.records_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.records_id_seq OWNED BY public.records.id;
CREATE TABLE public.set_informations (
    id bigint NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    record_regime_recording_duration numeric(9,4) DEFAULT 0 NOT NULL,
    record_regime_pause_duration numeric(9,4) DEFAULT 0 NOT NULL,
    first_record timestamp without time zone,
    last_record timestamp without time zone,
    record_count bigint DEFAULT 0 NOT NULL,
    record_duration numeric(14,4) DEFAULT 0 NOT NULL,
    corrupted_record_count bigint DEFAULT 0 NOT NULL,
    remarks text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);
COMMENT ON TABLE public.set_informations IS 'Contains all aggregated  information about the set, collected from is records.';
CREATE SEQUENCE public.set_informations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.set_informations_id_seq OWNED BY public.set_informations.id;
CREATE TABLE public.sets (
    id bigint NOT NULL,
    name text NOT NULL,
    set_information_id bigint,
    remarks text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone
);
COMMENT ON TABLE public.sets IS 'Group Parts of data from sites into sets';
CREATE SEQUENCE public.sets_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.sets_id_seq OWNED BY public.sets.id;
CREATE TABLE public.sets_sites_selections (
    id bigint NOT NULL,
    set_id bigint NOT NULL,
    site_id bigint NOT NULL,
    "from" timestamp without time zone NOT NULL,
    "to" timestamp without time zone NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone
);
CREATE SEQUENCE public.sets_sites_selections_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.sets_sites_selections_id_seq OWNED BY public.sets_sites_selections.id;
CREATE TABLE public.site_directories (
    id bigint NOT NULL,
    site_id bigint NOT NULL,
    directory text NOT NULL
);
CREATE SEQUENCE public.site_directories_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.site_directories_id_seq OWNED BY public.site_directories.id;
CREATE TABLE public.site_reports (
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    site_id bigint NOT NULL,
    first_record_date timestamp without time zone,
    last_record_date timestamp without time zone,
    records_count integer NOT NULL,
    record_duration integer NOT NULL,
    corrupted_files jsonb NOT NULL,
    duration_histogram jsonb NOT NULL,
    daily_histogram jsonb NOT NULL,
    monthly_histogram jsonb NOT NULL,
    records_heatmap jsonb NOT NULL
);
COMMENT ON TABLE public.site_reports IS 'Contains site records report';
CREATE SEQUENCE public.site_report_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.site_report_id_seq OWNED BY public.site_reports.id;
CREATE TABLE public.sites (
    id bigint NOT NULL,
    name text NOT NULL,
    location_id bigint NOT NULL,
    record_regime_recording_duration numeric(9,4) DEFAULT 0 NOT NULL,
    record_regime_pause_duration numeric(9,4) DEFAULT 0 NOT NULL,
    sample_rate integer NOT NULL,
    remarks text NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone,
    alias text NOT NULL
);
CREATE SEQUENCE public.sites_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.sites_id_seq OWNED BY public.sites.id;
ALTER TABLE ONLY public.events ALTER COLUMN id SET DEFAULT nextval('public.events_id_seq'::regclass);
ALTER TABLE ONLY public.jobs ALTER COLUMN id SET DEFAULT nextval('public.jobs_id_seq'::regclass);
ALTER TABLE ONLY public.labels ALTER COLUMN id SET DEFAULT nextval('public.labels_id_seq'::regclass);
ALTER TABLE ONLY public.locations ALTER COLUMN id SET DEFAULT nextval('public.location_id_seq'::regclass);
ALTER TABLE ONLY public.model_inference_results ALTER COLUMN id SET DEFAULT nextval('public.model_inference_results_id_seq'::regclass);
ALTER TABLE ONLY public.model_labels ALTER COLUMN id SET DEFAULT nextval('public.model_labels_id_seq'::regclass);
ALTER TABLE ONLY public.models ALTER COLUMN id SET DEFAULT nextval('public.models_id_seq'::regclass);
ALTER TABLE ONLY public.records ALTER COLUMN id SET DEFAULT nextval('public.records_id_seq'::regclass);
ALTER TABLE ONLY public.set_informations ALTER COLUMN id SET DEFAULT nextval('public.set_informations_id_seq'::regclass);
ALTER TABLE ONLY public.sets ALTER COLUMN id SET DEFAULT nextval('public.sets_id_seq'::regclass);
ALTER TABLE ONLY public.sets_sites_selections ALTER COLUMN id SET DEFAULT nextval('public.sets_sites_selections_id_seq'::regclass);
ALTER TABLE ONLY public.site_directories ALTER COLUMN id SET DEFAULT nextval('public.site_directories_id_seq'::regclass);
ALTER TABLE ONLY public.site_reports ALTER COLUMN id SET DEFAULT nextval('public.site_report_id_seq'::regclass);
ALTER TABLE ONLY public.sites ALTER COLUMN id SET DEFAULT nextval('public.sites_id_seq'::regclass);
ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.labels
    ADD CONSTRAINT labels_name_key UNIQUE (name);
ALTER TABLE ONLY public.labels
    ADD CONSTRAINT labels_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.locations
    ADD CONSTRAINT location_name_key UNIQUE (name);
ALTER TABLE ONLY public.locations
    ADD CONSTRAINT location_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.model_inference_results
    ADD CONSTRAINT model_inference_results_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.model_labels
    ADD CONSTRAINT model_labels_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.models
    ADD CONSTRAINT models_name_key UNIQUE (name);
ALTER TABLE ONLY public.models
    ADD CONSTRAINT models_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.records
    ADD CONSTRAINT records_filename_key UNIQUE (filename);
ALTER TABLE ONLY public.records
    ADD CONSTRAINT records_filepath_key UNIQUE (filepath);
ALTER TABLE ONLY public.records
    ADD CONSTRAINT records_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.set_informations
    ADD CONSTRAINT set_informations_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.sets
    ADD CONSTRAINT sets_name_key UNIQUE (name);
ALTER TABLE ONLY public.sets
    ADD CONSTRAINT sets_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.sets_sites_selections
    ADD CONSTRAINT sets_sites_selections_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.site_directories
    ADD CONSTRAINT site_directories_directory_key UNIQUE (directory);
ALTER TABLE ONLY public.site_directories
    ADD CONSTRAINT site_directories_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.site_reports
    ADD CONSTRAINT site_report_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.sites
    ADD CONSTRAINT sites_name_key UNIQUE (name);
ALTER TABLE ONLY public.sites
    ADD CONSTRAINT sites_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.sites
    ADD CONSTRAINT sites_short_id_key UNIQUE (alias);
CREATE INDEX created_at_index ON public.jobs USING btree (created_at);
CREATE UNIQUE INDEX id_unique ON public.jobs USING btree (id);
CREATE INDEX idx_model_id ON public.model_inference_results USING btree (model_id);
CREATE INDEX idx_model_record ON public.model_inference_results USING btree (model_id, record_id);
CREATE INDEX record_datetime ON public.records USING brin (record_datetime);
CREATE INDEX topic_index ON public.jobs USING btree (topic);
CREATE INDEX updated_at_index ON public.jobs USING btree (updated_at);
CREATE TRIGGER set_public_jobs_updated_at BEFORE UPDATE ON public.jobs FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
CREATE TRIGGER set_public_location_updated_at BEFORE UPDATE ON public.locations FOR EACH ROW EXECUTE FUNCTION public.set_current_timestamp_updated_at();
COMMENT ON TRIGGER set_public_location_updated_at ON public.locations IS 'trigger to set value of column "updated_at" to current timestamp on row update';
CREATE TRIGGER set_public_models_updated_at BEFORE UPDATE ON public.models FOR EACH ROW EXECUTE FUNCTION public.set_current_timestamp_updated_at();
CREATE TRIGGER set_public_set_informations_updated_at BEFORE UPDATE ON public.set_informations FOR EACH ROW EXECUTE FUNCTION public.set_current_timestamp_updated_at();
COMMENT ON TRIGGER set_public_set_informations_updated_at ON public.set_informations IS 'trigger to set value of column "updated_at" to current timestamp on row update';
CREATE TRIGGER set_public_sets_sites_selections_updated_at BEFORE UPDATE ON public.sets_sites_selections FOR EACH ROW EXECUTE FUNCTION public.set_current_timestamp_updated_at();
COMMENT ON TRIGGER set_public_sets_sites_selections_updated_at ON public.sets_sites_selections IS 'trigger to set value of column "updated_at" to current timestamp on row update';
CREATE TRIGGER set_public_sets_updated_at BEFORE UPDATE ON public.sets FOR EACH ROW EXECUTE FUNCTION public.set_current_timestamp_updated_at();
COMMENT ON TRIGGER set_public_sets_updated_at ON public.sets IS 'trigger to set value of column "updated_at" to current timestamp on row update';
CREATE TRIGGER set_public_sites_updated_at BEFORE UPDATE ON public.sites FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_label_id_fkey FOREIGN KEY (label_id) REFERENCES public.labels(id) ON UPDATE RESTRICT ON DELETE RESTRICT;
ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_model_id_fkey FOREIGN KEY (model_id) REFERENCES public.models(id) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_record_id_fkey FOREIGN KEY (record_id) REFERENCES public.records(id) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY public.model_inference_results
    ADD CONSTRAINT fk_label FOREIGN KEY (label_id) REFERENCES public.labels(id);
ALTER TABLE ONLY public.model_inference_results
    ADD CONSTRAINT fk_model FOREIGN KEY (model_id) REFERENCES public.models(id);
ALTER TABLE ONLY public.model_inference_results
    ADD CONSTRAINT fk_record FOREIGN KEY (record_id) REFERENCES public.records(id);
ALTER TABLE ONLY public.model_labels
    ADD CONSTRAINT model_labels_label_id_fkey FOREIGN KEY (label_id) REFERENCES public.labels(id) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY public.model_labels
    ADD CONSTRAINT model_labels_model_id_fkey FOREIGN KEY (model_id) REFERENCES public.models(id) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY public.records
    ADD CONSTRAINT records_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.sites(id) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY public.sets
    ADD CONSTRAINT sets_set_informations_fkey FOREIGN KEY (set_information_id) REFERENCES public.set_informations(id) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY public.sets_sites_selections
    ADD CONSTRAINT sets_sites_selections_set_id_fkey FOREIGN KEY (set_id) REFERENCES public.sets(id) ON UPDATE RESTRICT ON DELETE CASCADE;
ALTER TABLE ONLY public.sets_sites_selections
    ADD CONSTRAINT sets_sites_selections_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.sites(id) ON UPDATE RESTRICT ON DELETE CASCADE;
ALTER TABLE ONLY public.site_directories
    ADD CONSTRAINT site_directories_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.sites(id) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY public.site_reports
    ADD CONSTRAINT site_report_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.sites(id) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY public.sites
    ADD CONSTRAINT sites_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.locations(id) ON UPDATE RESTRICT ON DELETE CASCADE;
