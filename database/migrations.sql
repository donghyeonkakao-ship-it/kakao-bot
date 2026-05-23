-- 수집된 뉴스 캐시
create table if not exists articles (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  source text,
  url text,
  summary_3line text,
  market_impact text,
  tags text[],
  published_at timestamptz,
  created_at timestamptz default now()
);

-- 키워드-종목 관계 DB (할루시네이션 방지)
create table if not exists relations (
  id uuid primary key default gen_random_uuid(),
  keyword text not null unique,
  related_stocks text[],
  related_sectors text[]
);

-- 일일 브리핑 캐시
create table if not exists daily_briefings (
  date date primary key,
  nasdaq_summary text,
  soxx_summary text,
  top_news jsonb,
  generated_at timestamptz default now()
);

-- 기본 관계 데이터 삽입
insert into relations (keyword, related_stocks, related_sectors) values
  ('HBM',       array['SK하이닉스', '삼성전자', '마이크론'],          array['메모리반도체', 'AI가속기']),
  ('EUV',       array['ASML', 'SK하이닉스', '삼성전자', 'TSMC'],     array['파운드리', '반도체장비']),
  ('NVIDIA',    array['NVIDIA', 'SK하이닉스', '마이크론'],            array['AI가속기', 'GPU']),
  ('TSMC',      array['TSMC', 'ASML', 'Applied Materials'],          array['파운드리']),
  ('데이터센터', array['NVIDIA', 'AMD', 'Intel', 'SK하이닉스'],       array['AI인프라', '서버']),
  ('ASIC',      array['브로드컴', 'Marvell', 'TSMC'],                array['AI가속기', '커스텀칩']),
  ('HBM3E',     array['SK하이닉스', '마이크론'],                      array['메모리반도체']),
  ('CoWoS',     array['TSMC', 'ASE Group'],                          array['첨단패키징'])
on conflict (keyword) do nothing;
