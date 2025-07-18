from typing import List
import spacy

# Load spaCy English model (ensure it's installed: python -m spacy download en_core_web_sm)
nlp = spacy.load("en_core_web_sm")

def decompose_prompt(prompt: str, similarity_threshold: float = 0.75) -> List[str]:
    """
    Decompose the input prompt into thinklets (semantic chunks).
    1. Split by paragraphs (double newlines).
    2. Use spaCy to segment each paragraph into sentences.
    3. Group semantically similar sentences within a paragraph into a single thinklet.
    """
    thinklets = []
    paragraphs = [p.strip() for p in prompt.strip().split("\n\n") if p.strip()]
    for para in paragraphs:
        doc = nlp(para)
        sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        if not sentences:
            continue
        # Group sentences by semantic similarity
        current_chunk = sentences[0]
        current_vec = nlp(current_chunk).vector
        for sent in sentences[1:]:
            sent_vec = nlp(sent).vector
            similarity = nlp(current_chunk).similarity(nlp(sent))
            if similarity >= similarity_threshold:
                current_chunk += " " + sent
            else:
                thinklets.append(current_chunk)
                current_chunk = sent
        thinklets.append(current_chunk)
    return thinklets 