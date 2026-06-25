#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

WORD_RE = re.compile(r"\b[A-Za-z][A-Za-z'-]*\b")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
TRANSITIONS = [
    "moreover",
    "furthermore",
    "in addition",
    "however",
    "therefore",
    "consequently",
    "taken together",
    "it is important to note",
    "in this context",
    "as a result",
]
PARAGRAPH_START_TRANSITIONS = [
    "however",
    "therefore",
    "moreover",
    "furthermore",
    "in addition",
    "at the same time",
    "for this reason",
    "as a result",
    "taken together",
]
CONTRIBUTION_FORMULAS = [
    "the paper makes three contributions",
    "this paper makes three contributions",
    "this study makes three contributions",
    "the paper contributes in three ways",
    "this study contributes in three ways",
    "first,",
    "second,",
    "third,",
]
CAVEAT_MARKERS = [
    "does not attempt",
    "cannot decide",
    "cannot be turned into",
    "not the same as",
    "should not be",
    "rather than",
    "but it also",
    "still",
]
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def read_docx(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        xml = archive.read("word/document.xml")
    root = ET.fromstring(xml)
    paragraphs = []
    for para in root.findall(".//w:body/w:p", NS):
        text = "".join(node.text or "" for node in para.findall(".//w:t", NS)).strip()
        if text:
            paragraphs.append(text)
    return "\n\n".join(paragraphs)


def read_input(path: Path) -> str:
    if path.suffix.lower() == ".docx":
        return read_docx(path)
    return path.read_text(encoding="utf-8")


def syllable_count(word: str) -> int:
    cleaned = re.sub(r"[^a-z]", "", word.lower())
    if not cleaned:
        return 0
    groups = len(re.findall(r"[aeiouy]+", cleaned))
    if cleaned.endswith("e") and not cleaned.endswith(("le", "ye")) and groups > 1:
        groups -= 1
    return max(1, groups)


def sentence_metrics(body: str) -> dict:
    sentences = [s.strip() for s in SENTENCE_SPLIT_RE.split(body) if WORD_RE.search(s)]
    lengths = [len(WORD_RE.findall(s)) for s in sentences]
    words = WORD_RE.findall(body)
    syllables = sum(syllable_count(w) for w in words)
    complex_words = sum(syllable_count(w) >= 3 for w in words)
    word_count = max(1, len(words))
    sentence_count = max(1, len(sentences))
    flesch = 206.835 - 1.015 * (word_count / sentence_count) - 84.6 * (syllables / word_count)
    fk_grade = 0.39 * (word_count / sentence_count) + 11.8 * (syllables / word_count) - 15.59
    fog = 0.4 * ((word_count / sentence_count) + 100 * complex_words / word_count)
    return {
        "words": len(words),
        "sentences": len(sentences),
        "sentence_length_mean": round(statistics.mean(lengths), 2) if lengths else 0,
        "sentence_length_stdev": round(statistics.pstdev(lengths), 2) if lengths else 0,
        "sentence_length_min": min(lengths, default=0),
        "sentence_length_max": max(lengths, default=0),
        "sentences_over_35_words": sum(n > 35 for n in lengths),
        "sentences_under_9_words": sum(n < 9 for n in lengths),
        "flesch_reading_ease_estimate": round(flesch, 2),
        "flesch_kincaid_grade_estimate": round(fk_grade, 2),
        "gunning_fog_estimate": round(fog, 2),
    }


def citation_metrics(body: str, references: str) -> dict:
    reference_pairs = set()
    for line in references.splitlines():
        match = re.match(r"^([A-Z][^\n]+?) \((\d{4})\)\.", line.strip())
        if match:
            reference_pairs.add((match.group(1).split(",")[0].strip(), match.group(2)))

    citations = set()
    for group in re.findall(r"\(([^()]*(?:19|20)\d{2}[^()]*)\)", body):
        for item in group.split(";"):
            match = re.search(r"([A-Z][A-Za-z.& -]+?)(?: et al\.)?,?\s*((?:19|20)\d{2})", item.strip())
            if match:
                citations.add((match.group(1).strip().split()[0], match.group(2)))
    for match in re.finditer(r"([A-Z][A-Za-z]+)(?: et al\.)? \(((?:19|20)\d{2})\)", body):
        citations.add((match.group(1), match.group(2)))

    for author, year in reference_pairs:
        author_text = author.rstrip(".")
        pattern = rf"{re.escape(author_text)}\.?\s+\([^)]*\b{year}\b[^)]*\)"
        if re.search(pattern, body):
            citations.add((author, year))

    missing = sorted(citations - reference_pairs)
    uncited = sorted(reference_pairs - citations)
    return {
        "in_text_citation_pairs": len(citations),
        "reference_entries_detected": len(reference_pairs),
        "citations_missing_from_references": missing,
        "references_not_cited_in_text": uncited,
    }


def repeated_ngrams(body: str, n: int = 4) -> list[dict]:
    words = [w.lower() for w in WORD_RE.findall(body)]
    counts: dict[str, int] = {}
    for index in range(len(words) - n + 1):
        phrase = " ".join(words[index:index + n])
        counts[phrase] = counts.get(phrase, 0) + 1
    return [
        {"phrase": phrase, "count": count}
        for phrase, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        if count >= 3
    ][:20]


def template_metrics(body: str) -> dict:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if WORD_RE.search(p)]
    paragraph_starts: dict[str, int] = {}
    for paragraph in paragraphs:
        first_words = " ".join(WORD_RE.findall(paragraph.lower())[:5])
        for phrase in PARAGRAPH_START_TRANSITIONS:
            if first_words.startswith(phrase):
                paragraph_starts[phrase] = paragraph_starts.get(phrase, 0) + 1

    lower = body.lower()
    first_second_third_chain = all(token in lower for token in ["first,", "second,", "third,"])
    formula_hits = {
        phrase: lower.count(phrase)
        for phrase in CONTRIBUTION_FORMULAS
        if lower.count(phrase)
    }
    caveat_hits = {
        phrase: lower.count(phrase)
        for phrase in CAVEAT_MARKERS
        if lower.count(phrase)
    }
    paragraph_lengths = [len(WORD_RE.findall(p)) for p in paragraphs]
    return {
        "paragraph_count": len(paragraphs),
        "paragraph_length_words": paragraph_lengths,
        "paragraph_length_stdev": round(statistics.pstdev(paragraph_lengths), 2) if paragraph_lengths else 0,
        "paragraph_start_transitions": paragraph_starts,
        "contribution_formula_hits": formula_hits,
        "first_second_third_chain_present": first_second_third_chain,
        "caveat_marker_hits": caveat_hits,
    }


def audit(text: str, references_heading: str) -> dict:
    marker = re.search(rf"(?im)^\s*{re.escape(references_heading)}(?:\s*\([^\n]+\))?\s*$", text)
    if marker:
        body = text[:marker.start()]
        references = text[marker.end():]
    else:
        body = text
        references = ""

    lower = body.lower()
    return {
        "scope": {
            "references_heading_found": bool(marker),
            "body_characters": len(body),
        },
        "readability": sentence_metrics(body),
        "prose_patterns": {
            "transition_counts": {phrase: lower.count(phrase) for phrase in TRANSITIONS},
            "repeated_four_word_phrases": repeated_ngrams(body),
            "template_signals": template_metrics(body),
        },
        "citations": citation_metrics(body, references) if references else {
            "warning": "No references section detected; citation matching was skipped."
        },
        "interpretation": [
            "These diagnostics do not detect AI authorship.",
            "Revise only findings that weaken clarity, evidence, or citation integrity.",
            "Estimated readability formulas are approximate, especially for technical vocabulary.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit academic prose without AI-detector scoring.")
    parser.add_argument("input", type=Path, help="UTF-8 text or DOCX file")
    parser.add_argument("--references-heading", default="References")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    report = audit(read_input(args.input), args.references_heading)
    output = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        args.out.write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
