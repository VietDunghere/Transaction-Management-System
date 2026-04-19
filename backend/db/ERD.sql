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


ALTER TABLE "customers" ADD (
  "gender"   varchar(10),   
  "dob"      date,              
  "job"      varchar(150),      
  "lat"      decimal(10,7),     
  "long"     decimal(10,7),      
  "city_pop" number              
);



ALTER TABLE "merchants" ADD (
  "lat"  decimal(10,7),         
  "long" decimal(10,7)           
);


ALTER TABLE "transactions_live" ADD (
  "merch_lat"  decimal(10,7),    
  "merch_long" decimal(10,7),   
  "unix_time"  number           
);

-- ============================================================
-- PROCEDURES & TRIGGERS
-- ============================================================

-- Procedure: PROC_SUBMIT_TRANSACTION
-- Mục đích: Khởi tạo một giao dịch mới với cơ chế chống trùng lặp (Idempotency)
CREATE OR REPLACE PROCEDURE PROC_SUBMIT_TRANSACTION (
    p_idem_key           IN varchar2,
    p_txn_id             IN varchar2,
    p_customer_id        IN varchar2,
    p_merchant_id        IN varchar2,
    p_channel_id         IN number,
    p_amount             IN number,
    p_currency_code      IN varchar2,
    p_fraud_score        IN number,
    p_txn_time           IN timestamp,
    -- OUT params
    p_out_txn_id         OUT varchar2,
    p_out_status         OUT varchar2
) AS
    v_existing_status varchar2(20);
    v_existing_txn_id varchar2(36);
BEGIN
    -- B1 & B2: Check Idempotency (Kiểm tra trong txn_idempotency)
    BEGIN
        SELECT "txn_id", "status" 
        INTO v_existing_txn_id, v_existing_status
        FROM "txn_idempotency"
        WHERE "idem_key" = p_idem_key;
        
        -- Nếu đã tồn tại key, nhảy sang trả về kết quả cũ
        p_out_txn_id := v_existing_txn_id;
        p_out_status := v_existing_status;
        RETURN;
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            NULL; -- Tiếp tục nếu chưa có idem_key
    END;

    -- B3: Insert vào transactions_live với status = 'PENDING'
    INSERT INTO "transactions_live" (
        "txn_id", "customer_id", "merchant_id", "channel_id", "amount", 
        "currency_code", "txn_time", "status", "fraud_score", "created_at"
    ) VALUES (
        p_txn_id, p_customer_id, p_merchant_id, p_channel_id, p_amount, 
        NVL(p_currency_code, 'VND'), NVL(p_txn_time, SYSTIMESTAMP), 'PENDING', p_fraud_score, SYSTIMESTAMP
    );

    -- B4: Insert vào txn_state khởi tạo version = 1
    INSERT INTO "txn_state" (
        "txn_id", "status", "last_update", "version", "retry_count"
    ) VALUES (
        p_txn_id, 'PENDING', SYSTIMESTAMP, 1, 0
    );

    -- B5: Insert vào txn_idempotency để chốt khóa chống trùng
    INSERT INTO "txn_idempotency" (
        "idem_key", "txn_id", "status", "created_at"
    ) VALUES (
        p_idem_key, p_txn_id, 'PENDING', SYSTIMESTAMP
    );

    -- Gán kết quả trả về
    p_out_txn_id := p_txn_id;
    p_out_status := 'PENDING';

    -- B6: Commit giao dịch (ACID)
    COMMIT;

EXCEPTION
    WHEN OTHERS THEN
        -- Ngoại lệ: Lỗi DB -> ROLLBACK và ném lỗi ERR_DB_01
        ROLLBACK;
        RAISE_APPLICATION_ERROR(-20001, 'ERR_DB_01: Lỗi CSDL khi submit giao dịch - ' || SQLERRM);
END;
/

-- Procedure: PROC_PROCESS_REVIEW_CASE
-- Mục đích: Duyệt hoặc từ chối giao dịch cần Manual Review
CREATE OR REPLACE PROCEDURE PROC_PROCESS_REVIEW_CASE (
    p_case_id            IN varchar2,
    p_decision           IN varchar2, -- 'APPROVE' hoặc 'REJECT'
    p_decision_note      IN varchar2,
    -- OUT params
    p_out_status         OUT varchar2
) AS
    v_txn_id             varchar2(36);
    v_case_status        varchar2(20);
    v_new_txn_status     varchar2(20);
BEGIN
    -- B1 & B2: Lấy txn_id, case_status từ review_cases với Lock dòng (FOR UPDATE) 
    -- để tránh Race Condition nếu nhiều user cùng duyệt 1 case
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

    -- Kiểm tra ngoại lệ nếu case đã xử lý
    IF v_case_status NOT IN ('OPEN', 'ASSIGNED') THEN
        RAISE_APPLICATION_ERROR(-20003, 'ERR_CASE_01: Case đã được xử lý bởi người khác hoặc đã đóng.');
    END IF;

    -- Xác định status mới cho transaction
    IF p_decision = 'APPROVE' THEN
        v_new_txn_status := 'APPROVED';
    ELSIF p_decision = 'REJECT' THEN
        v_new_txn_status := 'REJECTED';
    ELSE
        RAISE_APPLICATION_ERROR(-20004, 'ERR_CASE_02: Quyết định (decision) không hợp lệ, chỉ nhận APPROVE hoặc REJECT.');
    END IF;

    -- B3: Cập nhật lại review_cases sang 'CLOSED'
    UPDATE "review_cases"
    SET "case_status" = 'CLOSED',
        "decision" = p_decision,
        "decision_note" = p_decision_note,
        "decided_at" = SYSTIMESTAMP
    WHERE "case_id" = p_case_id;

    -- B4: Cập nhật status của transactions_live
    UPDATE "transactions_live"
    SET "status" = v_new_txn_status,
        "updated_at" = SYSTIMESTAMP
    WHERE "txn_id" = v_txn_id;

    -- Gán status trả về
    p_out_status := v_new_txn_status;

    -- B5: Cập nhật thành công, gọi COMMIT (Trigger sẽ tự lo việc update txn_state & audit_logs)
    COMMIT;

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE; -- Ném lỗi ra ngoài (bao gồm cả các exception khai báo ở trên)
END;
/

-- Procedure: PROC_EXECUTE_RECONCILIATION
-- Mục đích: Đối soát dữ liệu giao dịch giữa OLTP (transactions_live), DWH (fact_transactions) và Data Lake (raw_ingest_batches)
CREATE OR REPLACE PROCEDURE PROC_EXECUTE_RECONCILIATION (
    p_job_id       IN varchar2,
    p_biz_date     IN date,
    p_source_name  IN varchar2,
    p_out_status   OUT varchar2
) AS
    v_live_count   number := 0;
    v_live_amount  decimal(18,2) := 0;
    v_dw_count     number := 0;
    v_dw_amount    decimal(18,2) := 0;
    v_raw_count    number := 0;
    v_match_status varchar2(20);
    v_time_id      number;
BEGIN
    -- B1: Tính tổng COUNT và SUM(amount) trong transactions_live cho ngày biz_date
    SELECT COUNT("txn_id"), NVL(SUM("amount"), 0)
    INTO v_live_count, v_live_amount
    FROM "transactions_live"
    WHERE TRUNC("txn_time") = TRUNC(p_biz_date);

    -- B2: Truy vấn fact_transactions để lấy số lượng tương ứng trong Warehouse
    BEGIN
        SELECT "time_id" INTO v_time_id
        FROM "dim_time"
        WHERE "full_date" = TRUNC(p_biz_date);
        
        SELECT COUNT("fact_id"), NVL(SUM("amount"), 0)
        INTO v_dw_count, v_dw_amount
        FROM "fact_transactions"
        WHERE "time_id" = v_time_id;
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            v_dw_count := 0;
            v_dw_amount := 0;
    END;

    -- B3: Truy vấn raw_ingest_batches để lấy số lượng từ Data Lake
    SELECT NVL(SUM("record_count"), 0)
    INTO v_raw_count
    FROM "raw_ingest_batches"
    WHERE "file_date" = TRUNC(p_biz_date)
      AND "ingest_status" = 'SUCCESS';

    -- Ngoại lệ: Nếu Warehouse chưa load xong (có phát sinh ở live/raw nhưng dw không có), coi như timeout/mismatch nặng
    IF (v_live_count > 0 OR v_raw_count > 0) AND v_dw_count = 0 THEN
        RAISE_APPLICATION_ERROR(-20005, 'ERR_RECON_01: Dữ liệu Warehouse chưa load xong hoặc Timeout.');
    END IF;

    -- B4: So sánh thông tin
    IF v_live_count = v_dw_count AND v_live_amount = v_dw_amount AND v_live_count = v_raw_count THEN
        v_match_status := 'MATCHED';
    ELSE
        v_match_status := 'MISMATCH';
    END IF;

    -- Insert vào reconciliation_jobs
    INSERT INTO "reconciliation_jobs" (
        "job_id", "biz_date", "source_name", "expected_count", "actual_count",
        "expected_amount", "actual_amount", "status", "created_at", "completed_at"
    ) VALUES (
        p_job_id, TRUNC(p_biz_date), NVL(p_source_name, 'SYSTEM'), v_live_count, v_dw_count,
        v_live_amount, v_dw_amount, v_match_status, SYSTIMESTAMP, SYSTIMESTAMP
    );

    -- Nếu lệch số liệu -> Ghi chi tiết vào reconciliation_items
    IF v_match_status = 'MISMATCH' THEN
        INSERT INTO "reconciliation_items" (
            "item_id", "job_id", "issue_type", "expected_value", "actual_value", "created_at"
        ) VALUES (
            SYS_GUID(), p_job_id, 'COUNT_OR_AMOUNT_MISMATCH',
            'Live: ' || v_live_count || ' reqs, Amt: ' || v_live_amount || ' | Raw: ' || v_raw_count || ' reqs',
            'DW: ' || v_dw_count || ' reqs, Amt: ' || v_dw_amount,
            SYSTIMESTAMP
        );
    END IF;

    COMMIT;
    p_out_status := v_match_status;

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        
        -- Ghi trạng thái FAILED lưu lại quá trình đối soát
        BEGIN
            INSERT INTO "reconciliation_jobs" (
                "job_id", "biz_date", "source_name", "status", "created_at", "completed_at"
            ) VALUES (
                p_job_id, TRUNC(p_biz_date), NVL(p_source_name, 'SYSTEM'), 'FAILED', SYSTIMESTAMP, SYSTIMESTAMP
            );
            COMMIT;
        EXCEPTION
            WHEN OTHERS THEN
                ROLLBACK;
        END;
        
        p_out_status := 'FAILED';
        RAISE;
END;
/

-- ============================================================
-- Trigger: TRG_DETECT_HIGH_VALUE
-- Mục đích: Hard Rule - Ép giao dịch lớn hơn 500 triệu (VND) phải vào trạng thái MANUAL_REVIEW
-- trước khi chèn vào database, không cho API / App được phép bỏ qua.
-- ============================================================
CREATE OR REPLACE TRIGGER TRG_DETECT_HIGH_VALUE
BEFORE INSERT ON "transactions_live"
FOR EACH ROW
BEGIN
    -- Nếu cột amount > 500M, ép status của dòng mới đổi sang 'MANUAL_REVIEW'
    IF :NEW."amount" > 500000000 THEN
        :NEW."status" := 'MANUAL_REVIEW';
    END IF;
END;
/

-- ============================================================
-- Trigger: TRG_AUTO_CREATE_CASE
-- Mục đích: Tự động tạo hồ sơ chờ xử lý (Review Case) để chuyển luồng (Workflow Routing)
-- ============================================================
CREATE OR REPLACE TRIGGER TRG_AUTO_CREATE_CASE
AFTER INSERT OR UPDATE ON "transactions_live"
FOR EACH ROW
BEGIN
    IF :NEW."status" = 'MANUAL_REVIEW' THEN
        -- Kiểm tra xem là lệnh INSERT mới hay lệnh UPDATE đổi status cũ từ khác thành MANUAL_REVIEW
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

-- ============================================================
-- Trigger: TRG_OPTIMISTIC_LOCK_CHECK
-- Mục đích: Ngăn chặn lỗi ghi đè dữ liệu (Race Condition) với Optimistic Locking
-- ============================================================
CREATE OR REPLACE TRIGGER TRG_OPTIMISTIC_LOCK_CHECK
BEFORE UPDATE ON "txn_state"
FOR EACH ROW
BEGIN
    -- Nếu ứng dụng truyền lên version khác với hiện tại, nghĩa là dữ liệu đã cũ
    IF :NEW."version" <> :OLD."version" THEN
        RAISE_APPLICATION_ERROR(-20001, 'Data modified by another user');
    END IF;
END;
/

-- ============================================================
-- Trigger: TRG_STATE_VERSION_UP
-- Mục đích: Tự động tăng version khi có sự thay đổi trạng thái
-- ============================================================
CREATE OR REPLACE TRIGGER TRG_STATE_VERSION_UP
BEFORE UPDATE ON "txn_state"
FOR EACH ROW
BEGIN
    IF :NEW."status" <> :OLD."status" THEN
        :NEW."version" := :OLD."version" + 1;
    END IF;
END;
/

-- ============================================================
-- Trigger: TRG_LOG_STATUS_CHANGE
-- Mục đích: Ghi log lịch sử mọi thay đổi trạng thái giao dịch để đảm bảo tính minh bạch (Auditability)
-- ============================================================
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


-- ============================================================
-- ANALYST MODULE — SCHEMA ADDITIONS (v1.3 — 2026-04-19)
-- ============================================================

-- ---- Cột mới trong risk_scoring_results ----
ALTER TABLE "risk_scoring_results" ADD (
  "reject_threshold"       decimal(6,4),        -- Ngưỡng REJECT tại thời điểm score (lấy từ model_configs)
  "review_threshold"       decimal(6,4),        -- Ngưỡng MANUAL_REVIEW tại thời điểm score
  "feature_snapshot_json"  CLOB                 -- Feature vector đã dùng — phục vụ audit & retraining
);

-- reason_json nâng cấp từ varchar(4000) → CLOB (lớn hơn khi có nhiều top_features)
ALTER TABLE "risk_scoring_results" MODIFY "reason_json" CLOB;

-- ---- Bảng loans (thay thế loan_applications trong OLTP) ----
-- loan_applications giữ lại cho DWH backward-compat; OLTP mới dùng loans
CREATE TABLE "loans" (
  "loan_id"                    varchar(36) PRIMARY KEY,
  "customer_id"                varchar(36) NOT NULL,
  "submitted_by"               varchar(36) NOT NULL,    -- OPERATOR gửi đơn vay
  "reviewed_by"                varchar(36),             -- MANAGER/ADMIN phê duyệt
  "principal_amount"           decimal(18,2) NOT NULL,
  "currency_code"              varchar(10) DEFAULT 'USD' NOT NULL,
  "interest_rate"              decimal(6,4) NOT NULL,   -- Lãi suất năm dạng thập phân (VD: 0.1200 = 12%)
  "term_months"                number NOT NULL,
  "purpose"                    varchar(200),
  -- Trạng thái: PENDING | APPROVED | REJECTED | DISBURSED | CLOSED | DEFAULTED
  "status"                     varchar(20) NOT NULL,
  "version"                    number DEFAULT 1 NOT NULL, -- Optimistic Locking
  "review_note"                varchar(500),
  "reviewed_at"                timestamp,
  -- Thông tin giải ngân (điền khi APPROVED)
  "monthly_payment"            decimal(18,2),
  "outstanding_balance"        decimal(18,2),
  "disbursed_at"               timestamp,
  "maturity_date"              date,
  -- Loan AI input features (snapshot tại thời điểm nộp đơn — XGBoost model)
  "person_age"                 number,
  "person_income"              decimal(18,2),
  "person_home_ownership"      varchar(20),              -- RENT|MORTGAGE|OWN|OTHER
  "person_emp_length"          number,
  "loan_grade"                 varchar(2),               -- A–G
  "loan_intent"                varchar(30),              -- PERSONAL|EDUCATION|MEDICAL|VENTURE|HOMEIMPROVEMENT|DEBTCONSOLIDATION
  "cb_person_default_on_file"  varchar(1),               -- Y|N
  "cb_person_cred_hist_length" number,
  -- Kết quả AI
  "pd_score"                   decimal(6,4),             -- Xác suất vỡ nợ 0.0–1.0
  "risk_level"                 varchar(20),              -- LOW RISK | MEDIUM RISK | HIGH RISK
  "created_at"                 timestamp NOT NULL,
  "updated_at"                 timestamp
);

COMMENT ON TABLE "loans" IS 'Bảng OLTP khoản vay — thay thế loan_applications (v1.3). loan_applications giữ lại cho DWH.';
COMMENT ON COLUMN "loans"."loan_id" IS 'UUID';
COMMENT ON COLUMN "loans"."status" IS 'PENDING|APPROVED|REJECTED|DISBURSED|CLOSED|DEFAULTED';
COMMENT ON COLUMN "loans"."version" IS 'Optimistic Locking — tăng mỗi lần cập nhật trạng thái';

ALTER TABLE "loans" ADD FOREIGN KEY ("customer_id")  REFERENCES "customers" ("customer_id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "loans" ADD FOREIGN KEY ("submitted_by") REFERENCES "users" ("user_id")     DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "loans" ADD FOREIGN KEY ("reviewed_by")  REFERENCES "users" ("user_id")     DEFERRABLE INITIALLY IMMEDIATE;

CREATE INDEX idx_loans_status      ON "loans" ("status");
CREATE INDEX idx_loans_customer    ON "loans" ("customer_id");
CREATE INDEX idx_loans_submitted   ON "loans" ("submitted_by");

-- ---- Bảng model_configs (ngưỡng phân loại do ANALYST điều chỉnh) ----
CREATE TABLE "model_configs" (
  "config_id"    number GENERATED AS IDENTITY PRIMARY KEY,
  "model_name"   varchar(50) NOT NULL,    -- "fraud" | "loan"
  "param_name"   varchar(100) NOT NULL,   -- "reject_threshold" | "review_threshold" | "risk_high_threshold" | ...
  "param_value"  decimal(10,6) NOT NULL,
  "description"  varchar(255),
  "updated_by"   varchar(36),             -- user_id của ANALYST cập nhật
  "updated_at"   timestamp NOT NULL,
  "version"      number DEFAULT 1 NOT NULL,
  CONSTRAINT uq_model_configs_name_param UNIQUE ("model_name", "param_name")
);

COMMENT ON TABLE "model_configs" IS 'Ngưỡng phân loại Fraud/PD Score — ANALYST điều chỉnh, không hardcode trong code';
COMMENT ON COLUMN "model_configs"."model_name" IS '"fraud" | "loan"';
COMMENT ON COLUMN "model_configs"."param_name" IS '"reject_threshold" | "review_threshold" | "risk_high_threshold" | "risk_medium_threshold"';

ALTER TABLE "model_configs" ADD FOREIGN KEY ("updated_by") REFERENCES "users" ("user_id") DEFERRABLE INITIALLY IMMEDIATE;

-- ---- Bảng suppression_rules (whitelist bypass fraud scoring) ----
CREATE TABLE "suppression_rules" (
  "rule_id"     varchar(36) PRIMARY KEY,
  "rule_type"   varchar(20) NOT NULL,    -- MERCHANT | CUSTOMER | CARD_HASH
  "entity_id"   varchar(255) NOT NULL,   -- merchant_id / customer_id / card_hash
  "reason"      CLOB NOT NULL,
  "created_by"  varchar(36) NOT NULL,    -- ANALYST tạo rule
  "expires_at"  timestamp,               -- NULL = không hết hạn
  "is_active"   number(1) DEFAULT 1 NOT NULL,
  "created_at"  timestamp NOT NULL
);

COMMENT ON TABLE "suppression_rules" IS 'Whitelist giao dịch bypass fraud scoring — ANALYST quản lý';
COMMENT ON COLUMN "suppression_rules"."rule_id" IS 'UUID';
COMMENT ON COLUMN "suppression_rules"."rule_type" IS 'MERCHANT | CUSTOMER | CARD_HASH';
COMMENT ON COLUMN "suppression_rules"."is_active" IS '1 = active, 0 = vô hiệu hóa';

ALTER TABLE "suppression_rules" ADD FOREIGN KEY ("created_by") REFERENCES "users" ("user_id") DEFERRABLE INITIALLY IMMEDIATE;

CREATE INDEX idx_suppression_active   ON "suppression_rules" ("is_active");
CREATE INDEX idx_suppression_type_eid ON "suppression_rules" ("rule_type", "entity_id");

-- ---- Bảng analyst_reports (báo cáo phân tích ANALYST → MANAGER) ----
CREATE TABLE "analyst_reports" (
  "report_id"        varchar(36) PRIMARY KEY,
  "title"            varchar(255) NOT NULL,
  "report_type"      varchar(50) NOT NULL,   -- FRAUD_ANALYSIS | LOAN_ANALYSIS | THRESHOLD_RECOMMENDATION | SUPPRESSION_REVIEW | GENERAL
  "content_md"       CLOB NOT NULL,          -- Nội dung Markdown (render PDF bằng fpdf2)
  -- PENDING_REVIEW | ACKNOWLEDGED | ARCHIVED
  "status"           varchar(20) NOT NULL,
  "submitted_by"     varchar(36) NOT NULL,   -- ANALYST tạo báo cáo
  "submitted_at"     timestamp NOT NULL,
  "acknowledged_by"  varchar(36),            -- MANAGER/ADMIN xác nhận
  "acknowledged_at"  timestamp,
  "note"             varchar(1000)           -- Ghi chú của MANAGER khi acknowledge
);

COMMENT ON TABLE "analyst_reports" IS 'Báo cáo phân tích rủi ro định kỳ — ANALYST tạo, MANAGER acknowledge';
COMMENT ON COLUMN "analyst_reports"."report_id" IS 'UUID';
COMMENT ON COLUMN "analyst_reports"."report_type" IS 'FRAUD_ANALYSIS | LOAN_ANALYSIS | THRESHOLD_RECOMMENDATION | SUPPRESSION_REVIEW | GENERAL';
COMMENT ON COLUMN "analyst_reports"."status" IS 'PENDING_REVIEW | ACKNOWLEDGED | ARCHIVED';

ALTER TABLE "analyst_reports" ADD FOREIGN KEY ("submitted_by")    REFERENCES "users" ("user_id") DEFERRABLE INITIALLY IMMEDIATE;
ALTER TABLE "analyst_reports" ADD FOREIGN KEY ("acknowledged_by") REFERENCES "users" ("user_id") DEFERRABLE INITIALLY IMMEDIATE;

CREATE INDEX idx_analyst_reports_status ON "analyst_reports" ("status");
CREATE INDEX idx_analyst_reports_by     ON "analyst_reports" ("submitted_by");
