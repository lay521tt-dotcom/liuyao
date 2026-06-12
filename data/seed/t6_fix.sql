-- T6双源比对裁定后的我方修正(21处) + 爻题残留清理
BEGIN;
UPDATE hexagram SET gua_ci=replace(gua_ci,'初噬告','初筮告') WHERE id=4;
UPDATE hexagram SET gua_ci=replace(gua_ci,'小利有所往','小利有攸往') WHERE id=22;
UPDATE yao_text SET yao_ci=replace(yao_ci,'既鹿无虞','即鹿无虞') WHERE hexagram_id=3 AND line_position=3;
UPDATE yao_text SET yao_ci=replace(yao_ci,'求婚媾，无不利','求婚媾，往吉，无不利') WHERE hexagram_id=3 AND line_position=4;
UPDATE yao_text SET yao_ci=replace(yao_ci,'复自命','复即命') WHERE hexagram_id=6 AND line_position=4;
UPDATE yao_text SET yao_ci=replace(yao_ci,'邑人不戒','邑人不诫') WHERE hexagram_id=8 AND line_position=5;
UPDATE yao_text SET yao_ci=replace(yao_ci,'以其夤','以其汇') WHERE hexagram_id=11 AND line_position=1;
UPDATE yao_text SET yao_ci=replace(yao_ci,'以其夤','以其汇') WHERE hexagram_id=12 AND line_position=1;
UPDATE yao_text SET yao_ci=replace(yao_ci,'履校灭趾','屦校灭趾') WHERE hexagram_id=21 AND line_position=1;
UPDATE yao_text SET yao_ci=replace(yao_ci,'无只悔','无祗悔') WHERE hexagram_id=24 AND line_position=1;
UPDATE yao_text SET yao_ci=replace(yao_ci,'舆说辐','舆说輹') WHERE hexagram_id=26 AND line_position=2;
UPDATE yao_text SET yao_ci=replace(yao_ci,'与丘颐','于丘颐') WHERE hexagram_id=27 AND line_position=2;
UPDATE yao_text SET yao_ci=replace(yao_ci,'只既平','祗既平') WHERE hexagram_id=29 AND line_position=5;
UPDATE yao_text SET yao_ci=replace(yao_ci,'获其匪丑','获匪其丑') WHERE hexagram_id=30 AND line_position=6;
UPDATE yao_text SET yao_ci=replace(yao_ci,'三岁不见','三岁不觌') WHERE hexagram_id=47 AND line_position=1;
UPDATE yao_text SET yao_ci=replace(yao_ci,'利用亨祀','利用享祀') WHERE hexagram_id=47 AND line_position=2;
UPDATE yao_text SET yao_ci=replace(yao_ci,'为我民恻','为我心恻') WHERE hexagram_id=48 AND line_position=3;
UPDATE yao_text SET yao_ci=replace(yao_ci,'鸿渐于逵','鸿渐于陆') WHERE hexagram_id=53 AND line_position=6;
UPDATE yao_text SET yao_ci=replace(yao_ci,'日中见昧','日中见沫') WHERE hexagram_id=55 AND line_position=3;
UPDATE yao_text SET yao_ci=replace(yao_ci,'三岁不见','三岁不觌') WHERE hexagram_id=55 AND line_position=6;
UPDATE yao_text SET yao_ci=replace(yao_ci,'有他不燕','有它不燕') WHERE hexagram_id=61 AND line_position=1;
-- 爻题残留清理(如"六二：鸣谦…")
UPDATE yao_text SET yao_ci=regexp_replace(yao_ci,'^(初[九六]|上[九六]|[九六][二三四五]|用[九六])[：:]','');
COMMIT;
