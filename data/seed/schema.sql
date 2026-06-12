-- 六爻占卜网站 数据库结构 V1.0 (PostgreSQL 15)
-- 依据: 开发文档第4章. 内容表为唯一数据源头, 前端快照由 export 脚本生成
BEGIN;

CREATE TABLE trigram (
  id smallint PRIMARY KEY CHECK (id BETWEEN 1 AND 8),
  name varchar(2) NOT NULL UNIQUE,
  symbol varchar(4) NOT NULL,
  wu_xing varchar(2) NOT NULL,
  binary_code char(3) NOT NULL UNIQUE,   -- 自下而上,阳1阴0
  created_at timestamptz DEFAULT now(), updated_at timestamptz DEFAULT now()
);

CREATE TABLE hexagram (
  id smallint PRIMARY KEY CHECK (id BETWEEN 1 AND 64),  -- 通行本卦序
  name varchar(8) NOT NULL UNIQUE,
  symbol_unicode varchar(4) NOT NULL,
  upper_trigram_id smallint NOT NULL REFERENCES trigram(id),
  lower_trigram_id smallint NOT NULL REFERENCES trigram(id),
  binary_code char(6) NOT NULL UNIQUE,
  palace_trigram_id smallint NOT NULL REFERENCES trigram(id),
  palace_index smallint NOT NULL CHECK (palace_index BETWEEN 0 AND 7), -- 0本宫..6游魂7归魂
  shi_position smallint NOT NULL CHECK (shi_position BETWEEN 1 AND 6),
  ying_position smallint NOT NULL CHECK (ying_position BETWEEN 1 AND 6),
  gua_ci text,            -- 卦辞原文(公有领域通行本)
  gua_annotation text,    -- 原创白话注解
  version int NOT NULL DEFAULT 1,
  created_at timestamptz DEFAULT now(), updated_at timestamptz DEFAULT now(),
  CHECK ( (shi_position - ying_position + 6) % 6 = 3 )  -- 世应相隔两位
);

CREATE TABLE najia (
  id serial PRIMARY KEY,
  hexagram_id smallint NOT NULL REFERENCES hexagram(id),
  line_position smallint NOT NULL CHECK (line_position BETWEEN 1 AND 6),
  tian_gan char(1) NOT NULL,
  di_zhi char(1) NOT NULL,
  wu_xing char(1) NOT NULL,
  UNIQUE (hexagram_id, line_position)
);

CREATE TABLE yao_text (
  id serial PRIMARY KEY,
  hexagram_id smallint NOT NULL REFERENCES hexagram(id),
  line_position smallint NOT NULL CHECK (line_position BETWEEN 0 AND 6), -- 0=用九/用六
  yao_ci text NOT NULL,
  annotation text,
  version int NOT NULL DEFAULT 1,
  created_at timestamptz DEFAULT now(), updated_at timestamptz DEFAULT now(),
  UNIQUE (hexagram_id, line_position)
);

CREATE TABLE solar_term (
  id serial PRIMARY KEY,
  year smallint NOT NULL,
  term_name varchar(4) NOT NULL,
  exact_time timestamptz NOT NULL,   -- 精确到分钟,来源须为权威历表
  UNIQUE (year, term_name)
);

CREATE TABLE liushen_rule (
  day_gan char(1) PRIMARY KEY,
  first_liushen varchar(2) NOT NULL
);

CREATE TABLE xun_kong (
  day_ganzhi char(2) PRIMARY KEY,
  kong1 char(1) NOT NULL,
  kong2 char(1) NOT NULL
);

-- 本期不在后端写入,结构预留(开发文档4.8)
CREATE TABLE divination_record (
  uuid uuid PRIMARY KEY,
  question_category varchar(16),
  question_text text,
  yaos char(6) NOT NULL,            -- 6789记法,自初至上
  datetime_cast timestamptz NOT NULL,
  paipan_result jsonb NOT NULL,
  created_at timestamptz DEFAULT now()
);

COMMIT;
