CREATE ROLE ROLE_READ_ONLY;
GRANT CONNECT TO ROLE_READ_ONLY;
CREATE USER USER1 IDENTIFIED BY "123456";
GRANT ROLE_READ_ONLY TO USER1;


-- ============================================================
-- TABLES
-- ============================================================

CREATE TABLE "users" (
  "user_id"       varchar(36) PRIMARY KEY,
  "username"      varchar(100) UNIQUE NOT NULL,
  "password_hash" varchar(255) NOT NULL,
  "full_name"     varchar(150),
  "email"         varchar(150) UNIQUE,
  "is_active"     number(1) DEFAULT 1 NOT NULL,
  "created_at"    timestamp NOT NULL,
  "updated_at"    timestamp
);

CREATE TABLE "roles" (
  "role_id"   number GENERATED AS IDENTITY PRIMARY KEY,
  "role_name" varchar(50) UNIQUE NOT NULL
);

CREATE TABLE "user_roles" (
  "user_id"     varchar(36) NOT NULL,
  "role_id"     number NOT NULL,
  "assigned_at" timestamp NOT NULL,
  PRIMARY KEY ("user_id", "role_id")
);

CREATE TABLE "customers" (
  "customer_id"     varchar(36) PRIMARY KEY,
  "customer_code"   varchar(50) UNIQUE,
  "kyc_status"      varchar(20),
  "full_name"       varchar(150),
  "identity_card"   varchar(50) UNIQUE,
  "address"         varchar(255),
  "city"            varchar(100),
  "state"           varchar(50),
  "zip_code"        varchar(20),
  "gender"          varchar(10),
  "date_of_birth"   date,
  "job"             varchar(150),
  "latitude"        decimal(9,6),
  "longitude"       decimal(9,6),
  "city_population" number,
  "income_level"    varchar(50),
  "created_at"      timestamp NOT NULL
);

CREATE TABLE "merchants" (
  "merchant_id"       varchar(36) PRIMARY KEY,
  "merchant_code"     varchar(50) UNIQUE NOT NULL,
  "merchant_name"     varchar(150) NOT NULL,
  "merchant_category" varchar(100),
  "city"              varchar(100),
  "state"             varchar(50),
  "country"           varchar(100),
  "latitude"          decimal(9,6),
  "longitude"         decimal(9,6),
  "risk_level"        varchar(20),
  "is_blacklisted"    number(1) DEFAULT 0 NOT NULL,
  "created_at"        timestamp NOT NULL
);

CREATE TABLE "channels" (
  "channel_id"   number GENERATED AS IDENTITY PRIMARY KEY,
  "channel_code" varchar(50) UNIQUE NOT NULL,
  "channel_name" varchar(100) NOT NULL
);

CREATE TABLE "transactions_live" (
  "txn_id"             varchar(36) PRIMARY KEY,
  "customer_id"        varchar(36) NOT NULL,
  "merchant_id"        varchar(36) NOT NULL,
  "channel_id"         number NOT NULL,
  "submitted_by"       varchar(36) NOT NULL,
  "card_number_masked" varchar(30),
  "card_number_hash"   varchar(64),
  "amount"             decimal(18,2) NOT NULL,
  "currency_code"      varchar(10) DEFAULT 'USD' NOT NULL,
  "txn_time"           timestamp NOT NULL,
  "status"             varchar(20) NOT NULL,
  "fraud_score"        decimal(6,4),
  "reason_code"        varchar(50),
  "override_reason"    varchar(50),
  "source_ip"          varchar(64),
  "merch_lat"          decimal(9,6),
  "merch_long"         decimal(9,6),
  "unix_time"          number,
  "created_at"         timestamp NOT NULL,
  "updated_at"         timestamp,
  CONSTRAINT chk_txn_amount      CHECK ("amount" > 0),
  CONSTRAINT chk_txn_fraud_score CHECK ("fraud_score" IS NULL OR "fraud_score" BETWEEN 0 AND 1),
  CONSTRAINT chk_txn_status      CHECK ("status" IN ('PENDING','APPROVED','REJECTED','MANUAL_REVIEW'))
);

CREATE TABLE "risk_scoring_results" (
  "score_id"              varchar(36) PRIMARY KEY,
  "txn_id"                varchar(36) NOT NULL,
  "model_version"         varchar(50),
  "fraud_score"           decimal(6,4) NOT NULL,
  "decision_suggested"    varchar(20),
  "reason_json"           CLOB,
  "reject_threshold"      decimal(6,4),
  "review_threshold"      decimal(6,4),
  "feature_snapshot_json" CLOB,
  "score_time"            timestamp NOT NULL,
  CONSTRAINT chk_scoring_fraud CHECK ("fraud_score" BETWEEN 0 AND 1)
);

CREATE TABLE "rule_hits" (
  "rule_hit_id" varchar(36) PRIMARY KEY,
  "txn_id"      varchar(36) NOT NULL,
  "rule_code"   varchar(50) NOT NULL,
  "rule_name"   varchar(150),
  "hit_value"   varchar(255),
  "severity"    varchar(20),
  "created_at"  timestamp NOT NULL
);

CREATE TABLE "review_cases" (
  "case_id"       varchar(36) PRIMARY KEY,
  "txn_id"        varchar(36) UNIQUE NOT NULL,
  "case_status"   varchar(20) NOT NULL,
  "assigned_to"   varchar(36),
  "decision"      varchar(20),
  "decision_note" varchar(2000),
  "version"       number DEFAULT 1 NOT NULL,
  "created_at"    timestamp NOT NULL,
  "decided_at"    timestamp,
  CONSTRAINT chk_case_status CHECK ("case_status" IN ('OPEN','ASSIGNED','APPROVED','REJECTED','CLOSED'))
);

CREATE TABLE "review_case_actions" (
  "action_id"     varchar(36) PRIMARY KEY,
  "case_id"       varchar(36) NOT NULL,
  "action_type"   varchar(30) NOT NULL,
  "actor_user_id" varchar(36) NOT NULL,
  "action_note"   varchar(500),
  "created_at"    timestamp NOT NULL
);

CREATE TABLE "txn_idempotency" (
  "idempotency_key"       varchar(100) PRIMARY KEY,
  "txn_hash"              varchar(128),
  "txn_id"                varchar(36),
  "status"                varchar(20) NOT NULL,
  "response_snapshot_json" varchar(4000),
  "created_at"            timestamp NOT NULL,
  "updated_at"            timestamp,
  CONSTRAINT chk_idem_status CHECK ("status" IN ('IN_PROGRESS','SUCCESS','FAILED'))
);

CREATE TABLE "txn_state" (
  "txn_id"            varchar(36) PRIMARY KEY,
  "status"            varchar(20) NOT NULL,
  "last_update"       timestamp DEFAULT SYSTIMESTAMP NOT NULL,
  "reason_code"       varchar(50),
  "retry_count"       number DEFAULT 0 NOT NULL,
  "last_error_code"   varchar(50),
  "last_error_message" varchar(500),
  "version"           number DEFAULT 1 NOT NULL,
  CONSTRAINT chk_txn_state_status CHECK ("status" IN ('PENDING','APPROVED','REJECTED','MANUAL_REVIEW'))
);

CREATE TABLE "txn_state_history" (
  "state_hist_id"     varchar(36) PRIMARY KEY,
  "txn_id"            varchar(36) NOT NULL,
  "old_status"        varchar(20),
  "new_status"        varchar(20) NOT NULL,
  "changed_by_user_id" varchar(36),
  "changed_at"        timestamp NOT NULL,
  "change_reason"     varchar(200)
);

CREATE TABLE "reconciliation_runs" (
  "run_id"                  varchar(36) PRIMARY KEY,
  "period_start"            timestamp NOT NULL,
  "period_end"              timestamp NOT NULL,
  "status"                  varchar(20) NOT NULL,
  "total_txn_count"         number,
  "matched_count"           number,
  "discrepancy_count"       number,
  "total_amount"            decimal(18,2),
  "pending_timeout_minutes" number DEFAULT 120 NOT NULL,
  "error_message"           varchar(500),
  "triggered_by"            varchar(36),
  "completed_at"            timestamp,
  "created_at"              timestamp NOT NULL,
  CONSTRAINT chk_recon_run_status CHECK ("status" IN ('RUNNING','COMPLETED','FAILED'))
);

CREATE TABLE "reconciliation_items" (
  "item_id"         varchar(36) PRIMARY KEY,
  "run_id"          varchar(36) NOT NULL,
  "txn_id"          varchar(36),
  "item_type"       varchar(50) NOT NULL,
  "txn_status"      varchar(20),
  "txn_amount"      decimal(18,2),
  "txn_created_at"  timestamp,
  "minutes_pending" number,
  "status"          varchar(20) DEFAULT 'OPEN' NOT NULL,
  "resolution_note" varchar(500),
  "resolved_by"     varchar(36),
  "resolved_at"     timestamp,
  "created_at"      timestamp NOT NULL,
  CONSTRAINT chk_recon_item_status CHECK ("status" IN ('OPEN','RESOLVED'))
);

CREATE TABLE "datalake_snapshots" (
  "snapshot_id"   varchar(36) PRIMARY KEY,
  "snapshot_type" varchar(50) NOT NULL,
  "snapshot_date" date NOT NULL,
  "job_id"        varchar(36),
  "source_label"  varchar(100),
  "record_count"  number DEFAULT 0 NOT NULL,
  "total_amount"  decimal(18,2),
  "data_json"     CLOB,
  "status"        varchar(20) DEFAULT 'ACTIVE' NOT NULL,
  "created_at"    timestamp NOT NULL,
  CONSTRAINT chk_datalake_status CHECK ("status" IN ('ACTIVE','ARCHIVED'))
);

CREATE TABLE "card_velocity_stats" (
  "card_hash"      varchar(64) PRIMARY KEY,
  "avg_daily_txn"  decimal(8,2) DEFAULT 0 NOT NULL,
  "total_txn"      number DEFAULT 0 NOT NULL,
  "avg_amt"        decimal(12,2) DEFAULT 0 NOT NULL,
  "std_amt"        decimal(12,2) DEFAULT 0 NOT NULL,
  "m2_amt"         decimal(20,4) DEFAULT 0 NOT NULL,
  "distinct_days"  number DEFAULT 1 NOT NULL,
  "last_txn_date"  varchar(10),
  "last_updated"   timestamp DEFAULT SYSTIMESTAMP NOT NULL
);

CREATE TABLE "dim_time" (
  "time_id"     number PRIMARY KEY,
  "full_date"   date UNIQUE NOT NULL,
  "day_num"     number NOT NULL,
  "month_num"   number NOT NULL,
  "year_num"    number NOT NULL,
  "quarter_num" number NOT NULL,
  "is_weekend"  number(1) NOT NULL
);

CREATE TABLE "dim_customer" (
  "customer_key" number GENERATED AS IDENTITY PRIMARY KEY,
  "customer_id"  varchar(36) UNIQUE NOT NULL,
  "segment"      varchar(50),
  "risk_level"   varchar(20),
  "city"         varchar(100),
  "country"      varchar(100)
);

CREATE TABLE "dim_merchant" (
  "merchant_key"      number GENERATED AS IDENTITY PRIMARY KEY,
  "merchant_id"       varchar(36) UNIQUE NOT NULL,
  "merchant_code"     varchar(50),
  "merchant_name"     varchar(150),
  "merchant_category" varchar(100),
  "city"              varchar(100),
  "country"           varchar(100),
  "risk_level"        varchar(20)
);

CREATE TABLE "dim_channel" (
  "channel_key"  number GENERATED AS IDENTITY PRIMARY KEY,
  "channel_id"   number UNIQUE NOT NULL,
  "channel_code" varchar(50),
  "channel_name" varchar(100)
);

CREATE TABLE "dim_location" (
  "location_key" number GENERATED AS IDENTITY PRIMARY KEY,
  "source_ip"    varchar(64),
  "city"         varchar(100),
  "district"     varchar(100),
  "country"      varchar(100)
);

CREATE TABLE "fact_transactions" (
  "fact_id"            varchar(36) PRIMARY KEY,
  "txn_id"             varchar(36) UNIQUE NOT NULL,
  "time_id"            number NOT NULL,
  "customer_key"       number NOT NULL,
  "merchant_key"       number NOT NULL,
  "channel_key"        number NOT NULL,
  "location_key"       number,
  "amount"             decimal(18,2) NOT NULL,
  "final_status"       varchar(20) NOT NULL,
  "fraud_label"        number(1),
  "manual_review_flag" number(1) DEFAULT 0 NOT NULL,
  "fraud_score"        decimal(6,4),
  "processing_time_ms" number,
  "model_version"      varchar(50),
  "load_ts"            timestamp NOT NULL
);

CREATE TABLE "fact_loans" (
  "fact_loan_id"     varchar(36) PRIMARY KEY,
  "loan_id"          varchar(36) UNIQUE NOT NULL,
  "time_id"          number NOT NULL,
  "customer_key"     number NOT NULL,
  "requested_amount" decimal(18,2) NOT NULL,
  "final_status"     varchar(20) NOT NULL,
  "pd_score"         decimal(6,4),
  "model_version"    varchar(50),
  "load_ts"          timestamp NOT NULL
);

CREATE TABLE "audit_logs" (
  "log_id"        varchar(36) PRIMARY KEY,
  "event_type"    varchar(50) NOT NULL,
  "entity_type"   varchar(50) NOT NULL,
  "entity_id"     varchar(36) NOT NULL,
  "actor_user_id" varchar(36),
  "actor_name"    varchar(150),
  "event_ts"      timestamp NOT NULL,
  "detail_json"   CLOB
);

CREATE TABLE "etl_logs" (
  "job_id"       varchar(36) PRIMARY KEY,
  "job_type"     varchar(50) NOT NULL,
  "target_date"  date NOT NULL,
  "status"       varchar(20) NOT NULL,
  "records_in"   number,
  "records_out"  number,
  "error_message" varchar(500),
  "triggered_by" varchar(36),
  "started_at"   timestamp DEFAULT SYSTIMESTAMP NOT NULL,
  "completed_at" timestamp,
  "created_at"   timestamp NOT NULL,
  CONSTRAINT chk_etl_status CHECK ("status" IN ('RUNNING','SUCCESS','FAILED'))
);

-- ============================================================
-- ANALYST MODULE (v1.3)
-- ============================================================

CREATE TABLE "loans" (
  "loan_id"                    varchar(36) PRIMARY KEY,
  "customer_id"                varchar(36) NOT NULL,
  "submitted_by"               varchar(36) NOT NULL,
  "reviewed_by"                varchar(36),
  "principal_amount"           decimal(18,2) NOT NULL,
  "currency_code"              varchar(10) DEFAULT 'USD' NOT NULL,
  "interest_rate"              decimal(6,4) NOT NULL,
  "term_months"                number NOT NULL,
  "purpose"                    varchar(200),
  "status"                     varchar(20) NOT NULL,
  "version"                    number DEFAULT 1 NOT NULL,
  "review_note"                varchar(500),
  "reviewed_at"                timestamp,
  "monthly_payment"            decimal(18,2),
  "outstanding_balance"        decimal(18,2),
  "disbursed_at"               timestamp,
  "maturity_date"              date,
  "person_age"                 number,
  "person_income"              decimal(18,2),
  "person_home_ownership"      varchar(20),
  "person_emp_length"          number,
  "loan_grade"                 varchar(2),
  "loan_intent"                varchar(30),
  "cb_person_default_on_file"  varchar(1),
  "cb_person_cred_hist_length" number,
  "pd_score"                   decimal(6,4),
  "risk_level"                 varchar(20),
  "created_at"                 timestamp NOT NULL,
  "updated_at"                 timestamp,
  CONSTRAINT chk_loan_amount        CHECK ("principal_amount" > 0),
  CONSTRAINT chk_loan_interest_rate CHECK ("interest_rate" > 0 AND "interest_rate" < 100),
  CONSTRAINT chk_loan_pd_score      CHECK ("pd_score" IS NULL OR "pd_score" BETWEEN 0 AND 1),
  CONSTRAINT chk_loan_status        CHECK ("status" IN ('PENDING','APPROVED','REJECTED','DISBURSED','CLOSED','DEFAULTED'))
);

CREATE TABLE "model_configs" (
  "config_id"   number GENERATED AS IDENTITY PRIMARY KEY,
  "model_name"  varchar(50) NOT NULL,
  "param_name"  varchar(100) NOT NULL,
  "param_value" decimal(10,6) NOT NULL,
  "description" varchar(255),
  "updated_by"  varchar(36),
  "updated_at"  timestamp DEFAULT SYSTIMESTAMP NOT NULL,
  "version"     number DEFAULT 1 NOT NULL,
  CONSTRAINT uq_model_configs_name_param UNIQUE ("model_name", "param_name")
);

CREATE TABLE "suppression_rules" (
  "rule_id"    varchar(36) PRIMARY KEY,
  "rule_type"  varchar(20) NOT NULL,
  "entity_id"  varchar(255) NOT NULL,
  "reason"     CLOB NOT NULL,
  "created_by" varchar(36) NOT NULL,
  "expires_at" timestamp,
  "is_active"  number(1) DEFAULT 1 NOT NULL,
  "created_at" timestamp NOT NULL,
  CONSTRAINT chk_supp_rule_type CHECK ("rule_type" IN ('MERCHANT','CUSTOMER','CARD_HASH'))
);

CREATE TABLE "analyst_reports" (
  "report_id"       varchar(36) PRIMARY KEY,
  "title"           varchar(255) NOT NULL,
  "report_type"     varchar(50) NOT NULL,
  "content_md"      CLOB NOT NULL,
  "status"          varchar(20) NOT NULL,
  "submitted_by"    varchar(36) NOT NULL,
  "submitted_at"    timestamp NOT NULL,
  "acknowledged_by" varchar(36),
  "acknowledged_at" timestamp,
  "note"            varchar(1000),
  CONSTRAINT chk_report_status CHECK ("status" IN ('PENDING_REVIEW','ACKNOWLEDGED','ARCHIVED'))
);

-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX idx_transactions_status  ON "transactions_live" ("status");
CREATE INDEX idx_txn_live_time        ON "transactions_live" ("txn_time");
CREATE INDEX idx_txn_live_cust        ON "transactions_live" ("customer_id");
CREATE INDEX idx_txn_live_merch       ON "transactions_live" ("merchant_id");
CREATE INDEX idx_txn_live_chan        ON "transactions_live" ("channel_id");
CREATE INDEX idx_txn_live_card_hash   ON "transactions_live" ("card_number_hash");
CREATE INDEX idx_risk_txn_id          ON "risk_scoring_results" ("txn_id");
CREATE INDEX idx_risk_score_time      ON "risk_scoring_results" ("score_time");
CREATE INDEX idx_recon_run_status     ON "reconciliation_runs" ("status");
CREATE INDEX idx_recon_item_run       ON "reconciliation_items" ("run_id");
CREATE INDEX idx_recon_item_txn       ON "reconciliation_items" ("txn_id");
CREATE INDEX idx_recon_item_status    ON "reconciliation_items" ("status");
CREATE INDEX idx_datalake_type        ON "datalake_snapshots" ("snapshot_type");
CREATE INDEX idx_datalake_date        ON "datalake_snapshots" ("snapshot_date");
CREATE INDEX idx_datalake_status      ON "datalake_snapshots" ("status");
CREATE INDEX idx_etl_logs_type        ON "etl_logs" ("job_type");
CREATE INDEX idx_etl_logs_date        ON "etl_logs" ("target_date");
CREATE INDEX idx_etl_logs_status      ON "etl_logs" ("status");
CREATE INDEX idx_loans_status         ON "loans" ("status");
CREATE INDEX idx_loans_customer       ON "loans" ("customer_id");
CREATE INDEX idx_loans_submitted      ON "loans" ("submitted_by");
CREATE INDEX idx_suppression_active   ON "suppression_rules" ("is_active");
CREATE INDEX idx_suppression_type_eid ON "suppression_rules" ("rule_type", "entity_id");
CREATE INDEX idx_analyst_reports_status ON "analyst_reports" ("status");
CREATE INDEX idx_analyst_reports_by     ON "analyst_reports" ("submitted_by");
CREATE INDEX idx_txn_live_submitted     ON "transactions_live" ("submitted_by");
CREATE INDEX idx_case_status            ON "review_cases" ("case_status");
CREATE INDEX idx_case_assigned          ON "review_cases" ("assigned_to");
CREATE INDEX idx_audit_event_type       ON "audit_logs" ("event_type");
CREATE INDEX idx_audit_entity_id        ON "audit_logs" ("entity_id");
CREATE INDEX idx_audit_event_ts         ON "audit_logs" ("event_ts");
CREATE INDEX idx_rule_hits_code         ON "rule_hits" ("rule_code");
CREATE INDEX idx_supp_expires           ON "suppression_rules" ("expires_at");

-- ============================================================
-- COMMENTS
-- ============================================================

COMMENT ON COLUMN "users"."user_id" IS 'UUID';
COMMENT ON COLUMN "customers"."customer_id" IS 'UUID';
COMMENT ON COLUMN "merchants"."merchant_id" IS 'UUID';
COMMENT ON COLUMN "transactions_live"."txn_id" IS 'UUID';
COMMENT ON COLUMN "transactions_live"."status" IS 'PENDING|APPROVED|REJECTED|MANUAL_REVIEW';
COMMENT ON COLUMN "transactions_live"."card_number_hash" IS 'SHA256 hash của số thẻ — không lưu số thẻ raw';
COMMENT ON COLUMN "transactions_live"."currency_code" IS 'ISO 4217, default USD';
COMMENT ON COLUMN "risk_scoring_results"."score_id" IS 'UUID';
COMMENT ON COLUMN "risk_scoring_results"."reject_threshold" IS 'Ngưỡng REJECT tại thời điểm score — lấy từ model_configs';
COMMENT ON COLUMN "risk_scoring_results"."review_threshold" IS 'Ngưỡng MANUAL_REVIEW tại thời điểm score';
COMMENT ON COLUMN "rule_hits"."rule_hit_id" IS 'UUID';
COMMENT ON COLUMN "review_cases"."case_id" IS 'UUID';
COMMENT ON COLUMN "review_cases"."case_status" IS 'OPEN|ASSIGNED|APPROVED|REJECTED|CLOSED';
COMMENT ON COLUMN "review_cases"."version" IS 'Optimistic Locking — tăng mỗi lần cập nhật';
COMMENT ON COLUMN "review_case_actions"."action_id" IS 'UUID';
COMMENT ON COLUMN "review_case_actions"."action_type" IS 'ASSIGN|COMMENT|APPROVE|REJECT|REOPEN';
COMMENT ON COLUMN "txn_idempotency"."status" IS 'IN_PROGRESS|SUCCESS|FAILED';
COMMENT ON COLUMN "txn_state_history"."state_hist_id" IS 'UUID';
COMMENT ON COLUMN "reconciliation_runs"."run_id" IS 'UUID';
COMMENT ON COLUMN "reconciliation_runs"."status" IS 'RUNNING|COMPLETED|FAILED';
COMMENT ON COLUMN "reconciliation_items"."item_id" IS 'UUID';
COMMENT ON COLUMN "reconciliation_items"."item_type" IS 'PENDING_TIMEOUT';
COMMENT ON COLUMN "reconciliation_items"."status" IS 'OPEN|RESOLVED';
COMMENT ON COLUMN "datalake_snapshots"."snapshot_id" IS 'UUID';
COMMENT ON COLUMN "datalake_snapshots"."snapshot_type" IS 'DAILY_TXN_SUMMARY|EXTERNAL_INGEST';
COMMENT ON COLUMN "datalake_snapshots"."status" IS 'ACTIVE|ARCHIVED';
COMMENT ON COLUMN "card_velocity_stats"."card_hash" IS 'SHA256 hash — PK, không lưu số thẻ raw';
COMMENT ON COLUMN "card_velocity_stats"."m2_amt" IS 'Welford algorithm M2 — dùng tính std online';
COMMENT ON COLUMN "fact_transactions"."fact_id" IS 'UUID';
COMMENT ON COLUMN "fact_loans"."fact_loan_id" IS 'UUID';
COMMENT ON COLUMN "fact_loans"."loan_id" IS 'FK → loans.loan_id';
COMMENT ON COLUMN "audit_logs"."log_id" IS 'UUID';
COMMENT ON COLUMN "etl_logs"."job_type" IS 'DAILY_SUMMARY';
COMMENT ON COLUMN "etl_logs"."status" IS 'RUNNING|SUCCESS|FAILED';
COMMENT ON TABLE  "loans" IS 'OLTP khoản vay (v1.3) — thay thế loan_applications';
COMMENT ON COLUMN "loans"."loan_id" IS 'UUID';
COMMENT ON COLUMN "loans"."status" IS 'PENDING|APPROVED|REJECTED|DISBURSED|CLOSED|DEFAULTED';
COMMENT ON COLUMN "loans"."version" IS 'Optimistic Locking';
COMMENT ON TABLE  "model_configs" IS 'Ngưỡng phân loại Fraud/PD Score — ANALYST điều chỉnh, không hardcode';
COMMENT ON COLUMN "model_configs"."model_name" IS '"fraud" | "loan"';
COMMENT ON COLUMN "model_configs"."param_name" IS '"reject_threshold" | "review_threshold" | "risk_high_threshold" | "risk_medium_threshold"';
COMMENT ON TABLE  "suppression_rules" IS 'Whitelist bypass fraud scoring — ANALYST quản lý';
COMMENT ON COLUMN "suppression_rules"."rule_id" IS 'UUID';
COMMENT ON COLUMN "suppression_rules"."rule_type" IS 'MERCHANT | CUSTOMER | CARD_HASH';
COMMENT ON COLUMN "suppression_rules"."is_active" IS '1 = active, 0 = vô hiệu hóa';
COMMENT ON TABLE  "analyst_reports" IS 'Báo cáo phân tích rủi ro định kỳ — ANALYST tạo, MANAGER acknowledge';
COMMENT ON COLUMN "analyst_reports"."report_id" IS 'UUID';
COMMENT ON COLUMN "analyst_reports"."report_type" IS 'FRAUD_ANALYSIS|LOAN_ANALYSIS|THRESHOLD_RECOMMENDATION|SUPPRESSION_REVIEW|GENERAL';
COMMENT ON COLUMN "analyst_reports"."status" IS 'PENDING_REVIEW|ACKNOWLEDGED|ARCHIVED';

-- ============================================================
-- FOREIGN KEYS
-- ============================================================

ALTER TABLE "user_roles" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("user_id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "user_roles" ADD FOREIGN KEY ("role_id") REFERENCES "roles" ("role_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "transactions_live" ADD FOREIGN KEY ("customer_id")  REFERENCES "customers" ("customer_id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "transactions_live" ADD FOREIGN KEY ("merchant_id")  REFERENCES "merchants" ("merchant_id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "transactions_live" ADD FOREIGN KEY ("channel_id")   REFERENCES "channels"  ("channel_id")  DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "transactions_live" ADD FOREIGN KEY ("submitted_by") REFERENCES "users"     ("user_id")     DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "risk_scoring_results" ADD FOREIGN KEY ("txn_id") REFERENCES "transactions_live" ("txn_id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "rule_hits"            ADD FOREIGN KEY ("txn_id") REFERENCES "transactions_live" ("txn_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "review_cases"         ADD FOREIGN KEY ("txn_id")      REFERENCES "transactions_live" ("txn_id")   DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "review_cases"         ADD FOREIGN KEY ("assigned_to") REFERENCES "users"             ("user_id")  DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "review_case_actions"  ADD FOREIGN KEY ("case_id")     REFERENCES "review_cases"      ("case_id")  DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "review_case_actions"  ADD FOREIGN KEY ("actor_user_id") REFERENCES "users"           ("user_id")  DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "txn_idempotency"   ADD FOREIGN KEY ("txn_id") REFERENCES "transactions_live" ("txn_id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "txn_state"         ADD FOREIGN KEY ("txn_id") REFERENCES "transactions_live" ("txn_id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "txn_state_history" ADD FOREIGN KEY ("txn_id")              REFERENCES "transactions_live" ("txn_id")  DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "txn_state_history" ADD FOREIGN KEY ("changed_by_user_id")  REFERENCES "users"             ("user_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "reconciliation_runs"  ADD FOREIGN KEY ("triggered_by") REFERENCES "users"                ("user_id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "reconciliation_items" ADD FOREIGN KEY ("run_id")       REFERENCES "reconciliation_runs"  ("run_id")  DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "reconciliation_items" ADD FOREIGN KEY ("txn_id")       REFERENCES "transactions_live"    ("txn_id")  DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "reconciliation_items" ADD FOREIGN KEY ("resolved_by")  REFERENCES "users"                ("user_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "etl_logs"          ADD FOREIGN KEY ("triggered_by") REFERENCES "users"     ("user_id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "datalake_snapshots" ADD FOREIGN KEY ("job_id")      REFERENCES "etl_logs"  ("job_id")  DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "fact_transactions" ADD FOREIGN KEY ("time_id")       REFERENCES "dim_time"     ("time_id")      DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "fact_transactions" ADD FOREIGN KEY ("customer_key")  REFERENCES "dim_customer" ("customer_key") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "fact_transactions" ADD FOREIGN KEY ("merchant_key")  REFERENCES "dim_merchant" ("merchant_key") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "fact_transactions" ADD FOREIGN KEY ("channel_key")   REFERENCES "dim_channel"  ("channel_key")  DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "fact_transactions" ADD FOREIGN KEY ("location_key")  REFERENCES "dim_location" ("location_key") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "fact_loans" ADD FOREIGN KEY ("time_id")      REFERENCES "dim_time"     ("time_id")      DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "fact_loans" ADD FOREIGN KEY ("customer_key") REFERENCES "dim_customer" ("customer_key") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "fact_loans" ADD FOREIGN KEY ("loan_id")      REFERENCES "loans"        ("loan_id")      DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "audit_logs" ADD FOREIGN KEY ("actor_user_id") REFERENCES "users" ("user_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "loans" ADD FOREIGN KEY ("customer_id")  REFERENCES "customers" ("customer_id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "loans" ADD FOREIGN KEY ("submitted_by") REFERENCES "users"     ("user_id")     DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "loans" ADD FOREIGN KEY ("reviewed_by")  REFERENCES "users"     ("user_id")     DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "model_configs"     ADD FOREIGN KEY ("updated_by")      REFERENCES "users" ("user_id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "suppression_rules" ADD FOREIGN KEY ("created_by")      REFERENCES "users" ("user_id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "analyst_reports"   ADD FOREIGN KEY ("submitted_by")    REFERENCES "users" ("user_id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "analyst_reports"   ADD FOREIGN KEY ("acknowledged_by") REFERENCES "users" ("user_id") DEFERRABLE INITIALLY IMMEDIATE;

-- ============================================================
-- PROCEDURES
-- ============================================================

-- Procedure: PROC_SUBMIT_TRANSACTION
-- Mục đích: Khởi tạo giao dịch mới với cơ chế chống trùng lặp (Idempotency)
CREATE OR REPLACE PROCEDURE PROC_SUBMIT_TRANSACTION (
    p_idempotency_key  IN varchar2,
    p_txn_id           IN varchar2,
    p_customer_id      IN varchar2,
    p_merchant_id      IN varchar2,
    p_channel_id       IN number,
    p_amount           IN number,
    p_currency_code    IN varchar2,
    p_fraud_score      IN number,
    p_txn_time         IN timestamp,
    p_submitted_by     IN varchar2,
    p_card_number_hash IN varchar2,
    -- OUT params
    p_out_txn_id   OUT varchar2,
    p_out_status   OUT varchar2
) AS
    v_existing_status varchar2(20);
    v_existing_txn_id varchar2(36);
BEGIN
    -- B1 & B2: Check Idempotency
    BEGIN
        SELECT "txn_id", "status"
        INTO v_existing_txn_id, v_existing_status
        FROM "txn_idempotency"
        WHERE "idempotency_key" = p_idempotency_key;

        p_out_txn_id := v_existing_txn_id;
        p_out_status := v_existing_status;
        RETURN;
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            NULL;
    END;

    -- B3: Insert vào transactions_live
    INSERT INTO "transactions_live" (
        "txn_id", "customer_id", "merchant_id", "channel_id",
        "submitted_by", "card_number_hash",
        "amount", "currency_code", "txn_time", "status", "fraud_score", "created_at"
    ) VALUES (
        p_txn_id, p_customer_id, p_merchant_id, p_channel_id,
        p_submitted_by, p_card_number_hash,
        p_amount, NVL(p_currency_code, 'USD'), NVL(p_txn_time, SYSTIMESTAMP), 'PENDING', p_fraud_score, SYSTIMESTAMP
    );

    -- B4: Insert vào txn_state (version = 1)
    INSERT INTO "txn_state" (
        "txn_id", "status", "last_update", "version", "retry_count"
    ) VALUES (
        p_txn_id, 'PENDING', SYSTIMESTAMP, 1, 0
    );

    -- B5: Insert vào txn_idempotency
    INSERT INTO "txn_idempotency" (
        "idempotency_key", "txn_id", "status", "created_at"
    ) VALUES (
        p_idempotency_key, p_txn_id, 'PENDING', SYSTIMESTAMP
    );

    p_out_txn_id := p_txn_id;
    p_out_status := 'PENDING';

    COMMIT;

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE_APPLICATION_ERROR(-20001, 'ERR_DB_01: Lỗi CSDL khi submit giao dịch - ' || SQLERRM);
END;
/

-- Procedure: PROC_PROCESS_REVIEW_CASE
-- Mục đích: Duyệt hoặc từ chối giao dịch MANUAL_REVIEW
CREATE OR REPLACE PROCEDURE PROC_PROCESS_REVIEW_CASE (
    p_case_id       IN varchar2,
    p_decision      IN varchar2,
    p_decision_note IN varchar2,
    p_out_status    OUT varchar2
) AS
    v_txn_id         varchar2(36);
    v_case_status    varchar2(20);
    v_new_txn_status varchar2(20);
BEGIN
    BEGIN
        SELECT "txn_id", "case_status"
        INTO v_txn_id, v_case_status
        FROM "review_cases"
        WHERE "case_id" = p_case_id
        FOR UPDATE;
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            RAISE_APPLICATION_ERROR(-20002, 'ERR_CASE_00: Không tìm thấy Case');
    END;

    IF v_case_status NOT IN ('OPEN', 'ASSIGNED') THEN
        RAISE_APPLICATION_ERROR(-20003, 'ERR_CASE_01: Case đã được xử lý hoặc đã đóng.');
    END IF;

    IF p_decision = 'APPROVE' THEN
        v_new_txn_status := 'APPROVED';
    ELSIF p_decision = 'REJECT' THEN
        v_new_txn_status := 'REJECTED';
    ELSE
        RAISE_APPLICATION_ERROR(-20004, 'ERR_CASE_02: Decision không hợp lệ, chỉ nhận APPROVE hoặc REJECT.');
    END IF;

    UPDATE "review_cases"
    SET "case_status"   = 'CLOSED',
        "decision"      = p_decision,
        "decision_note" = p_decision_note,
        "version"       = "version" + 1,
        "decided_at"    = SYSTIMESTAMP
    WHERE "case_id" = p_case_id;

    UPDATE "transactions_live"
    SET "status"     = v_new_txn_status,
        "updated_at" = SYSTIMESTAMP
    WHERE "txn_id" = v_txn_id;

    p_out_status := v_new_txn_status;

    COMMIT;

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE;
END;
/

-- Procedure: PROC_EXECUTE_RECONCILIATION
-- Mục đích: Phát hiện giao dịch stuck PENDING quá lâu trong một khoảng thời gian,
--           ghi kết quả vào reconciliation_runs + reconciliation_items
CREATE OR REPLACE PROCEDURE PROC_EXECUTE_RECONCILIATION (
    p_run_id                  IN varchar2,
    p_period_start            IN timestamp,
    p_period_end              IN timestamp,
    p_pending_timeout_minutes IN number,
    p_triggered_by            IN varchar2,
    p_out_status              OUT varchar2
) AS
    v_total_count   number := 0;
    v_matched_count number := 0;
    v_disc_count    number := 0;
    v_total_amount  decimal(18,2) := 0;
BEGIN
    -- B1: Khởi tạo reconciliation run
    INSERT INTO "reconciliation_runs" (
        "run_id", "period_start", "period_end", "status",
        "pending_timeout_minutes", "triggered_by", "created_at"
    ) VALUES (
        p_run_id, p_period_start, p_period_end, 'RUNNING',
        NVL(p_pending_timeout_minutes, 120), p_triggered_by, SYSTIMESTAMP
    );

    -- B2: Tính tổng giao dịch trong khoảng thời gian
    SELECT COUNT("txn_id"), NVL(SUM("amount"), 0)
    INTO v_total_count, v_total_amount
    FROM "transactions_live"
    WHERE "txn_time" BETWEEN p_period_start AND p_period_end;

    -- B3: Phát hiện giao dịch PENDING vượt quá pending_timeout_minutes
    FOR rec IN (
        SELECT t."txn_id", t."status", t."amount", t."created_at",
               ROUND((SYSTIMESTAMP - t."created_at") * 24 * 60, 0) AS minutes_pending
        FROM "transactions_live" t
        WHERE t."txn_time" BETWEEN p_period_start AND p_period_end
          AND t."status" = 'PENDING'
          AND (SYSTIMESTAMP - t."created_at") * 24 * 60 > NVL(p_pending_timeout_minutes, 120)
    ) LOOP
        INSERT INTO "reconciliation_items" (
            "item_id", "run_id", "txn_id", "item_type",
            "txn_status", "txn_amount", "txn_created_at", "minutes_pending",
            "status", "created_at"
        ) VALUES (
            SYS_GUID(), p_run_id, rec."txn_id", 'PENDING_TIMEOUT',
            rec."status", rec."amount", rec."created_at", rec.minutes_pending,
            'OPEN', SYSTIMESTAMP
        );
        v_disc_count := v_disc_count + 1;
    END LOOP;

    v_matched_count := v_total_count - v_disc_count;

    -- B4: Cập nhật kết quả
    UPDATE "reconciliation_runs"
    SET "status"            = 'COMPLETED',
        "total_txn_count"   = v_total_count,
        "matched_count"     = v_matched_count,
        "discrepancy_count" = v_disc_count,
        "total_amount"      = v_total_amount,
        "completed_at"      = SYSTIMESTAMP
    WHERE "run_id" = p_run_id;

    COMMIT;
    p_out_status := 'COMPLETED';

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        BEGIN
            UPDATE "reconciliation_runs"
            SET "status"        = 'FAILED',
                "error_message" = SUBSTR(SQLERRM, 1, 500),
                "completed_at"  = SYSTIMESTAMP
            WHERE "run_id" = p_run_id;
            COMMIT;
        EXCEPTION
            WHEN OTHERS THEN ROLLBACK;
        END;
        p_out_status := 'FAILED';
        RAISE;
END;
/

-- ============================================================
-- TRIGGERS
-- ============================================================

CREATE OR REPLACE TRIGGER TRG_DETECT_HIGH_VALUE
BEFORE INSERT ON "transactions_live"
FOR EACH ROW
BEGIN
    IF :NEW."amount" > 500000000 THEN
        :NEW."status" := 'MANUAL_REVIEW';
    END IF;
END;
/

CREATE OR REPLACE TRIGGER TRG_AUTO_CREATE_CASE
AFTER INSERT OR UPDATE ON "transactions_live"
FOR EACH ROW
BEGIN
    IF :NEW."status" = 'MANUAL_REVIEW' THEN
        IF INSERTING OR (UPDATING AND NVL(:OLD."status", '') <> 'MANUAL_REVIEW') THEN
            INSERT INTO "review_cases" (
                "case_id", "txn_id", "case_status", "created_at"
            ) VALUES (
                SYS_GUID(), :NEW."txn_id", 'OPEN', SYSTIMESTAMP
            );
        END IF;
    END IF;
END;
/

CREATE OR REPLACE TRIGGER TRG_OPTIMISTIC_LOCK_CHECK
BEFORE UPDATE ON "txn_state"
FOR EACH ROW
BEGIN
    IF :NEW."version" <> :OLD."version" THEN
        RAISE_APPLICATION_ERROR(-20001, 'Data modified by another user');
    END IF;
END;
/

CREATE OR REPLACE TRIGGER TRG_STATE_VERSION_UP
BEFORE UPDATE ON "txn_state"
FOR EACH ROW
BEGIN
    IF :NEW."status" <> :OLD."status" THEN
        :NEW."version" := :OLD."version" + 1;
    END IF;
END;
/

CREATE OR REPLACE TRIGGER TRG_LOG_STATUS_CHANGE
AFTER UPDATE ON "transactions_live"
FOR EACH ROW
BEGIN
    IF :OLD."status" <> :NEW."status" THEN
        INSERT INTO "txn_state_history" (
            "state_hist_id", "txn_id", "old_status", "new_status", "changed_at"
        ) VALUES (
            SYS_GUID(), :NEW."txn_id", :OLD."status", :NEW."status", SYSTIMESTAMP
        );
    END IF;
END;
/
