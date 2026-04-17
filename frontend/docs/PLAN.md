# Frontend Delivery Plan (16/04 -> 24/04)

## 1) Cập nhật trạng thái và nguyên tắc

- Trạng thái hiện tại: task 16/04 (Foundation + Design Context) đã hoàn thành.
- API contract đã cập nhật theo API_DESIGN v1.0.0 (17/04), từ giai đoạn này lock theo endpoint + payload thực tế.
- Mục tiêu giữ nguyên: hoàn thiện frontend trước 24/04, đã test và sẵn sàng handoff/UAT.
- Quy mô nhân sự:
    - Biden (4/5): owner toàn bộ critical path, logic nghiệp vụ rủi ro cao, tích hợp API và xử lý edge case.
    - Doanh (1/5): owner task low-risk (UI/presentational/formatting/checklist QA), không giữ khóa tiến độ release.
- Nguyên tắc điều phối:
    - Critical path do Biden nắm.
    - Doanh chạy song song để tăng throughput nhưng không quyết định kiến trúc/nghiệp vụ có side effect.
    - Duy trì adapter layer để cô lập thay đổi nhỏ từ backend.
    - Testing + bugfix tiếp tục chiếm khoảng 40% effort tổng.

## 2) Scope module theo API_DESIGN mới

- UC02: Authentication & Authorization.
- UC03: Transaction Management.
- UC04: User Management.
- UC05: Case Management & Review.
- UC06: Loan Management.
- UC07: Audit Logging.
- UC08: Dashboard & Reports.
- UC09: ETL Pipeline.

Nhóm ưu tiên triển khai:

- P0 (critical path): UC02, UC03, UC05, UC08.
- P1 (parallel): UC04, UC06, UC07, UC09.

## 3) Flow thực hiện (đã cập nhật)

1. Giữ nguyên nền tảng 16/04 (token, app shell, route skeleton, UI primitives).
2. Tích hợp API theo từng wave ưu tiên P0 -> P1.
3. Chuẩn hóa xử lý chung: auth token, error envelope, pagination, role guard.
4. Hoàn tất regression + bugfix theo checklist trước cutoff 24/04.

## 4) Phân công theo vai trò và mức rủi ro

### 4.1 Biden (owner critical path, high-risk)

- Kiến trúc và tích hợp lõi:
    - Route guard theo RBAC thực tế.
    - API client chuẩn (token lifecycle, refresh, error mapping, retry tối thiểu).
    - Query/mutation strategy và cache invalidation.
- Nghiệp vụ rủi ro cao:
    - Auth flow (login, me, refresh, change-password).
    - Transaction + Case state transition.
    - Loan decision/case decision có optimistic locking (`version`).
    - Dashboard/report mapping và export flow (json/csv).
- Quality gate:
    - Thiết kế test strategy theo rủi ro.
    - Owner bug triage mức high/critical.

### 4.2 Doanh (owner low-risk, non-blocking)

- UI/presentational:
    - Dựng/chỉnh page-level UI theo payload thực tế.
    - Hoàn thiện table/filter/cards/charts shell, loading/empty/error states.
    - Rà soát responsive và consistency.
- QA hỗ trợ:
    - Viết checklist test tay theo module.
    - Smoke test sau từng đợt merge.

Rule bắt buộc: task của Doanh không quyết định kiến trúc, không nắm nghiệp vụ có side effect, không giữ khóa merge branch critical.

## 5) Kế hoạch theo mốc thời gian (16/04 -> 24/04)

## 16/04 - Foundation + Design Context (Done)

- Biden: đã chốt route/module map nền, API client skeleton, error contract chung.
- Doanh: đã dựng app shell/page templates, UI primitives v1, bộ state components và responsive baseline.
- Deliverable đã đạt:
    - Skeleton chạy ổn, render được toàn bộ module khung.

## 17/04 - 18/04 - Integration Wave 1 (P0)

- Biden:
    - Tích hợp UC02: `/auth/login`, `/auth/logout`, `/auth/me`, `/auth/change-password`, `/auth/refresh`.
    - Tích hợp UC03: `/transactions/submit`, `/transactions`, `/transactions/{txn_id}`, `/transactions/{txn_id}/state-history`.
    - Tích hợp UC05: `/cases`, `/cases/{case_id}`, `/cases/{case_id}/assign`, `/cases/{case_id}/decision`.
    - Hoàn thiện unauthorized/forbidden flow theo role.
- Doanh:
    - Cập nhật form/list/detail UI theo payload thật của UC02/03/05.
    - Chuẩn hóa trạng thái loading/empty/error cho các page P0.
    - Chạy smoke test vòng 1 sau mỗi gói tích hợp.
- Deliverable cuối 18/04:
    - UC02/03/05 chạy end-to-end với API thật, không còn phụ thuộc mock cho luồng chính.

## 19/04 - 20/04 - Integration Wave 2 (P1 - Part A)

- Biden:
    - Tích hợp UC04: `/users`, `/users/{user_id}`, create/enable/disable/update-role.
    - Tích hợp UC06: `/loans`, `/loans/{loan_id}`, `/loans/simulate`, `/loans/{loan_id}/decision`.
    - Tích hợp UC07: `/audit-logs`, `/audit-logs/entities/{entity_type}/{entity_id}`, `/audit-logs/{log_id}`.
    - Xử lý conflict 409 cho endpoint có `version`.
- Doanh:
    - Hoàn thiện page-level UI cho User/Loan/Audit theo field thực tế.
    - Chuẩn hóa format tiền tệ, score, timestamp UTC -> local display.
    - Rà responsive cho các page newly integrated.
- Deliverable cuối 20/04:
    - UC04/06/07 cắm API đầy đủ, pass smoke test vòng 1.

## 21/04 - Integration Wave 3 (P1 - Part B) + Stabilize

- Biden:
    - Tích hợp UC08: `/dashboard/summary`, `/dashboard/fraud-trend`, `/reports/transactions`, `/reports/fraud`.
    - Tích hợp UC09: `/etl/run`, `/etl/logs` + guard ADMIN.
    - Chốt hành vi export csv/json, pagination chuẩn, mapping error envelope chung.
- Doanh:
    - Hoàn thiện chart/card/table bind dữ liệu thật cho UC08.
    - Hoàn thiện ETL logs/admin shell theo dữ liệu thật.
    - Smoke test toàn hệ thống sau wave 3.
- Deliverable cuối 21/04:
    - Toàn bộ UC02 -> UC09 đã tích hợp API ở mức production-ready (chưa tính polish sâu).

## 22/04 - 23/04 - Testing + Bugfix (40% effort trọng tâm)

- Biden:
    - Owner bug triage, fix bug high/critical.
    - Regression trọng điểm: RBAC matrix, token refresh, state transition, optimistic locking, API failure fallback.
- Doanh:
    - Chạy full checklist manual, log bug kèm reproduce steps rõ ràng.
    - Fix bug UI low-risk (layout/text/format/consistency), re-test xác nhận bug đóng.
- Deliverable cuối 23/04:
    - Bug critical = 0, bug high đã fix hoặc có workaround được chấp nhận.

## 24/04 - Hardening + Handoff

- Biden:
    - Final regression pass, technical sign-off, chốt danh sách known issues (nếu có).
- Doanh:
    - Chốt checklist test, cập nhật ảnh/chứng cứ test flow chính.
- Deliverable cuối 24/04:
    - Sẵn sàng bàn giao UAT, flow chính hoạt động ổn định theo API_DESIGN v1.0.0.

## 6) Ma trận module x owner

| Module                 | Biden (High-risk owner)                                         | Doanh (Low-risk support)                           |
| ---------------------- | --------------------------------------------------------------- | -------------------------------------------------- |
| UC02 Auth              | Auth flow, token lifecycle, RBAC guard                          | Login/change-password UI, state/error view         |
| UC03 Transaction       | Submit/list/detail/state-history logic                          | Table/filter/detail presentational, format display |
| UC04 User Management   | Role/permission logic, enable/disable/update-role               | User list/form UI, static validation text          |
| UC05 Case Management   | Assign/decision flow, required note, conflict handling          | Case list/detail UI, timeline rendering            |
| UC06 Loan Management   | Loan decision flow, simulate/decision mapping, version conflict | Loan form/list/detail UI, scoring/result display   |
| UC07 Audit Logging     | Filter/query mapping, entity trail logic                        | Audit table/detail UI, pagination shell            |
| UC08 Dashboard/Reports | KPI/trend mapping, export behavior                              | Chart/card shell, table/report presentation        |
| UC09 ETL Pipeline      | Trigger/log integration, admin-only guard                       | ETL log UI/status chip/filter presentation         |

## 7) Cơ chế kiểm soát tiến độ và rủi ro

- Daily 2 checkpoints:
    - 10:00: chốt mục tiêu ngày + blocker với backend.
    - 17:30: demo increment + bug list + kế hoạch ngày tiếp theo.
- Quy tắc merge:
    - PR ảnh hưởng nghiệp vụ/kiến trúc: Biden review + merge.
    - PR low-risk từ Doanh: phải qua smoke test trước khi vào nhánh chính.
- Fallback khi API thay đổi muộn:
    - Ưu tiên sửa adapter layer trước.
    - Freeze UI behavior cho flow chính, đẩy polish xuống sau.

## 8) Definition of Done (cutoff 24/04)

- UC02 -> UC09 hoàn thiện UI + integration theo API_DESIGN v1.0.0.
- RBAC hoạt động đúng theo role matrix trên flow chính.
- Hỗ trợ đầy đủ các hành vi bắt buộc: pagination chuẩn, error envelope chuẩn, optimistic locking cho case/loan.
- Bug critical = 0; bug high không chặn demo/UAT.
- Bộ test (manual + automated khả dụng) đã chạy xong, có biên bản và sẵn sàng handoff backend/UAT.
