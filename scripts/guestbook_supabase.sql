-- 방명록(guestbook.html)이 쓰는 Supabase 테이블과 공개 읽기·쓰기 정책 (SQL Editor에서 한 번 실행)
create table if not exists public.guestbook (
  id         bigint generated always as identity primary key,
  name       text not null check (char_length(name) between 1 and 30),
  content    text not null check (char_length(content) between 1 and 500),
  created_at timestamptz not null default now()
);

alter table public.guestbook enable row level security;

drop policy if exists "guestbook read" on public.guestbook;
create policy "guestbook read" on public.guestbook
  for select to anon, authenticated using (true);

drop policy if exists "guestbook insert" on public.guestbook;
create policy "guestbook insert" on public.guestbook
  for insert to anon, authenticated with check (true);

grant select, insert on public.guestbook to anon, authenticated;
