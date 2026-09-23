import re
from collections import Counter
from dataclasses import dataclass
from statistics import fmean, median, pstdev

WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)*")
SENTENCE_RE = re.compile(r"(?<=[.!?])(?:[\"'’”)]*)\s+")
REFLECTION_MARKERS = (
    "i realized",
    "i learned",
    "i began to understand",
    "i discovered",
    "i noticed",
    "i questioned",
    "looking back",
    "since then",
    "this taught me",
    "because of this",
)
FILLER_PHRASES = (
    "in order to",
    "due to the fact that",
    "at the end of the day",
    "it is important to note",
    "needless to say",
)
CLICHE_PHRASES = (
    "think outside the box",
    "changed my life",
    "dream come true",
    "never give up",
    "broadened my horizons",
    "stepping stone",
)
GENERIC_PHRASES = (
    "make a difference",
    "help people",
    "passionate about",
    "learned many things",
    "valuable experience",
)
TRANSITIONS = (
    "however",
    "therefore",
    "meanwhile",
    "instead",
    "although",
    "because",
    "afterward",
    "finally",
    "yet",
)


def words(text: str) -> list[str]:
    return WORD_RE.findall(text)


def sentences(text: str) -> list[str]:
    return [item.strip() for item in SENTENCE_RE.split(text.strip()) if item.strip()]


def paragraphs(text: str) -> list[str]:
    return [item.strip() for item in re.split(r"\n\s*\n", text.strip()) if item.strip()]


def _syllables(word: str) -> int:
    cleaned = re.sub(r"[^a-z]", "", word.lower())
    if not cleaned:
        return 0
    groups = re.findall(r"[aeiouy]+", cleaned)
    count = len(groups)
    if cleaned.endswith("e") and count > 1 and not cleaned.endswith(("le", "ye")):
        count -= 1
    return max(1, count)


def _phrase_counts(text: str, phrases: tuple[str, ...]) -> dict[str, int]:
    normalized = " ".join(words(text.lower()))
    return {
        phrase: len(re.findall(rf"\b{re.escape(phrase)}\b", normalized))
        for phrase in phrases
        if re.search(rf"\b{re.escape(phrase)}\b", normalized)
    }


@dataclass(frozen=True, slots=True)
class TextMetrics:
    word_count: int
    character_count: int
    sentence_count: int
    paragraph_count: int
    sentence_lengths: tuple[int, ...]
    paragraph_lengths: tuple[int, ...]
    average_sentence_length: float
    median_sentence_length: float
    sentence_length_stddev: float
    flesch_reading_ease: float | None
    lexical_diversity: float | None
    reflection_counts: dict[str, int]
    reflection_positions: tuple[int, ...]
    specificity_categories: frozenset[str]
    specificity_count: float
    filler_counts: dict[str, int]
    cliche_counts: dict[str, int]
    generic_counts: dict[str, int]
    repeated_phrases: dict[str, int]
    passive_sentence_count: int
    dialogue_present: bool
    transition_types: frozenset[str]


def analyze_text(text: str) -> TextMetrics:
    word_list = words(text)
    sentence_list = sentences(text)
    paragraph_list = paragraphs(text)
    sentence_lengths = tuple(len(words(item)) for item in sentence_list)
    paragraph_lengths = tuple(len(words(item)) for item in paragraph_list)
    word_count = len(word_list)
    syllables = sum(_syllables(word) for word in word_list)
    flesch = None
    if word_count and sentence_list:
        flesch = round(
            206.835 - 1.015 * (word_count / len(sentence_list)) - 84.6 * (syllables / word_count), 2
        )
    normalized_words = [word.lower() for word in word_list]
    reflection_counts = _phrase_counts(text, REFLECTION_MARKERS)
    normalized_text = " ".join(normalized_words)
    reflection_positions = tuple(
        normalized_text[: match.start()].count(" ")
        for marker in REFLECTION_MARKERS
        for match in re.finditer(rf"\b{re.escape(marker)}\b", normalized_text)
    )
    specificity: set[str] = set()
    if re.search(r"\b\d+(?:[.,]\d+)?\b", text):
        specificity.add("numbers")
    if re.search(
        r"\b(?:19|20)\d{2}\b|\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\b",
        text,
        re.I,
    ):
        specificity.add("date_time")
    if re.search(r"\b(?:at|in|from)\s+[A-Z][A-Za-z-]+", text):
        specificity.add("place")
    if re.search(r"\b[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)+\b", text):
        specificity.add("named_entity")
    dialogue = bool(re.search(r"[“\"]\s*[A-Za-z][^”\"]+[”\"]", text))
    if dialogue:
        specificity.add("dialogue")
    if re.search(r"\b(?:increased|reduced|grew|raised|served|reached)\b.{0,30}\b\d+", text, re.I):
        specificity.add("measurable_outcome")
    event_matches = re.findall(
        r"\b(?:when|after|before|during|that morning|that evening)\b", text, re.I
    )
    if event_matches:
        specificity.add("concrete_event")
    ngrams = Counter(
        " ".join(normalized_words[index : index + 3]) for index in range(max(0, word_count - 2))
    )
    repeated = {
        phrase: count
        for phrase, count in ngrams.items()
        if count >= 3 and len(set(phrase.split())) > 1
    }
    passive = sum(
        bool(re.search(r"\b(?:was|were|is|are|been|being)\s+\w+(?:ed|en)\b", sentence, re.I))
        for sentence in sentence_list
    )
    transition_types = frozenset(
        item for item in TRANSITIONS if re.search(rf"\b{item}\b", text, re.I)
    )
    return TextMetrics(
        word_count=word_count,
        character_count=len(text),
        sentence_count=len(sentence_list),
        paragraph_count=len(paragraph_list),
        sentence_lengths=sentence_lengths,
        paragraph_lengths=paragraph_lengths,
        average_sentence_length=round(fmean(sentence_lengths), 2) if sentence_lengths else 0,
        median_sentence_length=float(median(sentence_lengths)) if sentence_lengths else 0,
        sentence_length_stddev=round(pstdev(sentence_lengths), 2)
        if len(sentence_lengths) > 1
        else 0,
        flesch_reading_ease=flesch,
        lexical_diversity=round(len(set(normalized_words)) / word_count, 4) if word_count else None,
        reflection_counts=reflection_counts,
        reflection_positions=tuple(sorted(reflection_positions)),
        specificity_categories=frozenset(specificity),
        specificity_count=float(len(specificity) + min(2, len(event_matches) * 0.25)),
        filler_counts=_phrase_counts(text, FILLER_PHRASES),
        cliche_counts=_phrase_counts(text, CLICHE_PHRASES),
        generic_counts=_phrase_counts(text, GENERIC_PHRASES),
        repeated_phrases=repeated,
        passive_sentence_count=passive,
        dialogue_present=dialogue,
        transition_types=transition_types,
    )
