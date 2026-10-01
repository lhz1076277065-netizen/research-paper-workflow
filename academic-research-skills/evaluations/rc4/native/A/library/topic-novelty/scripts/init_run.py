#!/usr/bin/env python3
"""Create a new, explicitly unfinished standalone skill run. Never overwrite."""
from __future__ import annotations
import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    parser.add_argument('--request', default='', help='Actual requested scope, not an invented project')
    args = parser.parse_args()
    skill = Path(__file__).resolve().parents[1]
    dest = args.destination.resolve()
    try:
        template = json.loads((skill / 'assets/run.template.json').read_text(encoding='utf-8'))
        cfg = json.loads((skill / 'assets/contract.json').read_text(encoding='utf-8'))
        # Refuse existing directories so an accidental rerun cannot destroy data.
        dest.mkdir(parents=True, exist_ok=False)
        stamp = datetime.now(timezone.utc).isoformat()
        template.update(run_id='RUN-' + uuid.uuid4().hex[:16], created_at=stamp,
                        updated_at=stamp, request=args.request)
        (dest / 'outputs').mkdir()
        (dest / cfg['records_file']).write_text('', encoding='utf-8')
        (dest / 'run.json').write_text(json.dumps(template, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        (dest / 'RUN_README.md').write_text(
            '# 尚未完成的研究工作单元\n\n此目录仅被初始化；没有生成研究证据、图表或论文。\n'
            '完成实际工作后，在 run.json 登记真实产物、哈希、来源与门槛证据。\n'
            '任务记录写入 ' + cfg['records_file'] + '；模板在 Skill 的 assets 中。\n'
            '不需要总控或相邻 Skill。结构通过不等于研究完成或投稿就绪。\n', encoding='utf-8')
        print(json.dumps({'status':'initialized_not_completed','directory':str(dest),
                          'skill':cfg['skill']},ensure_ascii=False))
        return 0
    except (OSError, ValueError, TypeError) as exc:
        print(f'Initialization failed: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
