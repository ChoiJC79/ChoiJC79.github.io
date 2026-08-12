-- Supabase 데이터베이스 테이블 및 RLS 보안 정책을 설정하는 SQL 스키마 정의

-- 1. 기존 테이블이 존재할 경우 삭제 (안전한 재시작을 위해)
drop table if exists columns;
drop table if exists memos;

-- 2. columns (칼럼·기고) 테이블 생성
create table columns (
  id bigint generated always as identity primary key,
  slug text unique not null,
  title text not null,
  date date not null,
  tags text[] not null,
  body text not null,
  type text not null, -- 'policy' (행정·정책·제안) 또는 'life' (에세이·일상)
  image_url text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- columns 테이블 인덱스 설정 (빠른 조회를 위해)
create index idx_columns_slug on columns(slug);
create index idx_columns_date on columns(date desc);

-- 3. memos (4대 정리노트 통합) 테이블 생성
create table memos (
  id bigint generated always as identity primary key,
  category text not null, -- 'ideas' (아이디어·기획), 'goals' (목표·계획·다짐), 'diary' (일상·감정·회고), 'work' (업무·논문·공부)
  date date not null,
  content text not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- memos 테이블 인덱스 설정
create index idx_memos_category_date on memos(category, date desc);

-- 4. Row Level Security (RLS) 보안 설정 활성화
alter table columns enable row level security;
alter table memos enable row level security;

-- 5. RLS 정책 설정 (누구나 조회는 가능하지만, 데이터 추가/수정/삭제는 차단)

-- columns 테이블 보안 정책
create policy "누구나 칼럼을 읽을 수 있습니다." 
  on columns for select 
  using (true);

create policy "인증된 사용자만 칼럼을 추가/수정/삭제할 수 있습니다." 
  on columns for all 
  using (auth.role() = 'authenticated') 
  with check (auth.role() = 'authenticated');

-- memos 테이블 보안 정책
create policy "누구나 정리노트를 읽을 수 있습니다." 
  on memos for select 
  using (true);

create policy "인증된 사용자만 정리노트를 추가/수정/삭제할 수 있습니다." 
  on memos for all 
  using (auth.role() = 'authenticated') 
  with check (auth.role() = 'authenticated');
