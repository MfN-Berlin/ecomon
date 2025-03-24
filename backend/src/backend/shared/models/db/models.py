from typing import List, Optional

from sqlalchemy import BigInteger, Boolean, Column, Date, DateTime, Double, Enum, Float, ForeignKeyConstraint, Index, Integer, Numeric, PrimaryKeyConstraint, Sequence, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship
from sqlalchemy.orm.base import Mapped

Base = declarative_base()


class Jobs(Base):
    __tablename__ = 'jobs'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='jobs_pkey'),
        Index('created_at_index', 'created_at'),
        Index('id_unique', 'id', unique=True),
        Index('topic_index', 'topic'),
        Index('updated_at_index', 'updated_at')
    )

    id = mapped_column(BigInteger)
    topic = mapped_column(Text, nullable=False)
    status = mapped_column(Enum('running', 'preparing', 'finalizing', 'done', 'failed', 'pending', 'canceled', name='job_status'), nullable=False, server_default=text("'running'::job_status"))
    progress = mapped_column(Double(53), nullable=False, server_default=text('0'))
    created_at = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    metadata_ = mapped_column('metadata', JSONB)
    result = mapped_column(JSONB)
    error = mapped_column(JSONB)
    updated_at = mapped_column(DateTime)


class Labels(Base):
    __tablename__ = 'labels'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='labels_pkey'),
        UniqueConstraint('name', name='labels_name_key')
    )

    id = mapped_column(Integer)
    name = mapped_column(Text, nullable=False)
    english = mapped_column(Text)
    german = mapped_column(Text)
    gbif = mapped_column(Text)
    class_ = mapped_column('class', Text)
    order = mapped_column(Text)

    model_labels: Mapped[List['ModelLabels']] = relationship('ModelLabels', uselist=True, back_populates='label')
    events: Mapped[List['Events']] = relationship('Events', uselist=True, back_populates='label')
    model_inference_results: Mapped[List['ModelInferenceResults']] = relationship('ModelInferenceResults', uselist=True, back_populates='label')


class Locations(Base):
    __tablename__ = 'locations'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='location_pkey'),
        UniqueConstraint('name', name='location_name_key'),
        {'comment': 'Locations'}
    )

    id = mapped_column(BigInteger, Sequence('location_id_seq'))
    name = mapped_column(Text, nullable=False)
    created_at = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    lat = mapped_column(Numeric(9, 6))
    long = mapped_column(Numeric(9, 6))
    remarks = mapped_column(Text)
    updated_at = mapped_column(DateTime(True))

    sites: Mapped[List['Sites']] = relationship('Sites', uselist=True, back_populates='location')


class Models(Base):
    __tablename__ = 'models'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='models_pkey'),
        UniqueConstraint('name', name='models_name_key')
    )

    id = mapped_column(Integer)
    name = mapped_column(Text, nullable=False)
    created_at = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    additional_docker_arguments = mapped_column(Text)
    additional_model_arguments = mapped_column(Text)
    window_size = mapped_column(Integer)
    step_size = mapped_column(Integer)
    remarks = mapped_column(Text)
    updated_at = mapped_column(DateTime)

    model_labels: Mapped[List['ModelLabels']] = relationship('ModelLabels', uselist=True, back_populates='model')
    events: Mapped[List['Events']] = relationship('Events', uselist=True, back_populates='model')
    model_inference_log: Mapped[List['ModelInferenceLog']] = relationship('ModelInferenceLog', uselist=True, back_populates='model')
    model_inference_results: Mapped[List['ModelInferenceResults']] = relationship('ModelInferenceResults', uselist=True, back_populates='model')


class SetInformations(Base):
    __tablename__ = 'set_informations'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='set_informations_pkey'),
        {'comment': 'Contains all aggregated  information about the set, collected '
                'from is records.'}
    )

    id = mapped_column(BigInteger)
    start_date = mapped_column(Date, nullable=False)
    end_date = mapped_column(Date, nullable=False)
    record_regime_recording_duration = mapped_column(Numeric(9, 4), nullable=False, server_default=text('0'))
    record_regime_pause_duration = mapped_column(Numeric(9, 4), nullable=False, server_default=text('0'))
    record_count = mapped_column(BigInteger, nullable=False, server_default=text('0'))
    record_duration = mapped_column(Numeric(14, 4), nullable=False, server_default=text('0'))
    corrupted_record_count = mapped_column(BigInteger, nullable=False, server_default=text('0'))
    created_at = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    first_record = mapped_column(DateTime)
    last_record = mapped_column(DateTime)
    remarks = mapped_column(Text)

    sets: Mapped[List['Sets']] = relationship('Sets', uselist=True, back_populates='set_information')


class ModelLabels(Base):
    __tablename__ = 'model_labels'
    __table_args__ = (
        ForeignKeyConstraint(['label_id'], ['labels.id'], ondelete='CASCADE', onupdate='CASCADE', name='model_labels_label_id_fkey'),
        ForeignKeyConstraint(['model_id'], ['models.id'], ondelete='CASCADE', onupdate='CASCADE', name='model_labels_model_id_fkey'),
        PrimaryKeyConstraint('id', name='model_labels_pkey'),
        {'comment': 'Contains all all labels a mode uses'}
    )

    model_id = mapped_column(Integer, nullable=False)
    label_id = mapped_column(Integer, nullable=False)
    id = mapped_column(Integer)

    label: Mapped['Labels'] = relationship('Labels', back_populates='model_labels')
    model: Mapped['Models'] = relationship('Models', back_populates='model_labels')


class Sets(Base):
    __tablename__ = 'sets'
    __table_args__ = (
        ForeignKeyConstraint(['set_information_id'], ['set_informations.id'], ondelete='CASCADE', onupdate='CASCADE', name='sets_set_informations_fkey'),
        PrimaryKeyConstraint('id', name='sets_pkey'),
        UniqueConstraint('name', name='sets_name_key'),
        {'comment': 'Group Parts of data from sites into sets'}
    )

    id = mapped_column(BigInteger)
    name = mapped_column(Text, nullable=False)
    created_at = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    set_information_id = mapped_column(BigInteger)
    remarks = mapped_column(Text)
    updated_at = mapped_column(DateTime(True))

    set_information: Mapped[Optional['SetInformations']] = relationship('SetInformations', back_populates='sets')
    sets_sites_selections: Mapped[List['SetsSitesSelections']] = relationship('SetsSitesSelections', uselist=True, back_populates='set')


class Sites(Base):
    __tablename__ = 'sites'
    __table_args__ = (
        ForeignKeyConstraint(['location_id'], ['locations.id'], ondelete='CASCADE', onupdate='RESTRICT', name='sites_location_id_fkey'),
        PrimaryKeyConstraint('id', name='sites_pkey'),
        UniqueConstraint('alias', name='sites_short_id_key'),
        UniqueConstraint('name', name='sites_name_key')
    )

    id = mapped_column(BigInteger)
    name = mapped_column(Text, nullable=False)
    location_id = mapped_column(BigInteger, nullable=False)
    record_regime_recording_duration = mapped_column(Numeric(9, 4), nullable=False, server_default=text('0'))
    record_regime_pause_duration = mapped_column(Numeric(9, 4), nullable=False, server_default=text('0'))
    sample_rate = mapped_column(Integer, nullable=False)
    remarks = mapped_column(Text, nullable=False)
    created_at = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    alias = mapped_column(Text, nullable=False)
    updated_at = mapped_column(DateTime)

    location: Mapped['Locations'] = relationship('Locations', back_populates='sites')
    records: Mapped[List['Records']] = relationship('Records', uselist=True, back_populates='site')
    sets_sites_selections: Mapped[List['SetsSitesSelections']] = relationship('SetsSitesSelections', uselist=True, back_populates='site')
    site_directories: Mapped[List['SiteDirectories']] = relationship('SiteDirectories', uselist=True, back_populates='site')
    site_reports: Mapped[List['SiteReports']] = relationship('SiteReports', uselist=True, back_populates='site')


class Records(Base):
    __tablename__ = 'records'
    __table_args__ = (
        ForeignKeyConstraint(['site_id'], ['sites.id'], ondelete='CASCADE', onupdate='CASCADE', name='records_site_id_fkey'),
        PrimaryKeyConstraint('id', name='records_pkey'),
        UniqueConstraint('filename', name='records_filename_key'),
        UniqueConstraint('filepath', name='records_filepath_key'),
        Index('record_datetime', 'record_datetime'),
        {'comment': 'All records metdata and datapath'}
    )

    id = mapped_column(BigInteger)
    site_id = mapped_column(BigInteger, nullable=False)
    filepath = mapped_column(Text, nullable=False)
    filename = mapped_column(Text, nullable=False)
    record_datetime = mapped_column(DateTime, nullable=False)
    duration = mapped_column(Numeric(9, 4), nullable=False)
    channels = mapped_column(Text, nullable=False)
    sample_rate = mapped_column(Integer, nullable=False)
    mime_type = mapped_column(Text, nullable=False)
    created_at = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    errors = mapped_column(JSONB)

    site: Mapped['Sites'] = relationship('Sites', back_populates='records')
    events: Mapped[List['Events']] = relationship('Events', uselist=True, back_populates='record')
    model_inference_results: Mapped[List['ModelInferenceResults']] = relationship('ModelInferenceResults', uselist=True, back_populates='record')


class SetsSitesSelections(Base):
    __tablename__ = 'sets_sites_selections'
    __table_args__ = (
        ForeignKeyConstraint(['set_id'], ['sets.id'], ondelete='CASCADE', onupdate='RESTRICT', name='sets_sites_selections_set_id_fkey'),
        ForeignKeyConstraint(['site_id'], ['sites.id'], ondelete='CASCADE', onupdate='RESTRICT', name='sets_sites_selections_site_id_fkey'),
        PrimaryKeyConstraint('id', name='sets_sites_selections_pkey')
    )

    id = mapped_column(BigInteger)
    set_id = mapped_column(BigInteger, nullable=False)
    site_id = mapped_column(BigInteger, nullable=False)
    from_ = mapped_column('from', DateTime, nullable=False)
    to = mapped_column(DateTime, nullable=False)
    created_at = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at = mapped_column(DateTime(True))

    set: Mapped['Sets'] = relationship('Sets', back_populates='sets_sites_selections')
    site: Mapped['Sites'] = relationship('Sites', back_populates='sets_sites_selections')


class SiteDirectories(Base):
    __tablename__ = 'site_directories'
    __table_args__ = (
        ForeignKeyConstraint(['site_id'], ['sites.id'], ondelete='CASCADE', onupdate='CASCADE', name='site_directories_site_id_fkey'),
        PrimaryKeyConstraint('id', name='site_directories_pkey'),
        UniqueConstraint('directory', name='site_directories_directory_key')
    )

    id = mapped_column(BigInteger)
    site_id = mapped_column(BigInteger, nullable=False)
    directory = mapped_column(Text, nullable=False)

    site: Mapped['Sites'] = relationship('Sites', back_populates='site_directories')


class SiteReports(Base):
    __tablename__ = 'site_reports'
    __table_args__ = (
        ForeignKeyConstraint(['site_id'], ['sites.id'], ondelete='CASCADE', onupdate='CASCADE', name='site_report_site_id_fkey'),
        PrimaryKeyConstraint('id', name='site_report_pkey'),
        {'comment': 'Contains site records report'}
    )

    id = mapped_column(Integer, Sequence('site_report_id_seq'))
    created_at = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    site_id = mapped_column(BigInteger, nullable=False)
    records_count = mapped_column(Integer, nullable=False)
    record_duration = mapped_column(Integer, nullable=False)
    corrupted_files = mapped_column(JSONB, nullable=False)
    duration_histogram = mapped_column(JSONB, nullable=False)
    daily_histogram = mapped_column(JSONB, nullable=False)
    monthly_histogram = mapped_column(JSONB, nullable=False)
    records_heatmap = mapped_column(JSONB, nullable=False)
    first_record_date = mapped_column(DateTime)
    last_record_date = mapped_column(DateTime)

    site: Mapped['Sites'] = relationship('Sites', back_populates='site_reports')


class Events(Base):
    __tablename__ = 'events'
    __table_args__ = (
        ForeignKeyConstraint(['label_id'], ['labels.id'], ondelete='RESTRICT', onupdate='RESTRICT', name='events_label_id_fkey'),
        ForeignKeyConstraint(['model_id'], ['models.id'], ondelete='CASCADE', onupdate='CASCADE', name='events_model_id_fkey'),
        ForeignKeyConstraint(['record_id'], ['records.id'], ondelete='CASCADE', onupdate='CASCADE', name='events_record_id_fkey'),
        PrimaryKeyConstraint('id', name='events_pkey')
    )

    id = mapped_column(BigInteger)
    model_id = mapped_column(BigInteger, nullable=False)
    record_id = mapped_column(BigInteger, nullable=False)
    label_id = mapped_column(BigInteger, nullable=False)
    start_time = mapped_column(Numeric(9, 4), nullable=False)
    end_time = mapped_column(Numeric(9, 4), nullable=False)
    channel = mapped_column(Text, nullable=False)
    confidence = mapped_column(Float, nullable=False)

    label: Mapped['Labels'] = relationship('Labels', back_populates='events')
    model: Mapped['Models'] = relationship('Models', back_populates='events')
    record: Mapped['Records'] = relationship('Records', back_populates='events')


class ModelInferenceLog(Records):
    __tablename__ = 'model_inference_log'
    __table_args__ = (
        ForeignKeyConstraint(['model_id'], ['models.id'], ondelete='CASCADE', onupdate='CASCADE', name='model_inference_log_model_id_fkey'),
        ForeignKeyConstraint(['record_id'], ['records.id'], ondelete='CASCADE', onupdate='CASCADE', name='model_inference_log_record_id_fkey'),
        PrimaryKeyConstraint('record_id', name='model_inference_log_pkey'),
        UniqueConstraint('model_id', 'record_id', name='model_inference_log_model_id_record_id_key'),
        {'comment': 'For every record analysed by and a model an entry willl be '
                'created'}
    )

    model_id = mapped_column(BigInteger, nullable=False)
    record_id = mapped_column(BigInteger)
    analyzed = mapped_column(Boolean, server_default=text('true'))

    model: Mapped['Models'] = relationship('Models', back_populates='model_inference_log')


class ModelInferenceResults(Base):
    __tablename__ = 'model_inference_results'
    __table_args__ = (
        ForeignKeyConstraint(['label_id'], ['labels.id'], ondelete='CASCADE', name='fk_label'),
        ForeignKeyConstraint(['model_id'], ['models.id'], ondelete='CASCADE', name='fk_model'),
        ForeignKeyConstraint(['record_id'], ['records.id'], ondelete='CASCADE', name='fk_record'),
        PrimaryKeyConstraint('id', name='model_inference_results_pkey'),
        Index('idx_model_id', 'model_id'),
        Index('idx_model_record', 'model_id', 'record_id')
    )

    id = mapped_column(BigInteger)
    record_id = mapped_column(BigInteger, nullable=False)
    model_id = mapped_column(Integer, nullable=False)
    label_id = mapped_column(Integer, nullable=False)
    start_time = mapped_column(Numeric(9, 4), nullable=False)
    end_time = mapped_column(Numeric(9, 4), nullable=False)
    confidence = mapped_column(Float, nullable=False)

    label: Mapped['Labels'] = relationship('Labels', back_populates='model_inference_results')
    model: Mapped['Models'] = relationship('Models', back_populates='model_inference_results')
    record: Mapped['Records'] = relationship('Records', back_populates='model_inference_results')
