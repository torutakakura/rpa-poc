-- Scenario management minimal schema

create table if not exists workflows (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  description text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  is_hearing boolean not null default true,
  deleted_at timestamptz
);

create table if not exists scenario_versions (
  id uuid primary key default gen_random_uuid(),
  scenario_id uuid not null references workflows(id) on delete cascade,
  version integer not null,
  steps_json jsonb not null,
  notes text,
  created_by text,
  created_at timestamptz not null default now(),
  unique (scenario_id, version)
);

create table if not exists runs (
  id uuid primary key default gen_random_uuid(),
  scenario_version_id uuid not null references scenario_versions(id) on delete cascade,
  status text not null,
  started_at timestamptz default now(),
  finished_at timestamptz,
  logs_json jsonb,
  error text
);

-- helper extension for gen_random_uuid()
create extension if not exists pgcrypto;


-- Vector store for step catalog
create extension if not exists vector;

create table if not exists step_embeddings (
  id uuid primary key default gen_random_uuid(),
  step_key text not null,
  title text,
  description text,
  metadata jsonb,
  embedding vector(1536) not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (step_key)
);

create index if not exists step_embeddings_embedding_idx
  on step_embeddings using ivfflat (embedding vector_cosine_ops) with (lists = 100);


-- Hearing messages (linked to workflow)
create table if not exists messages (
  id uuid primary key default gen_random_uuid(),
  workflow_id uuid not null references workflows(id) on delete cascade,
  role text not null,
  content text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  deleted_at timestamptz,
  check (role in ('user', 'assistant'))
);

create index if not exists messages_workflow_id_idx on messages (workflow_id);
create index if not exists messages_workflow_id_created_at_idx on messages (workflow_id, created_at);
