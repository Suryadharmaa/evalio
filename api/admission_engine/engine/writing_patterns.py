import re
from collections import Counter
from statistics import fmean, pstdev
from typing import Literal

from api.admission_engine.schemas.writing_patterns import (
    PatternCategory,
    PatternLevel,
    PatternRisk,
    WritingPatternRequest,
    WritingPatternResponse,
    WritingPatternSignal,
)
from api.admission_engine.text.metrics import (
    CLICHE_PHRASES,
    FILLER_PHRASES,
    TRANSITIONS,
    analyze_text,
    paragraphs,
    sentences,
    words,
)

ABSTRACT_WORDS = frozenset(
    {"success", "growth", "impact", "journey", "potential", "passion", "purpose", "leadership", "community", "opportunity", "experience", "challenge"}
)
FORMAL_PHRASES = (
    "it is important to note",
    "furthermore",
    "moreover",
    "in conclusion",
    "in light of",
    "with regard to",
)
HEDGES = ("perhaps", "possibly", "somewhat", "arguably", "seems", "might", "maybe", "likely")
SENSORY_WORDS = frozenset(
    {"saw", "heard", "felt", "smelled", "tasted", "bright", "dark", "loud", "quiet", "warm", "cold", "rough", "smooth", "voice", "sound", "color"}
)
FIRST_PERSON = frozenset({"i", "me", "my", "mine", "myself", "we", "us", "our", "ours"})
CONTRACTION_RE = re.compile(r"\b[A-Za-z]+(?:n't|'(?:m|re|ve|ll|d|s))\b", re.I)
NAMED_DETAIL_RE = re.compile(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b")
NUMBER_RE = re.compile(r"\b\d+(?:[.,]\d+)?\b")
PASSIVE_RE = re.compile(r"\b(?:was|were|is|are|been|being)\s+\w+(?:ed|en)\b", re.I)


def _rate(count: int | float, total: int) -> float:
    return round(float(count) / total * 100, 2) if total else 0.0


def _phrase_occurrences(text: str, phrases: tuple[str, ...]) -> list[str]:
    normalized = " ".join(word.lower() for word in words(text))
    return [phrase for phrase in phrases for _ in re.finditer(rf"\b{re.escape(phrase)}\b", normalized)]


def _matching_sentence_numbers(text: str, pattern: re.Pattern[str]) -> list[str]:
    return [f"Sentence {index}" for index, sentence in enumerate(sentences(text), 1) if pattern.search(sentence)]


def _signal(
    signal_id: str,
    label: str,
    category: PatternCategory,
    metric: str,
    observed: float | int | str,
    threshold: str,
    triggered: bool,
    explanation: str,
    *,
    evidence: list[str] | None = None,
    available: bool = True,
    severity: PatternLevel = "MEDIUM",
) -> WritingPatternSignal:
    return WritingPatternSignal(
        signal_id=signal_id,
        label=label,
        category=category,
        metric=metric,
        observed_value=observed,
        threshold=threshold,
        triggered=triggered if available else False,
        level=severity if triggered and available else "NORMAL" if available else "INSUFFICIENT_DATA",
        evidence=evidence or [],
        explanation=explanation,
    )


def evaluate_writing_patterns(request: WritingPatternRequest) -> WritingPatternResponse:
    text = request.text
    metrics = analyze_text(text)
    sentence_list = sentences(text)
    paragraph_list = paragraphs(text)
    word_list = [word.lower() for word in words(text)]
    word_count = len(word_list)
    sentence_count = len(sentence_list)
    paragraph_count = len(paragraph_list)
    signals: list[WritingPatternSignal] = []

    sentence_cv = round(metrics.sentence_length_stddev / metrics.average_sentence_length, 3) if metrics.average_sentence_length else 0.0
    signals.append(_signal("WP-001", "Sentence length uniformity", "RHYTHM", "sentence_length_cv", sentence_cv, "triggered when CV < 0.25 across at least 4 sentences", sentence_cv < 0.25, "Very similar sentence lengths can create a uniform rhythm.", available=sentence_count >= 4))

    paragraph_lengths = [len(words(item)) for item in paragraph_list]
    paragraph_mean = fmean(paragraph_lengths) if paragraph_lengths else 0
    paragraph_cv = round(pstdev(paragraph_lengths) / paragraph_mean, 3) if paragraph_mean and len(paragraph_lengths) > 1 else 0.0
    signals.append(_signal("WP-002", "Paragraph length uniformity", "RHYTHM", "paragraph_length_cv", paragraph_cv, "triggered when CV < 0.20 across at least 3 paragraphs", paragraph_cv < 0.20, "Nearly identical paragraph sizes can make structure feel mechanical.", available=paragraph_count >= 3))

    lexical = metrics.lexical_diversity or 0.0
    signals.append(_signal("WP-003", "Lexical diversity", "LANGUAGE", "unique_word_ratio", lexical, "triggered when ratio < 0.45 with at least 100 words", lexical < 0.45, "A low unique-word ratio indicates repeated vocabulary.", available=word_count >= 100, severity="LOW"))

    trigrams = [" ".join(word_list[index:index + 3]) for index in range(max(0, word_count - 2))]
    trigram_counts = Counter(trigrams)
    repeated_excess = sum(count - 1 for count in trigram_counts.values() if count > 1)
    repeated_rate = _rate(repeated_excess, len(trigrams))
    repeated_examples = [phrase for phrase, count in trigram_counts.most_common(3) if count > 1]
    signals.append(_signal("WP-004", "Repeated n-gram rate", "LANGUAGE", "repeated_trigram_percent", repeated_rate, "triggered above 3% with at least 50 words", repeated_rate > 3, "Repeated three-word sequences can signal formulaic phrasing.", evidence=repeated_examples, available=word_count >= 50, severity="HIGH"))

    transition_hits = _phrase_occurrences(text, TRANSITIONS)
    transition_rate = _rate(len(transition_hits), word_count)
    signals.append(_signal("WP-005", "Transition phrase overuse", "LANGUAGE", "transitions_per_100_words", transition_rate, "triggered above 3 per 100 words", transition_rate > 3, "Frequent explicit transitions may make connections sound over-signposted.", evidence=sorted(set(transition_hits)), available=word_count >= 50))

    cliche_hits = _phrase_occurrences(text, CLICHE_PHRASES)
    cliche_rate = _rate(len(cliche_hits), word_count)
    signals.append(_signal("WP-006", "Cliché density", "LANGUAGE", "cliches_per_100_words", cliche_rate, "triggered above 0.5 per 100 words", cliche_rate > 0.5, "Configured cliché phrases can reduce specificity.", evidence=sorted(set(cliche_hits)), available=word_count >= 50))

    abstract_count = sum(word in ABSTRACT_WORDS for word in word_list)
    abstract_rate = _rate(abstract_count, word_count)
    signals.append(_signal("WP-007", "Abstract language density", "DETAIL", "abstract_words_per_100", abstract_rate, "triggered above 4 per 100 words", abstract_rate > 4, "A high concentration of abstract nouns may leave actions unclear.", evidence=sorted(set(word_list) & ABSTRACT_WORDS)))

    specific_rate = _rate(metrics.specificity_count, word_count)
    signals.append(_signal("WP-008", "Specific-detail density", "DETAIL", "specific_signals_per_100", specific_rate, "triggered below 1 per 100 words with at least 100 words", specific_rate < 1, "Few configured concrete-detail signals were detected.", evidence=sorted(metrics.specificity_categories), available=word_count >= 100, severity="HIGH"))

    named_matches = NAMED_DETAIL_RE.findall(text)
    named_rate = _rate(len(named_matches), word_count)
    signals.append(_signal("WP-009", "Named-detail density", "DETAIL", "named_details_per_100", named_rate, "triggered below 0.5 per 100 words with at least 100 words", named_rate < 0.5, "Named people, projects, or organizations can anchor a narrative.", evidence=named_matches[:5], available=word_count >= 100))

    numeric_matches = NUMBER_RE.findall(text)
    numeric_rate = _rate(len(numeric_matches), word_count)
    signals.append(_signal("WP-010", "Numeric-detail density", "DETAIL", "numeric_details_per_100", numeric_rate, "triggered below 0.3 per 100 words with at least 100 words", numeric_rate < 0.3, "Numbers are one measurable form of concrete detail, though not every story needs them.", evidence=numeric_matches[:5], available=word_count >= 100, severity="LOW"))

    singular = sum(word in {"i", "me", "my", "mine", "myself"} for word in word_list)
    plural = sum(word in {"we", "us", "our", "ours"} for word in word_list)
    mixed_first_person = singular >= 3 and plural >= 3 and min(singular, plural) / max(singular, plural) >= 0.5
    signals.append(_signal("WP-011", "First-person consistency", "STANCE", "singular_plural_first_person", f"{singular}:{plural}", "triggered when singular and plural forms each appear at least 3 times at a ratio ≥ 0.5", mixed_first_person, "Frequent shifts between individual and group perspective may need clarification.", evidence=[f"singular: {singular}", f"plural: {plural}"], available=word_count >= 50, severity="LOW"))

    contraction_count = len(CONTRACTION_RE.findall(text))
    contraction_rate = _rate(contraction_count, word_count)
    signals.append(_signal("WP-012", "Contraction usage", "LANGUAGE", "contractions_per_100", contraction_rate, "triggered at 0 with at least 150 words", contraction_count == 0, "No contractions in a longer personal draft may contribute to a formal register.", available=word_count >= 150, severity="LOW"))

    punctuation_types = [symbol for symbol in [",", ";", ":", "—", "?", "!", "("] if symbol in text]
    signals.append(_signal("WP-013", "Punctuation diversity", "RHYTHM", "punctuation_types", len(punctuation_types), "triggered below 2 types across at least 8 sentences", len(punctuation_types) < 2, "Limited punctuation variety can reinforce a uniform sentence rhythm.", evidence=punctuation_types, available=sentence_count >= 8, severity="LOW"))

    openings = [" ".join(words(item.lower())[:2]) for item in sentence_list if words(item)]
    opening_counts = Counter(openings)
    opening_rate = _rate(max(opening_counts.values(), default=0), len(openings))
    common_opening = opening_counts.most_common(1)[0][0] if opening_counts else "none"
    signals.append(_signal("WP-014", "Sentence opening repetition", "RHYTHM", "most_common_opening_percent", opening_rate, "triggered at 25% or more across at least 8 sentences", opening_rate >= 25, "Repeated sentence openings can make cadence predictable.", evidence=[f"opening: {common_opening}"], available=sentence_count >= 8))

    repeated_reflections = [f"{marker}: {count}" for marker, count in metrics.reflection_counts.items() if count >= 3]
    signals.append(_signal("WP-015", "Reflection marker repetition", "LANGUAGE", "markers_repeated_3_plus", len(repeated_reflections), "triggered when any configured marker appears at least 3 times", bool(repeated_reflections), "Repeated reflection formulas have diminishing informational value.", evidence=repeated_reflections))

    long_words = sum(len(word) >= 9 for word in word_list)
    long_word_rate = _rate(long_words, word_count)
    signals.append(_signal("WP-016", "Vocabulary sophistication", "LANGUAGE", "words_9_chars_plus_percent", long_word_rate, "triggered above 25% with at least 100 words", long_word_rate > 25, "A high share of long words may reduce directness; it does not measure intelligence.", available=word_count >= 100, severity="LOW"))

    formal_hits = _phrase_occurrences(text, FORMAL_PHRASES)
    formal_rate = _rate(len(formal_hits), word_count)
    signals.append(_signal("WP-017", "Over-formality", "LANGUAGE", "formal_phrases_per_100", formal_rate, "triggered above 1 per 100 words", formal_rate > 1, "Configured formal transitions may make personal writing sound distant.", evidence=sorted(set(formal_hits)), available=word_count >= 50))

    filler_hits = _phrase_occurrences(text, FILLER_PHRASES)
    filler_rate = _rate(len(filler_hits), word_count)
    signals.append(_signal("WP-018", "Filler phrase density", "LANGUAGE", "fillers_per_100_words", filler_rate, "triggered above 1 per 100 words", filler_rate > 1, "Filler phrases add length without equivalent detail.", evidence=sorted(set(filler_hits)), available=word_count >= 50))

    hedge_hits = [word for word in word_list if word in HEDGES]
    hedge_rate = _rate(len(hedge_hits), word_count)
    signals.append(_signal("WP-019", "Hedging density", "STANCE", "hedges_per_100_words", hedge_rate, "triggered above 2 per 100 words", hedge_rate > 2, "Frequent hedging can weaken direct claims.", evidence=sorted(set(hedge_hits)), available=word_count >= 50))

    passive_rate = _rate(metrics.passive_sentence_count, sentence_count)
    signals.append(_signal("WP-020", "Passive construction proxy", "STANCE", "passive_sentence_percent", passive_rate, "triggered above 20% across at least 5 sentences", passive_rate > 20, "A rule-based proxy found frequent be-plus-participle constructions; this is not a grammar judgment.", evidence=_matching_sentence_numbers(text, PASSIVE_RE), available=sentence_count >= 5))

    sensory_hits = [word for word in word_list if word in SENSORY_WORDS]
    sensory_rate = _rate(len(sensory_hits), word_count)
    signals.append(_signal("WP-021", "Sensory language density", "DETAIL", "sensory_words_per_100", sensory_rate, "triggered below 0.5 per 100 words with at least 100 words", sensory_rate < 0.5, "Few configured sensory terms were found; not every essay requires sensory description.", evidence=sorted(set(sensory_hits)), available=word_count >= 100, severity="LOW"))

    personal_pronouns = sum(word in FIRST_PERSON for word in word_list)
    pronoun_rate = _rate(personal_pronouns, word_count)
    signals.append(_signal("WP-022", "Pronoun distribution", "STANCE", "first_person_pronouns_per_100", pronoun_rate, "triggered below 1 per 100 words with at least 100 words", pronoun_rate < 1, "Sparse first-person reference may indicate distance in a personal narrative.", available=word_count >= 100, severity="LOW"))

    ending_types = {sentence.rstrip()[-1] for sentence in sentence_list if sentence.rstrip() and sentence.rstrip()[-1] in ".!?"}
    signals.append(_signal("WP-023", "Sentence type variety", "RHYTHM", "ending_punctuation_types", len(ending_types), "triggered below 2 types across at least 8 sentences", len(ending_types) < 2, "Only one ending pattern was observed across the draft.", evidence=sorted(ending_types), available=sentence_count >= 8, severity="LOW"))

    short_sentences = [index for index, sentence in enumerate(sentence_list, 1) if len(words(sentence)) < 8]
    short_rate = _rate(len(short_sentences), sentence_count)
    signals.append(_signal("WP-024", "Short sentence frequency", "RHYTHM", "sentences_under_8_words_percent", short_rate, "triggered above 35% across at least 5 sentences", short_rate > 35, "Frequent short sentences can create a clipped rhythm.", evidence=[f"Sentence {index}" for index in short_sentences[:10]], available=sentence_count >= 5))

    long_sentences = [index for index, sentence in enumerate(sentence_list, 1) if len(words(sentence)) > 35]
    long_rate = _rate(len(long_sentences), sentence_count)
    signals.append(_signal("WP-025", "Long sentence frequency", "RHYTHM", "sentences_over_35_words_percent", long_rate, "triggered above 25% across at least 5 sentences", long_rate > 25, "Frequent long sentences can increase reading effort.", evidence=[f"Sentence {index}" for index in long_sentences[:10]], available=sentence_count >= 5, severity="HIGH"))

    triggered_count = sum(signal.triggered for signal in signals)
    available_count = sum(signal.level != "INSUFFICIENT_DATA" for signal in signals)
    trigger_ratio = triggered_count / available_count if available_count else 0
    risk: PatternRisk = "HIGH" if trigger_ratio >= 0.4 else "MODERATE" if trigger_ratio >= 0.2 else "LOW"
    confidence: Literal["HIGH", "MEDIUM", "LOW"] = "HIGH" if word_count >= 250 and sentence_count >= 10 else "MEDIUM" if word_count >= 100 and sentence_count >= 5 else "LOW"
    return WritingPatternResponse(
        risk=risk,
        triggered_count=triggered_count,
        total_signals=len(signals),
        confidence=confidence,
        signals=signals,
    )
