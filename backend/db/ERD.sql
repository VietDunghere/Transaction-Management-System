-- ============================================================
-- ERD.sql — Hệ thống Hỗ trợ Phát triển Rủi ro & Đánh giá Tín chấp
-- Phiên bản : 2.0 (Tinh gọn theo UC_SUMMARY.md)
-- Bảng      : 11 (giảm từ 31)
-- UC        : 20 | Vai trò : 5
-- Chuẩn hóa : BCNF / 4NF / 5NF
--
-- Thay đổi chính so với v1:
--   • Gộp roles + user_roles → cột role trong users (mỗi người 1 vai trò)
--   • Gộp risk_scoring_results → fraud_score + model_version trong transactions_live
--   • Loại merch_lat/long khỏi transactions_live (3NF: phụ thuộc bắc cầu qua merchant_id)
--   • Loại unix_time (đạo hàm từ txn_time), source_ip, reason_code, override_reason
--   • Đơn giản review_cases.case_status: OPEN | ASSIGNED | CLOSED (tách decision riêng)
--   • Bỏ 20 bảng: roles, user_roles, risk_scoring_results, review_case_actions,
--     txn_idempotency, txn_state, txn_state_history, reconciliation_runs,
--     reconciliation_items, datalake_snapshots, etl_logs, suppression_rules,
--     analyst_reports, dim_time, dim_customer, dim_merchant, dim_channel,
--     dim_location, fact_transactions, fact_loans
--   • Bỏ PROC_EXECUTE_RECONCILIATION, bỏ triggers TRG_OPTIMISTIC_LOCK_CHECK,
--     TRG_STATE_VERSION_UP, TRG_LOG_STATUS_CHANGE (thay bằng TRG_AUDIT_TXN_STATUS)
--
-- Phân tích chuẩn hóa (tóm tắt):
--   Mọi bảng đều thỏa 5NF:
--   • Mỗi thuộc tính non-key phụ thuộc hàm vào toàn bộ khóa ứng viên (BCNF)
--   • Không tồn tại phụ thuộc đa trị phi tầm thường (4NF)
--   • Không tồn tại phụ thuộc nối phi tầm thường (5NF)
--   • loans.person_* là snapshot tại thời điểm nộp → KHÔNG phải phụ thuộc
--     bắc cầu qua customer_id (giá trị có thể thay đổi theo thời gian)
-- ============================================================

CREATE ROLE ROLE_READ_ONLY;
GRANT CONNECT TO ROLE_READ_ONLY;
CREATE USER USER1 IDENTIFIED BY 123456;
GRANT ROLE_READ_ONLY TO USER1;


-- ============================================================
-- TABLES (11)
-- ============================================================

-- 1. USERS — Tài khoản nhân viên hệ thống (UC01, UC06)
--    Khóa ứng viên: user_id, username, email
--    role gộp từ bảng roles (mỗi người đúng 1 vai trò theo UC06.3)
CREATE TABLE users (
  user_id       varchar(36)  PRIMARY KEY,
  username      varchar(100) UNIQUE NOT NULL,
  password_hash varchar(255) NOT NULL,
  full_name     varchar(150) NOT NULL,
  email         varchar(150) UNIQUE NOT NULL,
  role          varchar(20)  NOT NULL,
  status        varchar(20)  DEFAULT 'ACTIVE' NOT NULL,
  created_at    timestamp    DEFAULT SYSTIMESTAMP NOT NULL,
  updated_at    timestamp,
  CONSTRAINT chk_user_role   CHECK (role   IN ('OPERATOR','REVIEWER','ANALYST','MANAGER','ADMIN')),
  CONSTRAINT chk_user_status CHECK (status IN ('ACTIVE','DISABLED'))
);

-- 2. CUSTOMERS — Dữ liệu tham chiếu khách hàng (nạp sẵn từ core banking, không có UC quản lý)
--    Khóa ứng viên: customer_id, customer_code, identity_card
CREATE TABLE customers (
  customer_id   varchar(36)  PRIMARY KEY,
  customer_code varchar(50)  UNIQUE,
  full_name     varchar(150),
  identity_card varchar(50)  UNIQUE,
  date_of_birth date,
  gender        varchar(10),
  address       varchar(255),
  city          varchar(100),
  job           varchar(150),
  latitude      decimal(9,6),
  longitude     decimal(9,6),
  income_level  varchar(50),
  kyc_status    varchar(20),
  created_at    timestamp    DEFAULT SYSTIMESTAMP NOT NULL
);

-- 3. MERCHANTS — Dữ liệu tham chiếu đơn vị chấp nhận thẻ (nạp sẵn, không có UC quản lý)
--    Khóa ứng viên: merchant_id, merchant_code
CREATE TABLE merchants (
  merchant_id       varchar(36)  PRIMARY KEY,
  merchant_code     varchar(50)  UNIQUE NOT NULL,
  merchant_name     varchar(150) NOT NULL,
  merchant_category varchar(100),
  city              varchar(100),
  state             varchar(50),
  country           varchar(100),
  latitude          decimal(9,6),
  longitude         decimal(9,6),
  risk_level        varchar(20),
  is_blacklisted    number(1)    DEFAULT 0 NOT NULL,
  created_at        timestamp    DEFAULT SYSTIMESTAMP NOT NULL
);

-- 4. CHANNELS — Kênh giao dịch (nạp sẵn: POS, ATM, Online, Mobile…)
--    Khóa ứng viên: channel_id, channel_code
CREATE TABLE channels (
  channel_id   number       GENERATED AS IDENTITY PRIMARY KEY,
  channel_code varchar(50)  UNIQUE NOT NULL,
  channel_name varchar(100) NOT NULL
);

-- 5. TRANSACTIONS_LIVE — Giao dịch tài chính (UC02)
--    fraud_score, model_version gộp từ risk_scoring_results (đã bỏ bảng đó)
--    Đã loại: merch_lat/long (3NF: phụ thuộc bắc cầu → merchants),
--             unix_time (đạo hàm), source_ip, reason_code, override_reason
CREATE TABLE transactions_live (
  txn_id             varchar(36)  PRIMARY KEY,
  customer_id        varchar(36)  NOT NULL,
  merchant_id        varchar(36)  NOT NULL,
  channel_id         number       NOT NULL,
  submitted_by       varchar(36)  NOT NULL,
  card_number_masked varchar(30),
  card_number_hash   varchar(64),
  amount             decimal(18,2) NOT NULL,
  txn_time           timestamp    NOT NULL,
  status             varchar(20)  NOT NULL,
  fraud_score        decimal(6,4),
  model_version      varchar(50),
  created_at         timestamp    DEFAULT SYSTIMESTAMP NOT NULL,
  updated_at         timestamp,
  CONSTRAINT chk_txn_amount      CHECK (amount > 0),
  CONSTRAINT chk_txn_fraud_score CHECK (fraud_score IS NULL OR fraud_score BETWEEN 0 AND 1),
  CONSTRAINT chk_txn_status      CHECK (status IN ('PENDING','APPROVED','REJECTED','MANUAL_REVIEW'))
);

-- 6. REVIEW_CASES — Hồ sơ xét duyệt thủ công (UC04)
--    Tạo tự động khi giao dịch có status = MANUAL_REVIEW (trigger)
--    Khóa ứng viên: case_id, txn_id (UNIQUE)
CREATE TABLE review_cases (
  case_id       varchar(36)   PRIMARY KEY,
  txn_id        varchar(36)   UNIQUE NOT NULL,
  case_status   varchar(20)   NOT NULL,
  assigned_to   varchar(36),
  decision      varchar(20),
  decision_note varchar(2000),
  version       number        DEFAULT 1 NOT NULL,
  created_at    timestamp     DEFAULT SYSTIMESTAMP NOT NULL,
  decided_at    timestamp,
  CONSTRAINT chk_case_status   CHECK (case_status IN ('OPEN','ASSIGNED','CLOSED')),
  CONSTRAINT chk_case_decision CHECK (decision IS NULL OR decision IN ('APPROVE','REJECT'))
);

-- 7. LOANS — Hồ sơ đề nghị vay vốn (UC03)
--    person_* = snapshot thông tin cá nhân tại thời điểm nộp (AI model features)
--    KHÔNG phải phụ thuộc bắc cầu qua customer_id vì giá trị có thể thay đổi
--    theo thời gian (tuổi, thu nhập, tình trạng nhà ở… khác với dữ liệu hiện tại)
CREATE TABLE loans (
  loan_id          varchar(36)   PRIMARY KEY,
  customer_id      varchar(36)   NOT NULL,
  submitted_by     varchar(36)   NOT NULL,
  reviewed_by      varchar(36),
  principal_amount decimal(18,2) NOT NULL,
  interest_rate    decimal(6,4)  NOT NULL,
  term_months      number        NOT NULL,
  purpose          varchar(200),
  status           varchar(20)   NOT NULL,
  version          number        DEFAULT 1 NOT NULL,
  review_note      varchar(500),
  reviewed_at      timestamp,
  monthly_payment  decimal(18,2),
  outstanding_balance decimal(18,2),
  disbursed_at     timestamp,
  maturity_date    date,
  -- Snapshot: thông tin cá nhân tại thời điểm nộp hồ sơ
  person_age                 number,
  person_income              decimal(18,2),
  person_home_ownership      varchar(20),
  person_emp_length          number,
  loan_grade                 varchar(2),
  loan_intent                varchar(30),
  cb_person_default_on_file  varchar(1),
  cb_person_cred_hist_length number,
  -- AI scoring output
  pd_score       decimal(6,4),
  risk_level     varchar(20),
  model_version  varchar(50),
  created_at     timestamp     DEFAULT SYSTIMESTAMP NOT NULL,
  updated_at     timestamp,
  CONSTRAINT chk_loan_amount        CHECK (principal_amount > 0),
  CONSTRAINT chk_loan_interest_rate CHECK (interest_rate > 0 AND interest_rate < 100),
  CONSTRAINT chk_loan_pd_score      CHECK (pd_score IS NULL OR pd_score BETWEEN 0 AND 1),
  CONSTRAINT chk_loan_status        CHECK (status IN ('PENDING','APPROVED','REJECTED','DISBURSED','CLOSED','DEFAULTED'))
);

-- 8. MODEL_CONFIGS — Ngưỡng phân loại AI (UC07)
--    Khóa ứng viên: config_id, (model_name + param_name)
CREATE TABLE model_configs (
  config_id   number        GENERATED AS IDENTITY PRIMARY KEY,
  model_name  varchar(50)   NOT NULL,
  param_name  varchar(100)  NOT NULL,
  param_value decimal(10,6) NOT NULL,
  description varchar(255),
  updated_by  varchar(36),
  updated_at  timestamp     DEFAULT SYSTIMESTAMP NOT NULL,
  version     number        DEFAULT 1 NOT NULL,
  CONSTRAINT uq_model_configs_name_param UNIQUE (model_name, param_name)
);

-- 9. AUDIT_LOGS — Nhật ký kiểm toán toàn hệ thống (UC05.2)
--    Thay thế cả txn_state_history và review_case_actions (đã bỏ)
CREATE TABLE audit_logs (
  log_id        varchar(36)  PRIMARY KEY,
  event_type    varchar(50)  NOT NULL,
  entity_type   varchar(50)  NOT NULL,
  entity_id     varchar(36)  NOT NULL,
  actor_user_id varchar(36),
  actor_name    varchar(150),
  event_ts      timestamp    DEFAULT SYSTIMESTAMP NOT NULL,
  detail_json   CLOB
);

-- 10. RULE_HITS — Kết quả luật phát hiện gian lận (AI team sở hữu, web app chỉ đọc)
--     Cung cấp explainability cho UC04 (reviewer xem "tại sao giao dịch bị flag")
CREATE TABLE rule_hits (
  rule_hit_id varchar(36)  PRIMARY KEY,
  txn_id      varchar(36)  NOT NULL,
  rule_code   varchar(50)  NOT NULL,
  rule_name   varchar(150),
  hit_value   varchar(255),
  severity    varchar(20),
  created_at  timestamp    DEFAULT SYSTIMESTAMP NOT NULL
);

-- 11. CARD_VELOCITY_STATS — Thống kê tốc độ sử dụng thẻ (AI team sở hữu)
--     Pre-compute cho fraud detection model, web app không truy cập trực tiếp
CREATE TABLE card_velocity_stats (
  card_hash     varchar(64)   PRIMARY KEY,
  avg_daily_txn decimal(8,2)  DEFAULT 0 NOT NULL,
  total_txn     number        DEFAULT 0 NOT NULL,
  avg_amt       decimal(12,2) DEFAULT 0 NOT NULL,
  std_amt       decimal(12,2) DEFAULT 0 NOT NULL,
  m2_amt        decimal(20,4) DEFAULT 0 NOT NULL,
  distinct_days number        DEFAULT 1 NOT NULL,
  last_txn_date varchar(10),
  last_updated  timestamp     DEFAULT SYSTIMESTAMP NOT NULL
);


-- ============================================================
-- INDEXES
-- ============================================================

-- users
CREATE INDEX idx_users_role            ON users (role);
CREATE INDEX idx_users_status          ON users (status);

-- transactions_live
CREATE INDEX idx_txn_live_status       ON transactions_live (status);
CREATE INDEX idx_txn_live_time         ON transactions_live (txn_time);
CREATE INDEX idx_txn_live_cust         ON transactions_live (customer_id);
CREATE INDEX idx_txn_live_merch        ON transactions_live (merchant_id);
CREATE INDEX idx_txn_live_chan         ON transactions_live (channel_id);
CREATE INDEX idx_txn_live_card_hash    ON transactions_live (card_number_hash);
CREATE INDEX idx_txn_live_submitted    ON transactions_live (submitted_by);

-- review_cases
CREATE INDEX idx_case_status           ON review_cases (case_status);
CREATE INDEX idx_case_assigned         ON review_cases (assigned_to);

-- loans
CREATE INDEX idx_loans_status          ON loans (status);
CREATE INDEX idx_loans_customer        ON loans (customer_id);
CREATE INDEX idx_loans_submitted       ON loans (submitted_by);
CREATE INDEX idx_loans_reviewed_by     ON loans (reviewed_by);

-- audit_logs
CREATE INDEX idx_audit_event_type      ON audit_logs (event_type);
CREATE INDEX idx_audit_entity          ON audit_logs (entity_type, entity_id);
CREATE INDEX idx_audit_event_ts        ON audit_logs (event_ts);
CREATE INDEX idx_audit_actor           ON audit_logs (actor_user_id);

-- rule_hits
CREATE INDEX idx_rule_hits_txn         ON rule_hits (txn_id);
CREATE INDEX idx_rule_hits_code        ON rule_hits (rule_code);


-- ============================================================
-- COMMENTS
-- ============================================================

COMMENT ON TABLE  users IS 'Tài khoản nhân viên — role gộp từ bảng roles (mỗi người 1 vai trò theo UC06.3)';
COMMENT ON COLUMN users.user_id IS 'UUID';
COMMENT ON COLUMN users.role    IS 'OPERATOR | REVIEWER | ANALYST | MANAGER | ADMIN';
COMMENT ON COLUMN users.status  IS 'ACTIVE | DISABLED';

COMMENT ON TABLE  customers IS 'Dữ liệu tham chiếu — nạp sẵn từ core banking, không có UC quản lý';
COMMENT ON COLUMN customers.customer_id IS 'UUID';

COMMENT ON TABLE  merchants IS 'Dữ liệu tham chiếu — nạp sẵn, không có UC quản lý';
COMMENT ON COLUMN merchants.merchant_id IS 'UUID';

COMMENT ON TABLE  channels IS 'Dữ liệu tham chiếu — nạp sẵn (POS, ATM, Online, Mobile…)';

COMMENT ON TABLE  transactions_live IS 'Giao dịch tài chính — fraud_score + model_version gộp từ risk_scoring_results';
COMMENT ON COLUMN transactions_live.txn_id           IS 'UUID';
COMMENT ON COLUMN transactions_live.status           IS 'PENDING | APPROVED | REJECTED | MANUAL_REVIEW';
COMMENT ON COLUMN transactions_live.card_number_hash IS 'SHA256 hash — không lưu số thẻ raw';
COMMENT ON COLUMN transactions_live.fraud_score      IS 'Điểm gian lận từ AI model (0.0–1.0)';
COMMENT ON COLUMN transactions_live.model_version    IS 'Phiên bản model AI tại thời điểm scoring';

COMMENT ON TABLE  review_cases IS 'Hồ sơ xét duyệt thủ công — tạo tự động khi txn.status = MANUAL_REVIEW';
COMMENT ON COLUMN review_cases.case_id     IS 'UUID';
COMMENT ON COLUMN review_cases.case_status IS 'OPEN | ASSIGNED | CLOSED';
COMMENT ON COLUMN review_cases.decision    IS 'NULL (chưa quyết) | APPROVE | REJECT';
COMMENT ON COLUMN review_cases.version     IS 'Optimistic Locking — tăng mỗi lần cập nhật';

COMMENT ON TABLE  loans IS 'Hồ sơ vay — person_* là snapshot tại thời điểm nộp, không phải phụ thuộc bắc cầu';
COMMENT ON COLUMN loans.loan_id       IS 'UUID';
COMMENT ON COLUMN loans.status        IS 'PENDING | APPROVED | REJECTED | DISBURSED | CLOSED | DEFAULTED';
COMMENT ON COLUMN loans.version       IS 'Optimistic Locking';
COMMENT ON COLUMN loans.pd_score      IS 'Probability of Default từ AI model (0.0–1.0)';
COMMENT ON COLUMN loans.model_version IS 'Phiên bản model AI tại thời điểm scoring';

COMMENT ON TABLE  model_configs IS 'Ngưỡng phân loại Fraud / PD Score — ANALYST điều chỉnh (UC07)';
COMMENT ON COLUMN model_configs.model_name IS '"fraud" | "loan"';
COMMENT ON COLUMN model_configs.param_name IS '"reject_threshold" | "review_threshold" | "high_risk_threshold" | "medium_risk_threshold"';

COMMENT ON TABLE  audit_logs IS 'Nhật ký kiểm toán toàn hệ thống (UC05.2) — thay thế txn_state_history + review_case_actions';
COMMENT ON COLUMN audit_logs.log_id IS 'UUID';

COMMENT ON TABLE  rule_hits IS 'AI team sở hữu — luật nào triggered cho mỗi giao dịch (explainability UC04)';
COMMENT ON COLUMN rule_hits.rule_hit_id IS 'UUID';

COMMENT ON TABLE  card_velocity_stats IS 'AI team sở hữu — thống kê pre-compute cho fraud detection';
COMMENT ON COLUMN card_velocity_stats.card_hash IS 'SHA256 hash — PK, không lưu số thẻ raw';
COMMENT ON COLUMN card_velocity_stats.m2_amt    IS 'Welford algorithm M2 — tính std online';


-- ============================================================
-- FOREIGN KEYS
-- ============================================================

-- transactions_live → customers, merchants, channels, users
ALTER TABLE transactions_live ADD CONSTRAINT fk_txn_customer
  FOREIGN KEY (customer_id)  REFERENCES customers (customer_id);
ALTER TABLE transactions_live ADD CONSTRAINT fk_txn_merchant
  FOREIGN KEY (merchant_id)  REFERENCES merchants (merchant_id);
ALTER TABLE transactions_live ADD CONSTRAINT fk_txn_channel
  FOREIGN KEY (channel_id)   REFERENCES channels  (channel_id);
ALTER TABLE transactions_live ADD CONSTRAINT fk_txn_submitted_by
  FOREIGN KEY (submitted_by) REFERENCES users     (user_id);

-- review_cases → transactions_live, users
ALTER TABLE review_cases ADD CONSTRAINT fk_case_txn
  FOREIGN KEY (txn_id)      REFERENCES transactions_live (txn_id);
ALTER TABLE review_cases ADD CONSTRAINT fk_case_assigned
  FOREIGN KEY (assigned_to) REFERENCES users             (user_id);

-- rule_hits → transactions_live
ALTER TABLE rule_hits ADD CONSTRAINT fk_rule_hit_txn
  FOREIGN KEY (txn_id) REFERENCES transactions_live (txn_id);

-- loans → customers, users (submitted_by), users (reviewed_by)
ALTER TABLE loans ADD CONSTRAINT fk_loan_customer
  FOREIGN KEY (customer_id)  REFERENCES customers (customer_id);
ALTER TABLE loans ADD CONSTRAINT fk_loan_submitted_by
  FOREIGN KEY (submitted_by) REFERENCES users     (user_id);
ALTER TABLE loans ADD CONSTRAINT fk_loan_reviewed_by
  FOREIGN KEY (reviewed_by)  REFERENCES users     (user_id);

-- model_configs → users
ALTER TABLE model_configs ADD CONSTRAINT fk_config_updated_by
  FOREIGN KEY (updated_by) REFERENCES users (user_id);

-- audit_logs → users
ALTER TABLE audit_logs ADD CONSTRAINT fk_audit_actor
  FOREIGN KEY (actor_user_id) REFERENCES users (user_id);


-- ============================================================
-- PROCEDURES
-- ============================================================

-- PROC_SUBMIT_TRANSACTION
-- Mục đích: Nhập giao dịch mới, tự động phân loại dựa trên fraud_score và ngưỡng
-- Liên quan: UC02.1 (Nộp giao dịch mới)
CREATE OR REPLACE PROCEDURE PROC_SUBMIT_TRANSACTION (
    p_txn_id             IN varchar2,
    p_customer_id        IN varchar2,
    p_merchant_id        IN varchar2,
    p_channel_id         IN number,
    p_amount             IN number,
    p_txn_time           IN timestamp,
    p_submitted_by       IN varchar2,
    p_card_number_hash   IN varchar2,
    p_card_number_masked IN varchar2,
    p_fraud_score        IN number,
    p_model_version      IN varchar2,
    -- OUT
    p_out_txn_id   OUT varchar2,
    p_out_status   OUT varchar2
) AS
    v_reject_threshold decimal(6,4);
    v_review_threshold decimal(6,4);
    v_status           varchar2(20);
BEGIN
    -- B1: Lấy ngưỡng hiện hành từ model_configs
    BEGIN
        SELECT param_value INTO v_reject_threshold
        FROM model_configs
        WHERE model_name = 'fraud' AND param_name = 'reject_threshold';

        SELECT param_value INTO v_review_threshold
        FROM model_configs
        WHERE model_name = 'fraud' AND param_name = 'review_threshold';
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            RAISE_APPLICATION_ERROR(-20010, 'ERR_CFG_01: Chưa cấu hình ngưỡng fraud');
    END;

    -- B2: Phân loại dựa trên fraud_score
    IF p_fraud_score IS NULL THEN
        v_status := 'PENDING';
    ELSIF p_fraud_score >= v_reject_threshold THEN
        v_status := 'REJECTED';
    ELSIF p_fraud_score >= v_review_threshold THEN
        v_status := 'MANUAL_REVIEW';
    ELSE
        v_status := 'APPROVED';
    END IF;

    -- B3: Insert giao dịch (TRG_DETECT_HIGH_VALUE có thể override status)
    INSERT INTO transactions_live (
        txn_id, customer_id, merchant_id, channel_id,
        submitted_by, card_number_hash, card_number_masked,
        amount, txn_time,
        status, fraud_score, model_version, created_at
    ) VALUES (
        p_txn_id, p_customer_id, p_merchant_id, p_channel_id,
        p_submitted_by, p_card_number_hash, p_card_number_masked,
        p_amount, NVL(p_txn_time, SYSTIMESTAMP),
        v_status, p_fraud_score, p_model_version, SYSTIMESTAMP
    );

    -- B4: Ghi audit log
    INSERT INTO audit_logs (
        log_id, event_type, entity_type, entity_id,
        actor_user_id, event_ts, detail_json
    ) VALUES (
        SYS_GUID(), 'CREATE', 'TRANSACTION', p_txn_id,
        p_submitted_by, SYSTIMESTAMP,
        '{"status":"' || v_status || '","fraud_score":'
          || NVL(TO_CHAR(p_fraud_score), 'null') || '}'
    );

    p_out_txn_id := p_txn_id;
    p_out_status := v_status;
    COMMIT;

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE_APPLICATION_ERROR(-20001,
            'ERR_DB_01: Lỗi CSDL khi submit giao dịch - ' || SQLERRM);
END;
/


-- PROC_PROCESS_REVIEW_CASE
-- Mục đích: Reviewer quyết định phê duyệt / từ chối giao dịch MANUAL_REVIEW
-- Liên quan: UC04.3 (Ra quyết định Phê duyệt / Từ chối)
CREATE OR REPLACE PROCEDURE PROC_PROCESS_REVIEW_CASE (
    p_case_id       IN varchar2,
    p_decision      IN varchar2,    -- 'APPROVE' hoặc 'REJECT'
    p_decision_note IN varchar2,
    p_decided_by    IN varchar2,    -- user_id của reviewer
    p_out_status    OUT varchar2
) AS
    v_txn_id      varchar2(36);
    v_case_status varchar2(20);
    v_new_txn_status varchar2(20);
BEGIN
    -- B1: Lock và kiểm tra case
    BEGIN
        SELECT txn_id, case_status
        INTO v_txn_id, v_case_status
        FROM review_cases
        WHERE case_id = p_case_id
        FOR UPDATE;
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            RAISE_APPLICATION_ERROR(-20002, 'ERR_CASE_00: Không tìm thấy Case');
    END;

    IF v_case_status NOT IN ('OPEN', 'ASSIGNED') THEN
        RAISE_APPLICATION_ERROR(-20003, 'ERR_CASE_01: Case đã được xử lý');
    END IF;

    -- B2: Xác định trạng thái mới
    IF p_decision = 'APPROVE' THEN
        v_new_txn_status := 'APPROVED';
    ELSIF p_decision = 'REJECT' THEN
        v_new_txn_status := 'REJECTED';
    ELSE
        RAISE_APPLICATION_ERROR(-20004,
            'ERR_CASE_02: Decision không hợp lệ, chỉ nhận APPROVE hoặc REJECT');
    END IF;

    -- B3: Cập nhật case
    UPDATE review_cases
    SET case_status   = 'CLOSED',
        decision      = p_decision,
        decision_note = p_decision_note,
        assigned_to   = NVL(assigned_to, p_decided_by),
        version       = version + 1,
        decided_at    = SYSTIMESTAMP
    WHERE case_id = p_case_id;

    -- B4: Cập nhật trạng thái giao dịch
    UPDATE transactions_live
    SET status     = v_new_txn_status,
        updated_at = SYSTIMESTAMP
    WHERE txn_id = v_txn_id;

    -- B5: Ghi audit log
    INSERT INTO audit_logs (
        log_id, event_type, entity_type, entity_id,
        actor_user_id, event_ts, detail_json
    ) VALUES (
        SYS_GUID(), p_decision, 'REVIEW_CASE', p_case_id,
        p_decided_by, SYSTIMESTAMP,
        '{"txn_id":"' || v_txn_id || '","new_status":"' || v_new_txn_status || '"}'
    );

    p_out_status := v_new_txn_status;
    COMMIT;

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE;
END;
/


-- ============================================================
-- TRIGGERS
-- ============================================================

-- Auto-flag giao dịch giá trị cao → MANUAL_REVIEW (business rule)
-- Đơn vị tiền tệ: USD (toàn hệ thống). Ngưỡng: $20,000
CREATE OR REPLACE TRIGGER TRG_DETECT_HIGH_VALUE
BEFORE INSERT ON transactions_live
FOR EACH ROW
BEGIN
    IF :NEW.amount >= 6767 THEN
        :NEW.status := 'MANUAL_REVIEW';
    END IF;
END;
/

-- Auto-tạo review case khi giao dịch có status = MANUAL_REVIEW
CREATE OR REPLACE TRIGGER TRG_AUTO_CREATE_CASE
AFTER INSERT OR UPDATE ON transactions_live
FOR EACH ROW
BEGIN
    IF :NEW.status = 'MANUAL_REVIEW' THEN
        IF INSERTING OR (UPDATING AND NVL(:OLD.status, '') <> 'MANUAL_REVIEW') THEN
            INSERT INTO review_cases (
                case_id, txn_id, case_status, created_at
            ) VALUES (
                SYS_GUID(), :NEW.txn_id, 'OPEN', SYSTIMESTAMP
            );
        END IF;
    END IF;
END;
/

-- Ghi audit log khi trạng thái giao dịch thay đổi (bổ sung cho procedure)
CREATE OR REPLACE TRIGGER TRG_AUDIT_TXN_STATUS
AFTER UPDATE ON transactions_live
FOR EACH ROW
BEGIN
    IF :OLD.status <> :NEW.status THEN
        INSERT INTO audit_logs (
            log_id, event_type, entity_type, entity_id,
            event_ts, detail_json
        ) VALUES (
            SYS_GUID(), 'STATUS_CHANGE', 'TRANSACTION', :NEW.txn_id,
            SYSTIMESTAMP,
            '{"old_status":"' || :OLD.status
              || '","new_status":"' || :NEW.status || '"}'
        );
    END IF;
END;

