#!/usr/bin/env python3
"""Flag formulaic, conversational, promotional, and drafting residue in manuscripts."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import zipfile
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree


SUPPORTED_EXTENSIONS = {".md", ".markdown", ".txt", ".rst", ".tex", ".html", ".htm", ".docx"}
SEVERITY_RANK = {"low": 1, "medium": 2, "high": 3}


@dataclass(frozen=True)
class Rule:
    rule_id: str
    severity: str
    category: str
    pattern: str
    guidance: str


@dataclass(frozen=True)
class Finding:
    file: str
    location: str
    severity: str
    category: str
    rule_id: str
    match: str
    excerpt: str
    guidance: str


EN_RULES = (
    Rule("assistant_identity", "high", "assistant-residue", r"\bas an (?:ai|artificial intelligence) (?:language )?model\b", "Remove assistant identity language."),
    Rule("assistant_capability", "high", "assistant-residue", r"\bI (?:cannot|can't|do not have access|don't have access|am unable to)\b", "Replace capability commentary with manuscript content or remove it."),
    Rule("response_preamble", "high", "assistant-residue", r"(?:^|[.!?]\s+)(?:certainly|sure)[,!]?\s+(?:here|below)\b|\bhere (?:is|are) (?:the|a) (?:revised|final|requested|complete)\b", "Delete response preambles and retain only manuscript prose."),
    Rule("offer_more_help", "high", "assistant-residue", r"\b(?:feel free to|let me know if|I hope this helps)\b", "Remove conversational offers or reassurance."),
    Rule("editing_instruction", "high", "drafting-residue", r"\b(?:the author|you) should (?:add|insert|discuss|cite|verify|rewrite|revise|explain|clarify)\b|\b(?:add|insert) (?:a )?(?:citation|reference|figure|table) here\b", "Perform the edit; do not leave instructions in the manuscript."),
    Rule("placeholder_token", "high", "drafting-residue", r"\b(?:TODO|TBD|TK|lorem ipsum)\b|\[(?:insert|add|provide|describe|citation needed|reference needed|author(?: name)?|affiliation|institution|date|title|keywords?|x{2,})[^\]]*\]", "Replace or remove the placeholder."),
    Rule("submission_claim", "high", "drafting-residue", r"\b(?:the manuscript|this paper) is (?:now )?(?:ready for submission|submission-ready|publishable)\b", "Keep readiness decisions outside the scholarly manuscript."),
    Rule("reader_direction", "medium", "reader-directed", r"\b(?:as you can see|you can see|please note|remember that|note that the reader|the reader should)\b", "State the evidence or inference directly without directing the reader."),
    Rule("conversational_simplifier", "medium", "conversational", r"\b(?:of course|needless to say|simply put|in a nutshell|basically|to put it simply)\b", "Replace casual simplification with a precise statement."),
    Rule("collective_observation", "medium", "conversational", r"\bwe can (?:clearly )?(?:see|observe|notice)\b", "Name the observed result and its evidentiary basis directly."),
    Rule("rhetorical_prompt", "medium", "reader-directed", r"\b(?:consider|imagine) (?:for a moment|a scenario|the following)\b", "Replace rhetorical prompting with a direct analytical statement."),
    Rule("future_section_announcement", "medium", "empty-metadiscourse", r"\b(?:this|the following) section (?:will|aims to|seeks to) (?:discuss|describe|explain|explore|present|provide|examine)\b", "Replace the section announcement with its substantive claim."),
    Rule("section_purpose_announcement", "medium", "empty-metadiscourse", r"\bthe purpose of this section is to\b|\bthis paper is (?:organized|structured) as follows\b", "Keep navigation only when structurally necessary; otherwise state the substantive relationship."),
    Rule("note_formula", "medium", "empty-metadiscourse", r"\bit (?:is|should be) (?:important |also )?(?:(?:worth noting|important to note|noted) that|worth noting that)\b", "State the proposition directly and explain its relevance if needed."),
    Rule("clarity_formula", "medium", "empty-metadiscourse", r"\b(?:for (?:the sake of )?clarity|to make (?:this|it) (?:clearer|easier to understand))\b", "Remove the announcement and make the explanation itself precise."),
    Rule("above_below_reference", "medium", "empty-metadiscourse", r"\b(?:as|the) (?:mentioned|discussed|described|shown|stated) (?:above|below)\b", "Use a section, equation, table, or figure reference, or state the relationship directly."),
    Rule("formulaic_landscape", "medium", "formulaic-language", r"\b(?:rapidly evolving|ever-changing|dynamic) landscape\b", "Replace the ornamental context with the specific change and evidence."),
    Rule("formulaic_delving", "medium", "formulaic-language", r"\b(?:delve|delves|delved|delving) (?:into|deeper into)\b", "Use the precise analytical action performed."),
    Rule("formulaic_realm", "medium", "formulaic-language", r"\bin the realm of\b|\bwithin the realm of\b", "Name the field, setting, or scope directly."),
    Rule("formulaic_tapestry", "medium", "formulaic-language", r"\b(?:rich|complex|intricate) tapestry\b", "Replace metaphor with the specific components or relationships."),
    Rule("formulaic_interplay", "medium", "formulaic-language", r"\bintricate interplay\b", "Specify the variables, mechanisms, or dependencies."),
    Rule("formulaic_underscore", "medium", "formulaic-language", r"\b(?:underscores?|highlights?) the (?:critical|crucial|vital|paramount|pivotal) (?:importance|role|need)\b", "State the supported implication and its scope directly."),
    Rule("formulaic_crucial_role", "medium", "formulaic-language", r"\bplays? a (?:critical|crucial|vital|pivotal|paramount) role\b", "Specify the mechanism, contribution, or measured association."),
    Rule("promotional_superlative", "medium", "promotional", r"\b(?:groundbreaking|revolutionary|game-changing|transformative|unprecedented|remarkable|outstanding|highly innovative|cutting-edge|seamless|seamlessly|powerful)\b", "Replace promotion with a measured comparison or remove it."),
    Rule("comprehensive_claim", "medium", "unsupported-evaluation", r"\bcomprehensive (?:analysis|assessment|evaluation|framework|overview|review|study|approach)\b", "Define the coverage criteria or replace the unqualified completeness claim."),
    Rule("unsupported_certainty", "medium", "unsupported-evaluation", r"\b(?:obviously|undoubtedly|indisputably|without question|it is clear that)\b", "Provide evidence and calibrated certainty instead of assertion."),
    Rule("vague_success", "medium", "unsupported-evaluation", r"\b(?:highly|exceptionally|remarkably) (?:robust|accurate|effective|efficient|reliable|successful|superior)\b", "Report the metric, comparator, uncertainty, and conditions."),
    Rule("evaluative_predicate", "medium", "unsupported-evaluation", r"\b(?:is|are|was|were|remained|proved) (?:robust|accurate|effective|efficient|reliable|successful|superior)\b", "Confirm that the metric, comparator, uncertainty, and conditions immediately support this evaluation."),
    Rule("informal_contraction", "low", "conversational", r"\b(?:can't|won't|isn't|aren't|doesn't|don't|didn't|it's|we're|they're|there's)\b", "Use formal wording unless the text is a quotation."),
)

ZH_RULES = (
    Rule("zh_assistant_identity", "high", "assistant-residue", r"作为(?:一个|一名)?(?:AI|人工智能)(?:语言)?模型", "删除 AI 助手身份话术。"),
    Rule("zh_assistant_capability", "high", "assistant-residue", r"(?:我无法|我不能|我没有权限|我无法访问)", "删除能力说明，改为论文事实或明确的数据限制。"),
    Rule("zh_response_preamble", "high", "assistant-residue", r"(?:以下是|下面是)(?:为您)?(?:修改|润色|生成|整理|撰写)(?:后)?的", "删除回复前言，只保留论文正文。"),
    Rule("zh_offer_help", "high", "assistant-residue", r"(?:如有需要|如果您需要|希望对您有所帮助|欢迎继续提问)", "删除面向用户的帮助或邀约。"),
    Rule("zh_editing_instruction", "high", "drafting-residue", r"(?:请|建议)(?:作者)?(?:补充|添加|插入|修改|核实|引用|讨论)|(?:此处|这里)(?:需要|应当)?(?:插入|添加|补充)", "直接完成修改，不在稿件中保留编辑指令。"),
    Rule("zh_placeholder", "high", "drafting-residue", r"(?:待补充|待完善|待核实|待引用|占位符)|[【\[](?:补充|插入|添加|作者|单位|日期|题目|关键词|引用)[^】\]]*[】\]]", "补全或删除占位内容。"),
    Rule("zh_reader_direction", "medium", "reader-directed", r"(?:读者可以|大家可以|我们可以)(?:清楚地|明显地)?(?:看到|看出|发现|注意到)", "直接陈述观察结果及证据。"),
    Rule("zh_obviousness", "medium", "unsupported-evaluation", r"(?:众所周知|不难发现|显而易见|毋庸置疑|毫无疑问)", "以可核验依据替代常识或确定性断言。"),
    Rule("zh_note_formula", "medium", "empty-metadiscourse", r"(?:值得注意的是|需要指出的是|应当指出的是|必须强调的是)", "直接陈述命题及其学术意义。"),
    Rule("zh_section_announcement", "medium", "empty-metadiscourse", r"(?:本文|本节|下文)(?:首先|随后|接下来)?(?:会|将要|将)?(?:深入|全面)?(?:讨论|介绍|阐述|分析|探讨|说明)", "以具体研究内容或结果替代章节预告。"),
    Rule("zh_simplifier", "medium", "conversational", r"(?:简单来说|通俗地说|说白了|换句话说|当然|基本上)", "使用精确的学术陈述。"),
    Rule("zh_clarity_formula", "medium", "empty-metadiscourse", r"(?:为了便于理解|为了更清楚地说明|为清晰起见)", "删除说明性前缀并改写为清晰正文。"),
    Rule("zh_formulaic_development", "medium", "formulaic-language", r"随着.{0,24}(?:快速|迅速|不断|蓬勃)发展", "说明具体变化、时间和证据，避免宽泛开场。"),
    Rule("zh_formulaic_exploration", "medium", "formulaic-language", r"(?:深入探讨|全面系统地分析|多维度地揭示)", "写明具体分析对象、方法和结果。"),
    Rule("zh_promotional", "medium", "promotional", r"(?:开创性|颠覆性|革命性|里程碑式|前所未有|极具创新性|具有划时代意义)", "用量化比较、适用条件和证据替代宣传性判断。"),
    Rule("zh_vague_importance", "medium", "unsupported-evaluation", r"(?:具有|有着)(?:十分|非常|极其|重大)?重要(?:的)?(?:意义|价值|作用)", "明确理论、方法或实践影响及支持证据。"),
    Rule("zh_vague_success", "medium", "unsupported-evaluation", r"(?:大大|极大地|明显地)(?:提高|提升|改善|增强)|(?:非常|高度)(?:准确|可靠|稳健|有效|高效)", "报告指标、比较对象、不确定性和条件。"),
)

# Backward-compatible export for callers that imported RULES.
RULES = EN_RULES


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def read_text_file(path: Path) -> list[tuple[str, str]]:
    for encoding in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            text = path.read_text(encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError("unsupported text encoding")

    if path.suffix.lower() in {".html", ".htm"}:
        parser = TextExtractor()
        parser.feed(text)
        text = html.unescape("\n".join(parser.parts))

    return [(f"line {number}", line) for number, line in enumerate(text.splitlines(), start=1) if line.strip()]


def read_docx(path: Path) -> list[tuple[str, str]]:
    with zipfile.ZipFile(path) as archive:
        xml = archive.read("word/document.xml")
    root = ElementTree.fromstring(xml)
    namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    paragraphs: list[tuple[str, str]] = []
    for number, paragraph in enumerate(root.iter(f"{namespace}p"), start=1):
        text = normalize_space("".join(node.text or "" for node in paragraph.iter(f"{namespace}t")))
        if text:
            paragraphs.append((f"paragraph {number}", text))
    return paragraphs


def iter_files(inputs: Iterable[str], excludes: Iterable[str]) -> list[Path]:
    exclude_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in excludes]
    files: set[Path] = set()
    for item in inputs:
        path = Path(item).expanduser().resolve()
        candidates = path.rglob("*") if path.is_dir() else (path,)
        for candidate in candidates:
            if not candidate.is_file() or candidate.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue
            normalized = candidate.as_posix()
            if any(pattern.search(normalized) for pattern in exclude_patterns):
                continue
            files.add(candidate)
    return sorted(files)


def excerpt(text: str, start: int, end: int, width: int = 180) -> str:
    left = max(0, start - width // 2)
    right = min(len(text), end + width // 2)
    value = normalize_space(text[left:right])
    return ("..." if left else "") + value + ("..." if right < len(text) else "")


def select_rules(language: str, text: str) -> tuple[Rule, ...]:
    if language == "en":
        return EN_RULES
    if language == "zh":
        return ZH_RULES
    if language == "both":
        return EN_RULES + ZH_RULES
    chinese = len(re.findall(r"[\u3400-\u9fff]", text))
    english = len(re.findall(r"\b[A-Za-z]{3,}\b", text))
    if chinese >= 2 and english >= 3:
        return EN_RULES + ZH_RULES
    return ZH_RULES if chinese >= 2 else EN_RULES


def audit_file(path: Path, allow_patterns: list[re.Pattern[str]], language: str = "auto") -> list[Finding]:
    units = read_docx(path) if path.suffix.lower() == ".docx" else read_text_file(path)
    findings: list[Finding] = []
    for location, text in units:
        for rule in select_rules(language, text):
            for match in re.finditer(rule.pattern, text, flags=re.IGNORECASE | re.MULTILINE):
                if any(pattern.search(match.group(0)) for pattern in allow_patterns):
                    continue
                findings.append(Finding(
                    file=str(path),
                    location=location,
                    severity=rule.severity,
                    category=rule.category,
                    rule_id=rule.rule_id,
                    match=match.group(0),
                    excerpt=excerpt(text, match.start(), match.end()),
                    guidance=rule.guidance,
                ))
    return findings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", help="Manuscript files or directories to scan")
    parser.add_argument("--fail-on", choices=("high", "medium", "low", "none"), default="medium", help="Lowest severity that returns exit code 1")
    parser.add_argument("--allow", action="append", default=[], metavar="REGEX", help="Reviewed exact-match regex to suppress; repeat as needed")
    parser.add_argument("--exclude", action="append", default=[], metavar="REGEX", help="Path regex to exclude; repeat as needed")
    parser.add_argument("--language", choices=("auto", "en", "zh", "both"), default="auto", help="Language rules to apply")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        allow_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in args.allow]
        files = iter_files(args.inputs, args.exclude)
        if not files:
            raise ValueError("no supported manuscript files found")
        findings: list[Finding] = []
        errors: list[dict[str, str]] = []
        for path in files:
            try:
                findings.extend(audit_file(path, allow_patterns, args.language))
            except (OSError, ValueError, KeyError, zipfile.BadZipFile, ElementTree.ParseError) as error:
                errors.append({"file": str(path), "error": str(error)})
    except (OSError, ValueError, re.error) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    findings.sort(key=lambda item: (-SEVERITY_RANK[item.severity], item.file, item.location, item.rule_id))
    counts = {severity: sum(item.severity == severity for item in findings) for severity in ("high", "medium", "low")}

    if args.json:
        print(json.dumps({
            "files_scanned": len(files),
            "language": args.language,
            "counts": counts,
            "findings": [asdict(item) for item in findings],
            "errors": errors,
        }, indent=2, ensure_ascii=False))
    else:
        for item in findings:
            print(f"{item.severity.upper()} [{item.category}/{item.rule_id}] {item.file}:{item.location}")
            print(f"  Match: {item.match}")
            print(f"  Context: {item.excerpt}")
            print(f"  Action: {item.guidance}")
        for error in errors:
            print(f"ERROR {error['file']}: {error['error']}", file=sys.stderr)
        print(f"Scanned {len(files)} file(s): high={counts['high']} medium={counts['medium']} low={counts['low']} errors={len(errors)}")

    if errors:
        return 2
    if args.fail_on == "none":
        return 0
    threshold = SEVERITY_RANK[args.fail_on]
    return 1 if any(SEVERITY_RANK[item.severity] >= threshold for item in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
