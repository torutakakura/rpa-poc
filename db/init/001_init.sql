-- Scenario management minimal schema

create table if not exists scenarios (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  description text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists scenario_versions (
  id uuid primary key default gen_random_uuid(),
  scenario_id uuid not null references scenarios(id) on delete cascade,
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


