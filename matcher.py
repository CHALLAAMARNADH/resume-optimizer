import spacy
import io
from pdfminer.high_level import extract_text

nlp = spacy.load("en_core_web_md")

def extract_pdf_text(uploaded_file):
    return extract_text(io.BytesIO(uploaded_file.read()))

def extract_keywords(text):
    doc = nlp(text.lower())
    keywords = set()
    for token in doc:
        if (
            not token.is_stop and
            not token.is_punct and
            token.is_alpha and
            token.pos_ in ["NOUN", "PROPN"]
        ):
            keywords.add(token.lemma_)
    return keywords

def compute_similarity(text1, text2):
    doc1 = nlp(text1[:10000])
    doc2 = nlp(text2[:10000])
    return round(doc1.similarity(doc2) * 100, 2)

def get_suggestions(resume_text, jd_text, threshold=0.75):
    """
    For each missing JD keyword,
    find the closest word in resume and suggest replacing it.
    """
    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(jd_text)

    missing = jd_keywords - resume_keywords  # words in JD but not in resume

    suggestions = []

    for missing_word in missing:
        missing_token = nlp(missing_word)

        best_match = None
        best_score = 0.0

        # compare missing JD word with every resume keyword
        for resume_word in resume_keywords:
            resume_token = nlp(resume_word)

            # skip if no vector available
            if not missing_token.has_vector or not resume_token.has_vector:
                continue

            score = missing_token.similarity(resume_token)

            # we want words that are SIMILAR but NOT identical
            # threshold=0.5 means "related enough to be a replacement"
            if threshold < score < 0.95:
                if score > best_score:
                    best_score = score
                    best_match = resume_word

        if best_match:
            suggestions.append({
                "replace": best_match,       # word currently in resume
                "with": missing_word,        # word from JD
                "score": round(best_score * 100, 2)  # how similar they are
            })

    # sort by highest similarity first
    suggestions.sort(key=lambda x: x["score"], reverse=True)
    return suggestions[:15]  # top 15 suggestions

def apply_suggestions(resume_text, selected_suggestions):
    """
    Replace selected words in resume text with JD keywords.
    """
    updated = resume_text
    for s in selected_suggestions:
        # case-insensitive replace
        import re
        updated = re.sub(
            rf'\b{s["replace"]}\b',
            s["with"],
            updated,
            flags=re.IGNORECASE
        )
    return updated