import re
from typing import Dict, Any, List

from services.anonymizer import mask_pii
from services.gemini_client import generate_text

# Grounded DSM-5 Diagnostic Criteria Knowledge Chunks (ICD-10 / DSM-5)
DSM5_KNOWLEDGE_BASE = [
    {
        "id": "DSM5-MDD-01",
        "code": "DSM-5 296.23 / ICD-10 F32.2",
        "title": "Major Depressive Episode - Severe with Suicidal Ideation",
        "criteria": [
            "Depressed mood most of the day, nearly every day.",
            "Markedly diminished interest or pleasure in all or almost all activities (anhedonia).",
            "Recurrent suicidal ideation without a specific plan, or a suicide attempt or a specific plan for committing suicide.",
            "Feelings of worthlessness or excessive or inappropriate guilt nearly every day."
        ],
        "keywords": ["depressed", "worthless", "suicide", "end my life", "pills", "hopeless", "goodbye", "die"]
    },
    {
        "id": "DSM5-GAD-02",
        "code": "DSM-5 300.02 / ICD-10 F41.1",
        "title": "Generalized Anxiety Disorder - Severe Distress",
        "criteria": [
            "Excessive anxiety and worry occurring more days than not for at least 6 months.",
            "The individual finds it difficult to control the worry.",
            "Restlessness or feeling keyed up or on edge.",
            "Chest pain, muscle tension, or overwhelming panic sensations."
        ],
        "keywords": ["anxious", "panic", "worry", "chest hurt", "scared", "fear", "overwhelmed", "stressed"]
    },
    {
        "id": "DSM5-PTSD-03",
        "code": "DSM-5 309.81 / ICD-10 F43.10",
        "title": "Post-Traumatic Stress Disorder & Acute Distress",
        "criteria": [
            "Exposure to actual or threatened death, serious injury, or sexual violence.",
            "Recurrent, involuntary, and intrusive distressing memories or flashbacks.",
            "Persistent negative emotional state (e.g., fear, horror, anger, guilt, or shame)."
        ],
        "keywords": ["trauma", "nightmare", "flashback", "pain", "alone", "broke up", "invisible", "trauma"]
    }
]

# Columbia-Suicide Severity Rating Scale (C-SSRS) Protocols
CSSRS_PROTOCOLS = {
    "P0": {
        "level": "C-SSRS Level 5: Active Suicidal Ideation with Specific Plan & Intent",
        "triage": "CRITICAL EMERGENCY - IMMEDIATE SAFETY INTERVENTION REQUIRED",
        "color": "#EF4444",
        "steps": [
            "Initiate immediate crisis contact (988 Line / Emergency Dispatch).",
            "Do not leave patient unmonitored; implement active Lethal Means Restriction (secure medications/sharps).",
            "Complete Stanley-Brown Safety Planning Intervention (SPI) including designated emergency contacts.",
            "Notify designated human safety supervisor immediately."
        ]
    },
    "P1": {
        "level": "C-SSRS Level 3-4: Active Ideation with Method (No Specific Imminent Intent)",
        "triage": "HIGH RISK - PROACTIVE CLINICAL SUPPORT & WARMLINE DISPATCH",
        "color": "#F59E0B",
        "steps": [
            "Connect user to Crisis Text Line (Text HOME to 741741) or local mental health warmline.",
            "Schedule proactive clinical review check-in within 12 hours.",
            "Review coping strategies and internal distractors with patient."
        ]
    },
    "P2": {
        "level": "C-SSRS Level 1-2: Passive Suicidal Ideation / General Distress",
        "triage": "MODERATE RISK - STANDARD PSYCHOEDUCATION & COPING SKILLS",
        "color": "#3B82F6",
        "steps": [
            "Provide self-care guides, community support groups, and mental health helpline contacts.",
            "Monitor patient trajectory across subsequent communications."
        ]
    }
}

class ClinicalRAGCopilotEngine:
    """Retrieval-Augmented Generation (RAG) Clinical Decision Support Engine."""

    @staticmethod
    def query_rag_knowledge(text: str, prob_suicide: float, dominant_emotion: str) -> Dict[str, Any]:
        """
        Queries DSM-5 & C-SSRS knowledge base using TF-IDF / keyword similarity retrieval
        to return evidence-grounded recommendations for clinicians.
        """
        text_lower = text.lower()
        matched_dsm_criteria = []

        for item in DSM5_KNOWLEDGE_BASE:
            matches = [kw for kw in item["keywords"] if kw in text_lower]
            relevance_score = len(matches) / float(len(item["keywords"]))
            if matches:
                matched_dsm_criteria.append({
                    "id": item["id"],
                    "code": item["code"],
                    "title": item["title"],
                    "matched_keywords": matches,
                    "relevance_score": round(relevance_score, 3),
                    "criteria_snippets": item["criteria"]
                })

        # Sort by relevance
        matched_dsm_criteria.sort(key=lambda x: x["relevance_score"], reverse=True)

        # C-SSRS Level Selection
        if prob_suicide >= 0.70 or any(k in text_lower for k in ["pills", "tonight", "end my life", "goodbye", "plan"]):
            cssrs_info = CSSRS_PROTOCOLS["P0"]
        elif prob_suicide >= 0.40 or any(k in text_lower for k in ["die", "hopeless", "can't carry", "no point"]):
            cssrs_info = CSSRS_PROTOCOLS["P1"]
        else:
            cssrs_info = CSSRS_PROTOCOLS["P2"]

        # Evidence-grounded intervention plan
        rag_citations = [
            f"DSM-5 Diagnostic Criteria ({matched_dsm_criteria[0]['code']})" if matched_dsm_criteria else "DSM-5 Unspecified Distress Criteria",
            "Columbia-Suicide Severity Rating Scale (C-SSRS) Protocol Guidelines",
            "Stanley-Brown Safety Planning Intervention (SPI) Standard"
        ]

        template_summary = f"RAG analysis identified clinical alignment with {matched_dsm_criteria[0]['title'] if matched_dsm_criteria else 'Distress Criteria'} under {cssrs_info['level']}."
        top_matches = matched_dsm_criteria[:2]

        narrative = ClinicalRAGCopilotEngine._generate_narrative(
            text=text,
            dominant_emotion=dominant_emotion,
            matched_dsm_criteria=top_matches,
            cssrs_info=cssrs_info,
        )

        return {
            "rag_citations": rag_citations,
            "dsm5_matches": top_matches,
            "cssrs_protocol": cssrs_info,
            "grounded_summary": narrative or template_summary,
            "narrative_source": "gemini" if narrative else "template"
        }

    @staticmethod
    def _generate_narrative(text: str, dominant_emotion: str, matched_dsm_criteria: List[Dict[str, Any]], cssrs_info: Dict[str, Any]) -> str:
        """
        Asks Gemini for a short clinician-facing narrative grounded ONLY in the criteria
        matches and C-SSRS level already decided deterministically above -- the model is
        explicitly told not to re-derive or override the triage level. Text is PII-masked
        before it leaves the process. Returns None (falls back to template_summary) if the
        API key is missing or the call fails for any reason.
        """
        criteria_context = "\n".join(
            f"- {m['code']} ({m['title']}): matched keywords {m['matched_keywords']}"
            for m in matched_dsm_criteria
        ) or "- No specific DSM-5 criteria keywords matched; treat as general distress."

        prompt = (
            f"De-identified excerpt from a user's post: \"{mask_pii(text)}\"\n"
            f"Dominant detected emotion: {dominant_emotion}\n\n"
            f"Retrieved DSM-5 criteria matches (already determined, do not change):\n{criteria_context}\n\n"
            f"Already-assigned C-SSRS triage level (already determined, do not change): {cssrs_info['level']} "
            f"({cssrs_info['triage']})\n\n"
            "Write a 2-3 sentence clinical rationale for a human clinician reviewing this case, "
            "grounded strictly in the information above."
        )
        system_instruction = (
            "You are a clinical documentation assistant supporting a human clinician's review of an "
            "automated mental-health risk screen. You are NOT diagnosing the patient and you must NOT "
            "invent facts, criteria, or risk levels beyond what is given to you. Never change or "
            "contradict the supplied C-SSRS triage level -- only explain why the retrieved evidence "
            "supports it. Do not address the patient directly. Keep the tone clinical and concise."
        )
        return generate_text(prompt, system_instruction=system_instruction)
