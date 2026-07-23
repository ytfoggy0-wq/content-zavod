create table accounts (
    id bigint generated always as identity primary key,
    username text unique not null,
    added_at timestamptz default now()
);

create table reels (
    id bigint generated always as identity primary key,
    account_id bigint references accounts(id) not null,
    reel_url text unique not null,
    shortcode text,
    video_url text,
    caption text,
    posted_at timestamptz,
    views bigint,
    likes bigint,
    comments bigint,
    duration_seconds numeric,
    transcript text,
    median_score numeric,
    collected_at timestamptz default now()
);

create index on reels (account_id);
create index on reels (median_score desc);
