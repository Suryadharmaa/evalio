"""Zero token writing diagnostics for the hybrid essay review."""

import hashlib
import re
from collections import Counter

from api.admission_engine.text.metrics import (
    TRANSITIONS,
    analyze_text,
    paragraphs,
    sentences,
    words,
)

ANALYSIS_VERSION = "essay-hybrid-1.0"
RUBRIC_VERSION = "essay-semantic-1.0"
STOP_WORDS = frozenset(
    ["a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "from", "had", "has", "have", "he", "her", "his", "i", "in", "is", "it", "its", "me", "my", "of", "on", "or", "our", "she", "that", "the", "their", "them", "they", "this", "to", "was", "we", "were", "what", "when", "where", "which", "who", "will", "with", "you", "your"]
)


def normalize_essay(essay: str) -> str:
    return "\n".join(line.strip() for line in essay.replace("\r\n", "\n").split("\n")).strip()


def essay_hash(essay: str) -> str:
    return hashlib.sha256(normalize_essay(essay).encode("utf-8")).hexdigest()


def validate_essay(essay: str) -> str:
    normalized = normalize_essay(essay)
    if "\x00" in normalized or any(ord(char) < 32 and char not in "\n\t" for char in normalized):
        raise ValueError("Paste plain essay text; binary input is not supported.")
    count = len(words(normalized))
    if count < 50 or count > 5000:
        raise ValueError("Essay must contain between 50 and 5,000 words.")
    if any(not paragraph.strip() for paragraph in re.split(r"\n\s*\n", normalized)):
        raise ValueError("Remove empty paragraphs before analysis.")
    text_paragraphs = paragraphs(normalized)
    if len(text_paragraphs) >= 3:
        canonical = [" ".join(part.casefold().split()) for part in text_paragraphs]
        if len(set(canonical)) / len(canonical) < 0.6:
            raise ValueError("Essay contains excessive duplicated paragraphs.")
    return normalized


def _label(score: int) -> str:
    return "Excellent" if score >= 90 else "Strong" if score >= 80 else "Good" if score >= 70 else "Moderate" if score >= 60 else "Needs attention"


def local_analysis(essay: str) -> dict[str, object]:
    metrics = analyze_text(essay)
    sentence_list = sentences(essay)
    paragraph_list = paragraphs(essay)
    lengths = metrics.sentence_lengths
    bands = Counter(
        "short" if length < 10 else "medium" if length <= 20 else "long" if length <= 30 else "very_long"
        for length in lengths
    )
    if len(lengths) < 4:
        variety = 75
    else:
        variety = round(max(40, min(100, 55 + len(bands) * 11 - max(0, max(bands.values()) / len(lengths) - 0.6) * 30)))
    tokens = [token.casefold() for token in words(essay) if token.casefold() not in STOP_WORDS]
    windows = [tokens[start : start + 50] for start in range(0, len(tokens), 50)]
    ratios = [len(set(window)) / len(window) for window in windows if window]
    diversity = round(max(0, min(100, (sum(ratios) / len(ratios)) * 100))) if ratios else 0
    openings = Counter(" ".join(words(item)[:2]).casefold() for item in sentence_list)
    repeated_openings = [item for item, count in openings.items() if item and count >= 3]
    repeated_phrases = list(metrics.repeated_phrases)[:5]
    transition_openings = Counter(
        first for sentence in sentence_list
        if (first := (words(sentence)[:1] or [""])[0].casefold()) in TRANSITIONS
    )
    repeated_transitions = [item for item, count in transition_openings.items() if count >= 3]
    repetition_count = sum(metrics.repeated_phrases.values()) + len(repeated_openings) + len(repeated_transitions)
    repetition = "High" if repetition_count >= 6 else "Moderate" if repetition_count >= 3 else "Low"
    # Flesch is meaningful only for English text; keep this diagnostic separate from the score.
    reading_ease = metrics.flesch_reading_ease
    readability = round(max(0, min(100, reading_ease))) if reading_ease is not None else None
    ratios_by_paragraph = [round(len(words(item)) / metrics.word_count, 3) for item in paragraph_list]
    structural_flags = []
    if ratios_by_paragraph[0] < 0.05 and metrics.paragraph_count > 2:
        structural_flags.append("Very short opening")
    if ratios_by_paragraph[0] > 0.35:
        structural_flags.append("Long opening")
    if ratios_by_paragraph[-1] > 0.35 and metrics.paragraph_count > 1:
        structural_flags.append("Long conclusion")
    if max(ratios_by_paragraph) > 0.45:
        structural_flags.append("One paragraph dominates the essay")
    return {
        "word_count": metrics.word_count,
        "character_count": metrics.character_count,
        "paragraph_count": metrics.paragraph_count,
        "sentence_count": metrics.sentence_count,
        "average_words_per_sentence": metrics.average_sentence_length,
        "average_sentences_per_paragraph": round(metrics.sentence_count / max(1, metrics.paragraph_count), 2),
        "longest_sentence_words": max(lengths, default=0),
        "shortest_sentence_words": min(lengths, default=0),
        "sentence_length_buckets": dict(bands),
        "sentence_variety": {"score": variety, "label": _label(variety)},
        "vocabulary_diversity": {"score": diversity, "label": _label(diversity)},
        "readability": {"score": readability, "label": _label(readability) if readability is not None else "Unavailable"},
        "repetition": {"label": repetition, "repeated_phrases": repeated_phrases, "repeated_openings": repeated_openings[:5], "repeated_transitions": repeated_transitions},
        "structure": {
            "opening_ratio": ratios_by_paragraph[0],
            "conclusion_ratio": ratios_by_paragraph[-1],
            "largest_paragraph_ratio": max(ratios_by_paragraph),
            "flags": structural_flags,
        },
    }
