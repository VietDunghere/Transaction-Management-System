CREATE ROLE ROLE_READ_ONLY;
GRANT CONNECT TO ROLE_READ_ONLY;
CREATE USER USER1 IDENTIFIED BY "123456";
GRANT ROLE_READ_ONLY TO USER1;


CREATE TABLE "users" (
  "user_id" varchar(36) PRIMARY KEY,
  "username" varchar(100) UNIQUE NOT NULL,
  "password_hash" varchar(255) NOT NULL,
  "full_name" varchar(150),
  "email" varchar(150) UNIQUE,
  "is_active" number(1) DEFAULT 1 NOT NULL,
  "created_at" timestamp NOT NULL,
  "updated_at" timestamp                  -- Thêm: theo dõi lần cuối đổi role/password
);

CREATE TABLE "roles" (
  "role_id" number GENERATED AS IDENTITY PRIMARY KEY,
  "role_name" varchar(50) UNIQUE NOT NULL
);

CREATE TABLE "user_roles" (
  "user_id" varchar(36) NOT NULL,
  "role_id" number NOT NULL,
  "assigned_at" timestamp NOT NULL,
  PRIMARY KEY ("user_id", "role_id")
);

CREATE TABLE "customers" (
  "customer_id" varchar(36) PRIMARY KEY,
  "customer_code" varchar(50) UNIQUE,
  "kyc_status" varchar(20),
  "full_name" varchar(150),
  "identity_card" varchar(50) UNIQUE,
  "address" varchar(255),
  "income_level" varchar(50),
  "created_at" timestamp NOT NULL
);

CREATE TABLE "merchants" (
  "merchant_id" varchar(36) PRIMARY KEY,
  "merchant_code" varchar(50) UNIQUE NOT NULL,
  "merchant_name" varchar(150) NOT NULL,
  "merchant_category" varchar(100),
  "city" varchar(100),
  "country" varchar(100),
  "risk_level" varchar(20),
  "is_blacklisted" number(1) DEFAULT 0 NOT NULL,
  "created_at" timestamp NOT NULL
);

CREATE TABLE "channels" (
  "channel_id" number GENERATED AS IDENTITY PRIMARY KEY,
  "channel_code" varchar(50) UNIQUE NOT NULL,
  "channel_name" varchar(100) NOT NULL
);

CREATE TABLE "transactions_live" (
  "txn_id" varchar(36) PRIMARY KEY,
  "customer_id" varchar(36) NOT NULL,
  "merchant_id" varchar(36) NOT NULL,
  "channel_id" number NOT NULL,
  "submitted_by" varchar(36) NOT NULL,    -- Thêm: user_id của OPERATOR gửi giao dịch (dùng filter phân quyền)
  "card_number_masked" varchar(30),
  "amount" decimal(18,2) NOT NULL,
  "currency_code" varchar(10) DEFAULT 'VND' NOT NULL,
  "txn_time" timestamp NOT NULL,
  "status" varchar(20) NOT NULL,
  "fraud_score" decimal(6,4),
  "reason_code" varchar(50),              -- Lý do từ AI Model (VD: HIGH_FRAUD_SCORE)
  "override_reason" varchar(50),          -- Thêm: Lý do hệ thống ghi đè (VD: HIGH_VALUE)
  "source_ip" varchar(64),
  "created_at" timestamp NOT NULL,
  "updated_at" timestamp
);

CREATE TABLE "risk_scoring_results" (
  "score_id" varchar(36) PRIMARY KEY,
  "txn_id" varchar(36) NOT NULL,
  "model_version" varchar(50),
  "fraud_score" decimal(6,4) NOT NULL,
  "decision_suggested" varchar(20),
  "reason_json" varchar(4000),
  "score_time" timestamp NOT NULL
);

CREATE TABLE "rule_hits" (
  "rule_hit_id" varchar(36) PRIMARY KEY,
  "txn_id" varchar(36) NOT NULL,
  "rule_code" varchar(50) NOT NULL,
  "rule_name" varchar(150),
  "hit_value" varchar(255),
  "severity" varchar(20),
  "created_at" timestamp NOT NULL
);

CREATE TABLE "review_cases" (
  "case_id" varchar(36) PRIMARY KEY,
  "txn_id" varchar(36) UNIQUE NOT NULL,
  "case_status" varchar(20) NOT NULL,
  "assigned_to" varchar(36),
  "decision" varchar(20),
  "decision_note" varchar(2000),          -- Tăng: 500→2000 cho ghi chú nghiệp vụ dài
  "version" number DEFAULT 1 NOT NULL,    -- Thêm: Optimistic Locking, tăng mỗi khi có thay đổi
  "created_at" timestamp NOT NULL,
  "decided_at" timestamp
);

CREATE TABLE "review_case_actions" (
  "action_id" varchar(36) PRIMARY KEY,
  "case_id" varchar(36) NOT NULL,
  "action_type" varchar(30) NOT NULL,
  "actor_user_id" varchar(36) NOT NULL,
  "action_note" varchar(500),
  "created_at" timestamp NOT NULL
);

CREATE TABLE "txn_idempotency" (
  "idempotency_key" varchar(100) PRIMARY KEY, -- Đổi tên: idem_key→idempotency_key (nhất quán API)
  "txn_hash" varchar(128),
  "txn_id" varchar(36),
  "status" varchar(20) NOT NULL,
  "response_snapshot_json" varchar(4000),
  "created_at" timestamp NOT NULL,
  "updated_at" timestamp
);

CREATE TABLE "txn_state" (
  "txn_id" varchar(36) PRIMARY KEY,
  "status" varchar(20) NOT NULL,
  "last_update" timestamp NOT NULL,
  "reason_code" varchar(50),
  "retry_count" number DEFAULT 0 NOT NULL,
  "last_error_code" varchar(50),
  "last_error_message" varchar(500),
  "version" number DEFAULT 1 NOT NULL
);

CREATE TABLE "txn_state_history" (
  "state_hist_id" varchar(36) PRIMARY KEY,
  "txn_id" varchar(36) NOT NULL,
  "old_status" varchar(20),
  "new_status" varchar(20) NOT NULL,
  "changed_by_user_id" varchar(36),
  "changed_at" timestamp NOT NULL,
  "change_reason" varchar(200)
);

CREATE TABLE "reconciliation_jobs" (
  "job_id" varchar(36) PRIMARY KEY,
  "biz_date" date NOT NULL,
  "source_name" varchar(50) NOT NULL,
  "expected_count" number,
  "actual_count" number,
  "expected_amount" decimal(18,2),
  "actual_amount" decimal(18,2),
  "status" varchar(20) NOT NULL,          -- PENDING|MATCHED|MISMATCH|FAILED
  "error_message" varchar(1000),          -- Thêm: Lý do chi tiết khi status=FAILED
  "created_at" timestamp NOT NULL,
  "completed_at" timestamp
);

CREATE TABLE "reconciliation_items" (
  "item_id" varchar(36) PRIMARY KEY,
  "job_id" varchar(36) NOT NULL,
  "ref_key" varchar(100),
  "issue_type" varchar(50) NOT NULL,
  "expected_value" varchar(255),
  "actual_value" varchar(255),
  "created_at" timestamp NOT NULL
);

CREATE TABLE "raw_ingest_batches" (
  "batch_id" varchar(36) PRIMARY KEY,
  "file_path" varchar(500) NOT NULL,
  "file_date" date NOT NULL,
  "record_count" number,
  "ingest_status" varchar(20) NOT NULL,
  "error_message" varchar(500),
  "created_at" timestamp NOT NULL,
  "completed_at" timestamp
);

CREATE TABLE "dim_time" (
  "time_id" number PRIMARY KEY,
  "full_date" date UNIQUE NOT NULL,
  "day_num" number NOT NULL,
  "month_num" number NOT NULL,
  "year_num" number NOT NULL,
  "quarter_num" number NOT NULL,
  "is_weekend" number(1) NOT NULL
);

CREATE TABLE "dim_customer" (
  "customer_key" number GENERATED AS IDENTITY PRIMARY KEY,
  "customer_id" varchar(36) UNIQUE NOT NULL,
  "segment" varchar(50),
  "risk_level" varchar(20),
  "city" varchar(100),
  "country" varchar(100)
);

CREATE TABLE "dim_merchant" (
  "merchant_key" number GENERATED AS IDENTITY PRIMARY KEY,
  "merchant_id" varchar(36) UNIQUE NOT NULL,
  "merchant_code" varchar(50),
  "merchant_name" varchar(150),
  "merchant_category" varchar(100),
  "city" varchar(100),
  "country" varchar(100),
  "risk_level" varchar(20)
);

CREATE TABLE "dim_channel" (
  "channel_key" number GENERATED AS IDENTITY PRIMARY KEY,
  "channel_id" number UNIQUE NOT NULL,
  "channel_code" varchar(50),
  "channel_name" varchar(100)
);

CREATE TABLE "dim_location" (
  "location_key" number GENERATED AS IDENTITY PRIMARY KEY,
  "source_ip" varchar(64),
  "city" varchar(100),
  "district" varchar(100),
  "country" varchar(100)
);

CREATE TABLE "fact_transactions" (
  "fact_id" varchar(36) PRIMARY KEY,
  "txn_id" varchar(36) UNIQUE NOT NULL,
  "time_id" number NOT NULL,
  "customer_key" number NOT NULL,
  "merchant_key" number NOT NULL,
  "channel_key" number NOT NULL,
  "location_key" number,
  "amount" decimal(18,2) NOT NULL,
  "final_status" varchar(20) NOT NULL,
  "fraud_label" number(1),
  "manual_review_flag" number(1) DEFAULT 0 NOT NULL,
  "fraud_score" decimal(6,4),
  "processing_time_ms" number,
  "model_version" varchar(50),
  "load_ts" timestamp NOT NULL
);

CREATE TABLE "fact_loans" (
  "fact_loan_id" varchar(36) PRIMARY KEY,
  "app_id" varchar(36) UNIQUE NOT NULL,
  "time_id" number NOT NULL,
  "customer_key" number NOT NULL,
  "requested_amount" decimal(18,2) NOT NULL,
  "final_status" varchar(20) NOT NULL,
  "pd_score" decimal(6,4),
  "model_version" varchar(50),
  "load_ts" timestamp NOT NULL
);

CREATE TABLE "loan_applications" (
  "app_id" varchar(36) PRIMARY KEY,
  "customer_id" varchar(36) NOT NULL,
  "requested_amount" decimal(18,2) NOT NULL,
  "status" varchar(20) NOT NULL,          -- SUBMITTED|SCORING|APPROVED|REJECTED|MANUAL_REVIEW
  "pd_score" decimal(6,4),               -- Thêm: Kết quả AI điểm rủi ro vỡ nợ (cache tránh join)
  "risk_level" varchar(20),              -- Thêm: LOW|MEDIUM|HIGH (cache tránh join)
  "created_at" timestamp NOT NULL,
  "decided_at" timestamp
);

CREATE TABLE "loan_feature_snapshots" (
  "snapshot_id" varchar(36) PRIMARY KEY,
  "app_id" varchar(36) UNIQUE NOT NULL,
  "annual_income" decimal(18,2),
  "employment_years" number,
  "debt_to_income_ratio" decimal(8,4),
  "credit_score" number,
  "prior_default_count" number,
  "requested_term_months" number,
  "feature_json" varchar(4000),
  "created_at" timestamp NOT NULL
);

CREATE TABLE "loan_risk_scores" (
  "score_id" varchar(36) PRIMARY KEY,
  "app_id" varchar(36) NOT NULL,
  "pd_score" decimal(6,4) NOT NULL,
  "model_version" varchar(50) NOT NULL,
  "score_time" timestamp NOT NULL,
  "reason_json" varchar(4000)
);

CREATE TABLE "audit_logs" (
  "log_id" varchar(36) PRIMARY KEY,
  "event_type" varchar(50) NOT NULL,
  "entity_type" varchar(50) NOT NULL,
  "entity_id" varchar(36) NOT NULL,
  "actor_user_id" varchar(36),
  "actor_name" varchar(150),
  "event_ts" timestamp NOT NULL,
  "detail_json" varchar(4000)
);

-- Bảng ETL Job Logs (Thêm mới: theo dõi toàn bộ pipeline Extract→Transform→Load)
CREATE TABLE "etl_job_logs" (
  "job_id" varchar(36) PRIMARY KEY,
  "triggered_by" varchar(36),             -- user_id của ADMIN kích hoạt, NULL nếu chạy tự động
  "mode" varchar(20) NOT NULL,            -- FULL|INCREMENTAL
  "biz_date" date NOT NULL,               -- Ngày dữ liệu được xử lý
  "status" varchar(20) NOT NULL,          -- RUNNING|SUCCESS|FAILED
  "records_extracted" number DEFAULT 0,
  "records_transformed" number DEFAULT 0,
  "records_loaded" number DEFAULT 0,
  "error_message" varchar(1000),          -- Chi tiết lỗi nếu FAILED
  "started_at" timestamp NOT NULL,
  "completed_at" timestamp
);

CREATE INDEX idx_transactions_status ON "transactions_live" ("status");

CREATE INDEX idx_txn_live_time ON "transactions_live" ("txn_time");

CREATE INDEX idx_txn_live_cust ON "transactions_live" ("customer_id");

CREATE INDEX idx_txn_live_merch ON "transactions_live" ("merchant_id");

CREATE INDEX idx_txn_live_chan ON "transactions_live" ("channel_id");

CREATE INDEX idx_risk_txn_id ON "risk_scoring_results" ("txn_id");

CREATE INDEX idx_risk_score_time ON "risk_scoring_results" ("score_time");

COMMENT ON COLUMN "users"."user_id" IS 'UUID';

COMMENT ON COLUMN "customers"."customer_id" IS 'UUID';

COMMENT ON COLUMN "merchants"."merchant_id" IS 'UUID';

COMMENT ON COLUMN "transactions_live"."txn_id" IS 'UUID';

COMMENT ON COLUMN "transactions_live"."status" IS 'PENDING|APPROVED|REJECTED|MANUAL_REVIEW';

COMMENT ON COLUMN "risk_scoring_results"."score_id" IS 'UUID';

COMMENT ON COLUMN "rule_hits"."rule_hit_id" IS 'UUID';

COMMENT ON COLUMN "review_cases"."case_id" IS 'UUID';

COMMENT ON COLUMN "review_cases"."case_status" IS 'OPEN|ASSIGNED|APPROVED|REJECTED|CLOSED';

COMMENT ON COLUMN "review_case_actions"."action_id" IS 'UUID';

COMMENT ON COLUMN "review_case_actions"."action_type" IS 'ASSIGN|COMMENT|APPROVE|REJECT|REOPEN';

COMMENT ON COLUMN "txn_idempotency"."status" IS 'IN_PROGRESS|SUCCESS|FAILED';

COMMENT ON COLUMN "txn_state_history"."state_hist_id" IS 'UUID';

COMMENT ON COLUMN "reconciliation_jobs"."job_id" IS 'UUID';

COMMENT ON COLUMN "reconciliation_jobs"."status" IS 'PENDING|MATCHED|MISMATCH|FAILED';

COMMENT ON COLUMN "reconciliation_items"."item_id" IS 'UUID';

COMMENT ON COLUMN "raw_ingest_batches"."batch_id" IS 'UUID';

COMMENT ON COLUMN "raw_ingest_batches"."ingest_status" IS 'PENDING|SUCCESS|FAILED';

COMMENT ON COLUMN "fact_transactions"."fact_id" IS 'UUID';

COMMENT ON COLUMN "fact_loans"."fact_loan_id" IS 'UUID';

COMMENT ON COLUMN "loan_applications"."app_id" IS 'UUID';

COMMENT ON COLUMN "loan_applications"."status" IS 'SUBMITTED|SCORING|APPROVED|REJECTED|MANUAL_REVIEW';

COMMENT ON COLUMN "loan_feature_snapshots"."snapshot_id" IS 'UUID';

COMMENT ON COLUMN "loan_risk_scores"."score_id" IS 'UUID';

COMMENT ON COLUMN "audit_logs"."log_id" IS 'UUID';

ALTER TABLE "loan_applications" ADD FOREIGN KEY ("customer_id") REFERENCES "customers" ("customer_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "loan_feature_snapshots" ADD FOREIGN KEY ("app_id") REFERENCES "loan_applications" ("app_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "loan_risk_scores" ADD FOREIGN KEY ("app_id") REFERENCES "loan_applications" ("app_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "fact_transactions" ADD FOREIGN KEY ("time_id") REFERENCES "dim_time" ("time_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "fact_transactions" ADD FOREIGN KEY ("customer_key") REFERENCES "dim_customer" ("customer_key") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "fact_transactions" ADD FOREIGN KEY ("merchant_key") REFERENCES "dim_merchant" ("merchant_key") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "fact_transactions" ADD FOREIGN KEY ("channel_key") REFERENCES "dim_channel" ("channel_key") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "fact_transactions" ADD FOREIGN KEY ("location_key") REFERENCES "dim_location" ("location_key") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "fact_loans" ADD FOREIGN KEY ("time_id") REFERENCES "dim_time" ("time_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "fact_loans" ADD FOREIGN KEY ("customer_key") REFERENCES "dim_customer" ("customer_key") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "user_roles" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("user_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "user_roles" ADD FOREIGN KEY ("role_id") REFERENCES "roles" ("role_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "transactions_live" ADD FOREIGN KEY ("customer_id") REFERENCES "customers" ("customer_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "transactions_live" ADD FOREIGN KEY ("merchant_id") REFERENCES "merchants" ("merchant_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "transactions_live" ADD FOREIGN KEY ("channel_id") REFERENCES "channels" ("channel_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "risk_scoring_results" ADD FOREIGN KEY ("txn_id") REFERENCES "transactions_live" ("txn_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "rule_hits" ADD FOREIGN KEY ("txn_id") REFERENCES "transactions_live" ("txn_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "review_cases" ADD FOREIGN KEY ("txn_id") REFERENCES "transactions_live" ("txn_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "review_cases" ADD FOREIGN KEY ("assigned_to") REFERENCES "users" ("user_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "review_case_actions" ADD FOREIGN KEY ("case_id") REFERENCES "review_cases" ("case_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "review_case_actions" ADD FOREIGN KEY ("actor_user_id") REFERENCES "users" ("user_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "audit_logs" ADD FOREIGN KEY ("actor_user_id") REFERENCES "users" ("user_id") DEFERRABLE INITIALLY IMMEDIATE;

-- FK mới: submitted_by trong transactions_live → users
ALTER TABLE "transactions_live" ADD FOREIGN KEY ("submitted_by") REFERENCES "users" ("user_id") DEFERRABLE INITIALLY IMMEDIATE;

-- FK mới: triggered_by trong etl_job_logs → users
ALTER TABLE "etl_job_logs" ADD FOREIGN KEY ("triggered_by") REFERENCES "users" ("user_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "txn_idempotency" ADD FOREIGN KEY ("txn_id") REFERENCES "transactions_live" ("txn_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "txn_state" ADD FOREIGN KEY ("txn_id") REFERENCES "transactions_live" ("txn_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "txn_state_history" ADD FOREIGN KEY ("txn_id") REFERENCES "transactions_live" ("txn_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "txn_state_history" ADD FOREIGN KEY ("changed_by_user_id") REFERENCES "users" ("user_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "reconciliation_items" ADD FOREIGN KEY ("job_id") REFERENCES "reconciliation_jobs" ("job_id") DEFERRABLE INITIALLY IMMEDIATE;
