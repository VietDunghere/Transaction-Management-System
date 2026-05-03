SET SERVEROUTPUT ON
SET FEEDBACK OFF

-- Drop only APP tables explicitly (v1 leftovers + v2)
-- Children first, parents last
DECLARE
  TYPE t_names IS TABLE OF VARCHAR2(128);
  v_tables t_names := t_names(
    'REVIEW_CASE_ACTIONS',
    'RECONCILIATION_ITEMS',
    'DATALAKE_SNAPSHOTS',
    'ETL_LOGS',
    'ANALYST_REPORTS',
    'SUPPRESSION_RULES',
    'TXN_STATE_HISTORY',
    'TXN_STATE',
    'TXN_IDEMPOTENCY',
    'RISK_SCORING_RESULTS',
    'USER_ROLES',
    'ROLES',
    'RECONCILIATION_RUNS',
    'RULE_HITS',
    'CARD_VELOCITY_STATS',
    'AUDIT_LOGS',
    'MODEL_CONFIGS',
    'REVIEW_CASES',
    'LOANS',
    'TRANSACTIONS_LIVE',
    'MERCHANTS',
    'CHANNELS',
    'CUSTOMERS',
    'USERS'
  );
BEGIN
  FOR i IN 1 .. v_tables.COUNT LOOP
    BEGIN
      EXECUTE IMMEDIATE 'DROP TABLE ' || v_tables(i) || ' CASCADE CONSTRAINTS PURGE';
      DBMS_OUTPUT.PUT_LINE('Dropped: ' || v_tables(i));
    EXCEPTION
      WHEN OTHERS THEN
        IF SQLCODE = -942 THEN
          DBMS_OUTPUT.PUT_LINE('Skip (not exist): ' || v_tables(i));
        ELSE
          DBMS_OUTPUT.PUT_LINE('ERROR ' || v_tables(i) || ': ' || SQLERRM);
        END IF;
    END;
  END LOOP;
END;
/

-- Drop app triggers
BEGIN FOR r IN (SELECT trigger_name FROM user_triggers WHERE trigger_name LIKE 'TRG_%') LOOP
  EXECUTE IMMEDIATE 'DROP TRIGGER ' || r.trigger_name;
  DBMS_OUTPUT.PUT_LINE('Dropped trigger: ' || r.trigger_name);
END LOOP; END;
/

-- Drop app procedures
BEGIN FOR r IN (SELECT object_name FROM user_objects WHERE object_type = 'PROCEDURE' AND object_name LIKE 'SP_%') LOOP
  EXECUTE IMMEDIATE 'DROP PROCEDURE ' || r.object_name;
  DBMS_OUTPUT.PUT_LINE('Dropped procedure: ' || r.object_name);
END LOOP; END;
/

PROMPT === Drop complete. Recreating from ERD.sql... ===

@@ERD.sql

PROMPT === Done. ===
EXIT;
