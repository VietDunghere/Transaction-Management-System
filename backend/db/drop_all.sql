-- Drop all v1+v2 objects, then recreate from ERD.sql
-- Run: sqlplus ADMIN/123456@localhost:1521/FREEPDB1 @db/drop_all.sql

SET SERVEROUTPUT ON
SET FEEDBACK OFF

-- Drop triggers first
BEGIN FOR r IN (SELECT trigger_name FROM user_triggers) LOOP
  EXECUTE IMMEDIATE 'DROP TRIGGER "' || r.trigger_name || '"';
  DBMS_OUTPUT.PUT_LINE('Dropped trigger: ' || r.trigger_name);
END LOOP; END;
/

-- Drop procedures
BEGIN FOR r IN (SELECT object_name FROM user_objects WHERE object_type = 'PROCEDURE') LOOP
  EXECUTE IMMEDIATE 'DROP PROCEDURE "' || r.object_name || '"';
  DBMS_OUTPUT.PUT_LINE('Dropped procedure: ' || r.object_name);
END LOOP; END;
/

-- Drop all tables (CASCADE CONSTRAINTS to handle FK ordering)
BEGIN FOR r IN (SELECT table_name FROM user_tables) LOOP
  EXECUTE IMMEDIATE 'DROP TABLE "' || r.table_name || '" CASCADE CONSTRAINTS PURGE';
  DBMS_OUTPUT.PUT_LINE('Dropped table: ' || r.table_name);
END LOOP; END;
/

PROMPT
PROMPT === All objects dropped. Now recreating from ERD.sql... ===
PROMPT

@@ERD.sql

PROMPT
PROMPT === Done. ===

EXIT;
