-- 测试数据: 占卜记录样例(供前端联调与测试用例引用; paipan_result为占位结构,
-- 正式黄金用例的期望值由测试工程师在 tests/golden/ 中独立维护, 不以此为基准)
BEGIN;
INSERT INTO divination_record(uuid,question_category,question_text,yaos,datetime_cast,paipan_result) VALUES
('11111111-1111-1111-1111-111111111111','事业','工作变动可否','787878','2026-06-11T10:30:00+08:00','{"placeholder":true}'),
('22222222-2222-2222-2222-222222222222','感情',NULL,'987788','2026-06-10T23:15:00+08:00','{"placeholder":true,"note":"23点后换日边界用例"}'),
('33333333-3333-3333-3333-333333333333','其他','六爻全动极端用例','999999','2026-02-04T05:00:00+08:00','{"placeholder":true,"note":"立春节气交接日用例"}');
COMMIT;
