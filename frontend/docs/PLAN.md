# Frontend Delivery Plan (16/04 -> 24/04)

## 1) Bối cảnh và nguyên tắc lập kế hoạch

- Mục tiêu: hoàn thành toàn bộ frontend theo module lớn trước 24/04, đã test và sẵn sàng handoff.
- Ràng buộc: API chưa chốt hoàn toàn, chỉ bám module lớn; backend dự kiến hoàn tất full API trong 17-18/04.
- Quy mô nhân sự:
    - Biden (4/5, mạnh kỹ thuật + prompt + AI tools): nhận toàn bộ task rủi ro cao, task có thể làm sai logic nghiệp vụ, task ảnh hưởng critical path.
    - Doanh (1/5, mạnh research, code web mức cơ bản): chỉ nhận task rủi ro thấp, có thể review/replace nhanh, không được đứng trên critical path.
- Nguyên tắc điều phối:
    - Critical path do Biden nắm.
    - Doanh làm song song các phần UI/presentational/mocking/QA checklist để tăng throughput nhưng không khóa tiến độ.
    - Chấp nhận hardcode tạm + mock adapter trong giai đoạn chờ API.
    - Thời lượng testing + bugfix chiếm xấp xỉ 40% tổng thời gian.

## 2) Scope module (chỉ lấy module lớn từ API Design)

- UC02: Auth & Authorization.
- UC03: Transaction Management.
- UC05: Case Management & Audit.
- UC06: Dashboard, BI, Data/Reports.
- UC07: State History & Reconciliation.

Ghi chú: không lock theo endpoint chi tiết ở thời điểm này, chỉ lock theo module boundary để giảm rủi ro đổi API.

## 3) Flow thực hiện bắt buộc

1. Dùng Figma MCP để lấy style/context từ file thiết kế.
2. Dùng AI để đề xuất layout -> chuyển thành component map.
3. Dựng frontend hardcode + mock state trước khi API ổn định.
4. Khi API đủ (17-18/04), bắt đầu ghép API và sync chặt với backend.
5. Testing + bugfix là giai đoạn trọng tâm cuối, chiếm khoảng 40% effort.

## 4) Phân công theo vai trò và mức rủi ro

### 4.1 Biden (owner critical path, high-risk)

- Kiến trúc nền:
    - Router skeleton, route guard theo role, module boundary.
    - API layer chuẩn (axios client, error mapping, auth token handling, retry policy tối thiểu).
    - Query key strategy, mutation flow, cache invalidation.
- Nghiệp vụ nhạy cảm:
    - Luồng Auth/RBAC và điều hướng theo permission.
    - Luồng Transaction/Case state transition, approve/reject, note bắt buộc.
    - Mapping dữ liệu BI/Reconciliation có nhiều trạng thái và edge cases.
- Tích hợp backend:
    - Chốt contract thực tế với BE, tạo adapter cho khác biệt payload.
    - Xử lý lỗi, fallback UI, empty states, permission denied.
- Quality gate:
    - Thiết kế test strategy, viết test case rủi ro cao, điều phối bug triage cuối kỳ.

### 4.2 Doanh (owner low-risk, non-blocking)

- UI/presentational:
    - Dựng layout theo Figma (không xử lý business logic phức tạp).
    - Tạo reusable component low-risk: table shell, filter panel UI, badges, cards, skeletons, empty states.
    - Hoàn thiện responsive cơ bản cho các page chính.
- Hardcode/mocking:
    - Mock data và static page cho toàn bộ module để unblock demo flow.
    - Gắn wiring UI đơn giản bằng props, tránh tự thiết kế state machine.
- QA hỗ trợ:
    - Viết checklist test tay theo page.
    - Smoke test vòng 1 sau mỗi lần merge từ Biden.

Rule bắt buộc: task của Doanh không được yêu cầu quyết định kiến trúc, không nắm flow nghiệp vụ có side effect, không giữ khóa merge của release branch.

## 5) Kế hoạch theo mốc thời gian (16/04 -> 24/04)

## 16/04 - Foundation + Design Context

- Biden:
    - Lấy context style qua Figma MCP, chốt design token + component taxonomy.
    - Chốt route map và module map theo UC02/03/05/06/07.
    - Tạo skeleton API client + error contract chuẩn.
- Doanh:
    - Dựng base layout, khung trang, typography/spacing theo token đã chốt.
        - App shell v1:
            - Khung chung gồm header, sidebar, content container cho tất cả module.
            - Slot rõ ràng cho page title, breadcrumb, action area.
        - Page frame template:
            - Template cho list page (filter bar + table zone + pagination zone).
            - Template cho detail page (summary section + info section + timeline/activities section).
            - Template cho dashboard page (KPI row + chart row + secondary cards row).
            - Template cho form page (form body + action footer sticky).
        - Typography theo token:
            - Chốt mapping H1/H2/H3/body/caption theo semantic usage.
            - Không dùng font-size hardcode ngoài token map.
        - Spacing theo token:
            - Chốt spacing scale cho section, block, card, form-field, table-cell.
            - Chỉ dùng spacing token, hạn chế giá trị px rời.
        - Responsive baseline:
            - Desktop: sidebar mở mặc định.
            - Tablet: sidebar thu gọn, giữ hierarchy nội dung.
            - Mobile: stacked layout, action ưu tiên theo chiều dọc.
        - Acceptance criteria:
            - 5 module lớn đều render được trên cùng app shell.
            - Không có layout vỡ ở 3 breakpoint chính (mobile/tablet/desktop).
    - Tạo bộ component UI low-risk phiên bản v1.
        - Primitive components (presentational only):
            - Button, Input, Select, Textarea, Badge/StatusChip, Card, Modal shell.
        - Data display components:
            - TableShell, StatCard, KeyValueRow, TimelineItem, SectionHeader.
        - Navigation/filter components:
            - SearchBox UI, FilterBar UI, DateRange UI shell, Pagination UI.
        - State components:
            - LoadingSkeleton block, EmptyState block, ErrorState block (static).
        - Rules bắt buộc cho v1:
            - Chỉ nhận props; không gọi API, không chứa business logic quyết định trạng thái.
            - Không phụ thuộc store global; không side effect.
            - Tên component + props thống nhất, dễ thay mock bằng dữ liệu thật ở phase sau.
        - Output v1 cần bàn giao cuối ngày:
            - Danh sách component + props contract ngắn gọn.
            - 1 trang demo nội bộ thể hiện đầy đủ component states cơ bản.
- Deliverable:
    - Skeleton chạy được, có route khung cho 5 module lớn.

## 17/04 - 18/04 - Hardcode trước API

- Biden:
    - Dựng flow nghiệp vụ hardcode cho Auth + Transaction + Case actions.
    - Chuẩn bị adapter layer để cắm API nhanh khi BE chốt.
    - Define acceptance criteria cho từng module.
- Doanh:
    - Hoàn thiện UI page-level cho 5 module với mock data.
        - UC02 Auth/Authorization:
            - Login page (username/password, error text tĩnh, disabled button state).
            - Change password page (form layout + helper/error text tĩnh).
            - User management shell (list/filter UI tĩnh cho MANAGER/ADMIN view).
        - UC03 Transaction Management:
            - Transaction submit page (form UI, review block, result card tĩnh).
            - Transaction list page (table, filter bar, pagination UI tĩnh).
            - Transaction detail page (summary card, metadata panel, state history timeline UI).
        - UC05 Case Management & Audit:
            - Case list page (OPEN/ASSIGNED tabs, filter, assignee badge).
            - Case detail page (transaction snapshot, action panel approve/reject UI tĩnh).
            - Audit log page (event list/table, filter panel, trace drawer/modal UI).
        - UC06 BI/Data/Reports:
            - Dashboard summary page (KPI cards + trend chart placeholder).
            - Fraud chart page (period selector + chart container + legend).
            - Reports page (table report + export button UI tĩnh).
            - ETL logs/page admin shell (job list + status badge + trigger panel tĩnh).
        - UC07 State/Reconciliation:
            - Reconciliation jobs page (job list + status chips + date filter UI).
            - Reconciliation detail page (sources comparison + discrepancies section).
            - Transaction state history view (timeline/table component tái sử dụng).
        - Chuẩn đầu ra page-level:
            - Mỗi page có mock data riêng, tách file constants/mock rõ ràng.
            - Không gọi API thật, không cài business rule quyết định trạng thái.
            - Có responsive tối thiểu cho desktop + tablet + mobile.
    - Hoàn thiện states: loading/empty/error static.
        - Loading static:
            - Có skeleton cho table/list/card/form theo từng page.
            - Có loading placeholder cho chart (container + legend giả lập).
        - Empty static:
            - Empty message rõ ngữ cảnh (ví dụ: chưa có giao dịch/case/report).
            - Có CTA tĩnh hợp lý (refresh, clear filter, create first item).
        - Error static:
            - Error banner/card tĩnh theo 3 nhóm: network, unauthorized, unknown.
            - Có nút Retry UI tĩnh (chưa gắn action thật trong giai đoạn này).
        - Chuẩn chất lượng cho states:
            - Copy text ngắn gọn, không technical noise.
            - Trạng thái hiển thị nhất quán giữa các module (cùng pattern component).
            - Không để layout shift lớn khi chuyển giữa loading/empty/error/data.
    - Chuẩn bị checklist QA test tay vòng 1.
- Deliverable cuối 18/04:
    - Frontend demo full flow bằng hardcode/mock, không block bởi API.

## 19/04 - 20/04 - API Integration Wave 1

- Biden (chủ lực):
    - Ghép API Auth + Transaction + Case/Audit.
    - Resolve mismatch payload/status code với backend.
    - Bổ sung guard, error boundary, unauthorized flow.
- Doanh:
    - Support map field UI theo payload thực tế (low-risk only).
    - Cập nhật table/filter/display format.
    - Chạy smoke test sau từng gói tích hợp.
- Deliverable cuối 20/04:
    - Core module chạy end-to-end với API thật.

## 21/04 - API Integration Wave 2 + Stabilize

- Biden:
    - Ghép API Dashboard/Reports + Reconciliation.
    - Hoàn tất state history/reconciliation view logic.
    - Chốt toàn bộ edge-case handling.
- Doanh:
    - Hoàn thiện hiển thị chart/card/table theo dữ liệu thật.
    - Rà soát responsive và consistency UI.
- Deliverable:
    - Toàn bộ 5 module lớn đã cắm API mức production-ready (không gồm polish sâu).

## 22/04 - 24/04 - Testing + Bugfix (40% effort)

- Biden:
    - Owner bug triage, fix bug high/critical.
    - Tập trung regression cho role/permission, state transition, API failures.
    - Chốt test sign-off kỹ thuật trước cutoff.
- Doanh:
    - Chạy test checklist đầy đủ, ghi bug rõ reproduce steps.
    - Fix bug UI low-risk (spacing/text/format/display).
    - Re-test và xác nhận bug đóng.
- Deliverable cuối 24/04:
    - Test pass cho flow chính, bug critical = 0, bug high đã xử lý hoặc có workaround được chấp nhận.

## 6) Ma trận module x owner

| Module lớn                | Biden (High-risk owner)                                  | Doanh (Low-risk support)                                  |
| ------------------------- | -------------------------------------------------------- | --------------------------------------------------------- |
| UC02 Auth/Authorization   | Auth flow, RBAC guard, token/error handling              | Login/change-password UI, validation UI, empty/error view |
| UC03 Transaction          | Submit/list/detail/status logic, query/mutation strategy | Table/filter UI, detail panel layout, static formatting   |
| UC05 Case/Audit           | Assign/approve/reject logic, audit timeline mapping      | Case list/detail presentational, timeline component UI    |
| UC06 BI/Data              | Data mapping chart/report/export behavior                | Dashboard layout, card/chart shell, loading skeleton      |
| UC07 Reconciliation/State | History/reconciliation logic, mismatch handling          | Reconciliation table/report UI, visual states             |

## 7) Cơ chế kiểm soát tiến độ và rủi ro

- Daily 2 checkpoints:
    - 10:00: chốt mục tiêu trong ngày, xác nhận blocker với backend.
    - 17:30: demo increment, chốt bug list, cập nhật plan hôm sau.
- Quy tắc merge:
    - PR có ảnh hưởng nghiệp vụ/kiến trúc phải do Biden review và merge.
    - PR từ Doanh chỉ vào nhánh feature low-risk; không merge thẳng vào critical branch nếu chưa qua smoke test.
- Fallback khi API thay đổi muộn:
    - Giữ adapter layer để cô lập thay đổi contract.
    - Ưu tiên đảm bảo flow chính hoạt động trước, polish đẩy sau.

## 8) Definition of Done (cutoff 24/04)

- 5 module lớn hoàn thiện UI + integration theo mức API đã chốt.
- Quyền theo role hoạt động đúng trên flow chính.
- Không còn bug critical; bug high không chặn demo/UAT.
- Bộ test (manual + automated khả dụng) đã chạy xong và có biên bản kết quả.
- Sẵn sàng chuyển sang vòng UAT với backend.
