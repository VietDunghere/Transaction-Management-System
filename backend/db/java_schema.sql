-- ============================================================================
-- TMS (Transaction Management System) - MySQL 8 Schema
-- Translated from the Oracle DDL in
--   docs/tms_migration_to_java_more_like_downgrade_xd.md  (section 3.2)
-- per docs/plan.md section 5.
--
-- Translations applied:
--   NUMBER(p,s)            -> DECIMAL(p,s)
--   integer NUMBER         -> INT / BIGINT
--   GENERATED AS IDENTITY  -> AUTO_INCREMENT
--   SYSTIMESTAMP / DEFAULT -> CURRENT_TIMESTAMP
--   NUMBER(1) boolean      -> TINYINT(1)
--   CLOB                   -> JSON (detail_json)
--   CHECK constraints      -> kept (MySQL 8 enforces them)
--   Engine InnoDB, charset utf8mb4.
--
-- Extra columns (plan.md section 5):
--   users.is_first_login TINYINT(1) NOT NULL DEFAULT 0
--   users.email NOT NULL UNIQUE (ERD form)
--   customers.state VARCHAR(10) (present in ORM + seed, missing from Oracle ERD)
--
-- Re-runnable: drops are wrapped with FOREIGN_KEY_CHECKS=0/1.
-- ============================================================================

CREATE DATABASE IF NOT EXISTS tms_local
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE tms_local;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS rule_hits;
DROP TABLE IF EXISTS card_velocity_stats;
DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS model_configs;
DROP TABLE IF EXISTS loans;
DROP TABLE IF EXISTS review_cases;
DROP TABLE IF EXISTS transactions_live;
DROP TABLE IF EXISTS channels;
DROP TABLE IF EXISTS merchants;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS users;
SET FOREIGN_KEY_CHECKS = 1;

-- ----------------------------------------------------------------------------
-- users
-- ----------------------------------------------------------------------------
CREATE TABLE users (
    user_id         VARCHAR(36)  NOT NULL,
    username        VARCHAR(100) NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    full_name       VARCHAR(150) NOT NULL,
    email           VARCHAR(150) NOT NULL,
    role            VARCHAR(20)  NOT NULL,            -- OPERATOR|REVIEWER|ANALYST|MANAGER|ADMIN
    status          VARCHAR(20)  NOT NULL DEFAULT 'ACTIVE',  -- ACTIVE|DISABLED
    is_first_login  TINYINT(1)   NOT NULL DEFAULT 0,
    created_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP    NULL,
    PRIMARY KEY (user_id),
    UNIQUE KEY uq_users_username (username),
    UNIQUE KEY uq_users_email (email),
    KEY idx_users_role (role),
    KEY idx_users_status (status),
    CONSTRAINT chk_users_role   CHECK (role IN ('OPERATOR','REVIEWER','ANALYST','MANAGER','ADMIN')),
    CONSTRAINT chk_users_status CHECK (status IN ('ACTIVE','DISABLED'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- customers
-- ----------------------------------------------------------------------------
CREATE TABLE customers (
    customer_id    VARCHAR(36) NOT NULL,
    customer_code  VARCHAR(50) NULL,
    full_name      VARCHAR(150) NULL,
    identity_card  VARCHAR(50) NULL,
    date_of_birth  DATE NULL,
    gender         VARCHAR(10) NULL,
    address        VARCHAR(255) NULL,
    city           VARCHAR(100) NULL,
    state          VARCHAR(10) NULL,
    job            VARCHAR(150) NULL,
    latitude       DECIMAL(9,6) NULL,
    longitude      DECIMAL(9,6) NULL,
    income_level   VARCHAR(50) NULL,
    kyc_status     VARCHAR(20) NULL,
    created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (customer_id),
    UNIQUE KEY uq_customers_code (customer_code),
    UNIQUE KEY uq_customers_identity (identity_card),
    KEY idx_customers_code (customer_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- merchants
-- ----------------------------------------------------------------------------
CREATE TABLE merchants (
    merchant_id       VARCHAR(36) NOT NULL,
    merchant_code     VARCHAR(50) NOT NULL,
    merchant_name     VARCHAR(150) NOT NULL,
    merchant_category VARCHAR(100) NULL,
    risk_level        VARCHAR(20) NULL,            -- LOW|MEDIUM|HIGH
    is_blacklisted    TINYINT(1) NOT NULL DEFAULT 0,
    city              VARCHAR(100) NULL,
    state             VARCHAR(50) NULL,
    country           VARCHAR(100) NULL,
    latitude          DECIMAL(9,6) NULL,
    longitude         DECIMAL(9,6) NULL,
    created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (merchant_id),
    UNIQUE KEY uq_merchants_code (merchant_code),
    KEY idx_merchants_code (merchant_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- channels
-- ----------------------------------------------------------------------------
CREATE TABLE channels (
    channel_id   INT NOT NULL AUTO_INCREMENT,
    channel_code VARCHAR(50) NOT NULL,
    channel_name VARCHAR(100) NOT NULL,
    PRIMARY KEY (channel_id),
    UNIQUE KEY uq_channels_code (channel_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- transactions_live
-- ----------------------------------------------------------------------------
CREATE TABLE transactions_live (
    txn_id             VARCHAR(36) NOT NULL,
    customer_id        VARCHAR(36) NOT NULL,
    merchant_id        VARCHAR(36) NOT NULL,
    channel_id         INT NOT NULL,
    submitted_by       VARCHAR(36) NOT NULL,
    card_number_masked VARCHAR(30) NULL,
    card_number_hash   VARCHAR(64) NULL,
    amount             DECIMAL(18,2) NOT NULL,
    txn_time           TIMESTAMP NOT NULL,
    status             VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    fraud_score        DECIMAL(6,4) NULL,
    model_version      VARCHAR(50) NULL,
    created_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at         TIMESTAMP NULL,
    PRIMARY KEY (txn_id),
    KEY idx_txn_status (status),
    KEY idx_txn_time (txn_time),
    KEY idx_txn_customer (customer_id),
    KEY idx_txn_merchant (merchant_id),
    KEY idx_txn_channel (channel_id),
    KEY idx_txn_card_hash (card_number_hash),
    KEY idx_txn_submitted_by (submitted_by),
    CONSTRAINT fk_txn_customer  FOREIGN KEY (customer_id)  REFERENCES customers(customer_id),
    CONSTRAINT fk_txn_merchant  FOREIGN KEY (merchant_id)  REFERENCES merchants(merchant_id),
    CONSTRAINT fk_txn_channel   FOREIGN KEY (channel_id)   REFERENCES channels(channel_id),
    CONSTRAINT fk_txn_submitter FOREIGN KEY (submitted_by) REFERENCES users(user_id),
    CONSTRAINT chk_txn_amount      CHECK (amount > 0),
    CONSTRAINT chk_txn_fraud_score CHECK (fraud_score IS NULL OR (fraud_score BETWEEN 0 AND 1)),
    CONSTRAINT chk_txn_status      CHECK (status IN ('PENDING','APPROVED','REJECTED','MANUAL_REVIEW'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- review_cases
-- ----------------------------------------------------------------------------
CREATE TABLE review_cases (
    case_id       VARCHAR(36) NOT NULL,
    txn_id        VARCHAR(36) NOT NULL,
    case_status   VARCHAR(20) NOT NULL DEFAULT 'OPEN',  -- OPEN|ASSIGNED|CLOSED
    assigned_to   VARCHAR(36) NULL,
    decision      VARCHAR(20) NULL,                     -- APPROVE|REJECT or NULL
    decision_note VARCHAR(2000) NULL,
    version       INT NOT NULL DEFAULT 1,
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    decided_at    TIMESTAMP NULL,
    PRIMARY KEY (case_id),
    UNIQUE KEY uq_cases_txn (txn_id),
    KEY idx_cases_status (case_status),
    KEY idx_cases_assigned (assigned_to),
    CONSTRAINT fk_cases_txn      FOREIGN KEY (txn_id)      REFERENCES transactions_live(txn_id),
    CONSTRAINT fk_cases_assigned FOREIGN KEY (assigned_to) REFERENCES users(user_id),
    CONSTRAINT chk_cases_status   CHECK (case_status IN ('OPEN','ASSIGNED','CLOSED')),
    CONSTRAINT chk_cases_decision CHECK (decision IN ('APPROVE','REJECT') OR decision IS NULL)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- loans
-- ----------------------------------------------------------------------------
CREATE TABLE loans (
    loan_id          VARCHAR(36) NOT NULL,
    customer_id      VARCHAR(36) NOT NULL,
    submitted_by     VARCHAR(36) NOT NULL,
    reviewed_by      VARCHAR(36) NULL,
    principal_amount DECIMAL(18,2) NOT NULL,
    interest_rate    DECIMAL(6,4) NOT NULL,
    term_months      INT NOT NULL,
    purpose          VARCHAR(200) NULL,
    status           VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    version          INT NOT NULL DEFAULT 1,
    review_note      VARCHAR(500) NULL,
    reviewed_at      TIMESTAMP NULL,
    monthly_payment  DECIMAL(18,2) NULL,
    outstanding_balance DECIMAL(18,2) NULL,
    disbursed_at     TIMESTAMP NULL,
    maturity_date    DATE NULL,
    -- AI input features
    person_age       INT NULL,
    person_income    DECIMAL(18,2) NULL,
    person_home_ownership VARCHAR(20) NULL,
    person_emp_length INT NULL,
    loan_grade       VARCHAR(2) NULL,
    loan_intent      VARCHAR(30) NULL,
    cb_person_default_on_file VARCHAR(1) NULL,
    cb_person_cred_hist_length INT NULL,
    -- AI output
    pd_score         DECIMAL(6,4) NULL,
    risk_level       VARCHAR(20) NULL,
    model_version    VARCHAR(50) NULL,
    created_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP NULL,
    PRIMARY KEY (loan_id),
    KEY idx_loans_status (status),
    KEY idx_loans_customer (customer_id),
    KEY idx_loans_submitted (submitted_by),
    KEY idx_loans_reviewed (reviewed_by),
    CONSTRAINT fk_loans_customer  FOREIGN KEY (customer_id)  REFERENCES customers(customer_id),
    CONSTRAINT fk_loans_submitter FOREIGN KEY (submitted_by) REFERENCES users(user_id),
    CONSTRAINT fk_loans_reviewer  FOREIGN KEY (reviewed_by)  REFERENCES users(user_id),
    CONSTRAINT chk_loans_principal CHECK (principal_amount > 0),
    CONSTRAINT chk_loans_rate      CHECK (interest_rate > 0 AND interest_rate < 100),
    CONSTRAINT chk_loans_pd        CHECK (pd_score IS NULL OR (pd_score BETWEEN 0 AND 1)),
    CONSTRAINT chk_loans_status    CHECK (status IN ('PENDING','APPROVED','REJECTED','DISBURSED','CLOSED','DEFAULTED'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- model_configs
-- ----------------------------------------------------------------------------
CREATE TABLE model_configs (
    config_id   INT NOT NULL AUTO_INCREMENT,
    model_name  VARCHAR(50)  NOT NULL,
    param_name  VARCHAR(100) NOT NULL,
    param_value DECIMAL(10,6) NOT NULL,
    description VARCHAR(255) NULL,
    updated_by  VARCHAR(36) NULL,
    updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    version     INT NOT NULL DEFAULT 1,
    PRIMARY KEY (config_id),
    UNIQUE KEY uq_model_param (model_name, param_name),
    CONSTRAINT fk_modelcfg_updater FOREIGN KEY (updated_by) REFERENCES users(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- audit_logs
-- ----------------------------------------------------------------------------
CREATE TABLE audit_logs (
    log_id        VARCHAR(36) NOT NULL,
    event_type    VARCHAR(50) NOT NULL,
    entity_type   VARCHAR(50) NOT NULL,
    entity_id     VARCHAR(36) NOT NULL,
    actor_user_id VARCHAR(36) NULL,
    actor_name    VARCHAR(150) NULL,
    event_ts      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    detail_json   JSON NULL,
    PRIMARY KEY (log_id),
    KEY idx_audit_event_type (event_type),
    KEY idx_audit_entity (entity_type, entity_id),
    KEY idx_audit_event_ts (event_ts),
    KEY idx_audit_actor (actor_user_id),
    CONSTRAINT fk_audit_actor FOREIGN KEY (actor_user_id) REFERENCES users(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- rule_hits
-- ----------------------------------------------------------------------------
CREATE TABLE rule_hits (
    rule_hit_id VARCHAR(36) NOT NULL,
    txn_id      VARCHAR(36) NOT NULL,
    rule_code   VARCHAR(50) NOT NULL,
    rule_name   VARCHAR(150) NULL,
    hit_value   VARCHAR(255) NULL,
    severity    VARCHAR(20) NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (rule_hit_id),
    KEY idx_rule_hits_txn (txn_id),
    KEY idx_rule_hits_code (rule_code),
    CONSTRAINT fk_rule_hits_txn FOREIGN KEY (txn_id) REFERENCES transactions_live(txn_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- card_velocity_stats
-- ----------------------------------------------------------------------------
CREATE TABLE card_velocity_stats (
    card_hash      VARCHAR(64) NOT NULL,
    avg_daily_txn  DECIMAL(8,2)  DEFAULT 0.00,
    total_txn      INT           DEFAULT 0,
    avg_amt        DECIMAL(12,2) DEFAULT 0.00,
    std_amt        DECIMAL(12,2) DEFAULT 0.00,
    m2_amt         DECIMAL(20,4) DEFAULT 0.0000,
    distinct_days  INT           DEFAULT 1,
    last_txn_date  VARCHAR(10) NULL,
    last_updated   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (card_hash)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
