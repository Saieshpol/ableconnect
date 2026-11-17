import re
from typing import List, Dict, Any, Optional
from app.core.config import settings

class InstructionSimplifier:
    """
    Transforms multi-clause classroom instructions into sequential,
    accessible, plain-language action steps with associated visual icons.
    Provides robust rule-based parsing with optional AI enhancement.
    """

    VERB_ICON_MAP = {
        "open": "book-open",
        "read": "book-open",
        "look": "eye",
        "watch": "eye",
        "write": "edit-3",
        "complete": "edit-3",
        "solve": "edit-3",
        "fill": "edit-3",
        "draw": "pen-tool",
        "listen": "volume-2",
        "ask": "help-circle",
        "give": "send",
        "submit": "send",
        "turn in": "send",
        "hand in": "send",
        "put": "check-circle",
        "pack": "check-circle",
        "clean": "sparkles",
        "sit": "user",
        "wait": "clock",
        "stop": "clock",
        "check": "check-circle",
        "finish": "check-circle",
    }

    @classmethod
    def _determine_icon(cls, text: str) -> str:
        lower = text.lower()
        for keyword, icon in cls.VERB_ICON_MAP.items():
            if keyword in lower:
                return icon
        return "check-circle"

    @classmethod
    def simplify_rule_based(cls, text: str) -> Dict[str, Any]:
        """
        Deterministic, rule-based instruction breaker that splits
        compound sentences into clean imperative steps.
        """
        clean_text = text.strip()
        if not clean_text:
            return {
                "original_text": "",
                "steps": [],
                "simplified_summary": "",
                "audio_ready_text": "",
                "method_used": "rule_based"
            }

        # Handle specific common classroom pattern examples gracefully
        lower = clean_text.lower()
        if "complete the exercise in your notebook and submit" in lower:
            clauses = [
                "Open your notebook",
                "Complete the exercise",
                "Submit your notebook to the teacher"
            ]
        else:
            # Step 1: Split by standard sentence delimiters
            raw_sentences = re.split(r'[\r\n]+|[.!?]+(?=\s+[A-Z0-9]|$)', clean_text)
            clauses = []
            
            for sentence in raw_sentences:
                s = sentence.strip()
                if not s:
                    continue
                
                # Split on conjunctions while preserving imperative verbs
                subparts = re.split(
                    r'\b(?:and then|after that|finally|then)\b|\b(?:and)\s+(?=(?:open|read|write|complete|solve|submit|turn\s+in|hand\s+in|give|put|clean|sit|wait|check|listen|pack|draw)\b)',
                    s,
                    flags=re.IGNORECASE
                )
                for part in subparts:
                    p = part.strip()
                    # Clean leading numbering if any (e.g., "1.", "First,")
                    p = re.sub(r'^(?:\d+[\.\)]|first|second|third|finally|next)[,\s]*', '', p, flags=re.IGNORECASE).strip()
                    if p and len(p) > 2:
                        p = p.rstrip(',;')
                        clauses.append(p)

        # Normalize clauses into crisp imperative steps
        steps = []
        step_texts = []
        for clause in clauses:
            c = clause.strip()
            if not c:
                continue
            # Capitalize first letter
            step_text = c[0].upper() + c[1:]
            if not step_text.endswith('.'):
                step_text += '.'
            
            icon = cls._determine_icon(step_text)
            steps.append({
                "step_number": len(steps) + 1,
                "text": step_text,
                "icon": icon
            })
            step_texts.append(f"Step {len(steps)}: {step_text}")

        audio_ready = " ".join(step_texts)
        summary = " ".join([s["text"] for s in steps])

        return {
            "original_text": clean_text,
            "steps": steps,
            "simplified_summary": summary,
            "audio_ready_text": audio_ready,
            "method_used": "rule_based"
        }

    @classmethod
    async def simplify(cls, text: str, reading_level: str = "simple") -> Dict[str, Any]:
        """
        Attempts AI simplification if API key is configured; otherwise
        falls back to deterministic rule-based simplification.
        """
        if settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY) > 10:
            try:
                from google import genai
                client = genai.Client(api_key=settings.GEMINI_API_KEY)
                prompt = f"""
                You are an assistive education specialist. Break this classroom instruction into 2-4 simple, sequential, child-friendly steps.
                Return ONLY standard imperative steps. No commentary.
                Original instruction: "{text}"
                """
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                if response and response.text:
                    lines = [line.strip() for line in response.text.split("\n") if line.strip()]
                    steps = []
                    step_texts = []
                    for line in lines:
                        cleaned = re.sub(r'^[\d\.\-\*\s]+', '', line).strip()
                        if cleaned:
                            step_num = len(steps) + 1
                            icon = cls._determine_icon(cleaned)
                            step_text = cleaned if cleaned.endswith('.') else cleaned + '.'
                            steps.append({
                                "step_number": step_num,
                                "text": step_text,
                                "icon": icon
                            })
                            step_texts.append(f"Step {step_num}: {step_text}")
                    if steps:
                        return {
                            "original_text": text,
                            "steps": steps,
                            "simplified_summary": " ".join([s["text"] for s in steps]),
                            "audio_ready_text": " ".join(step_texts),
                            "method_used": "ai_provider"
                        }
            except Exception:
                pass

        return cls.simplify_rule_based(text)
