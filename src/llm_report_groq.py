import os
from typing import Any, Dict

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT_EN = """
You are a supportive assistant generating an autism pre-screening feedback report for parents.

IMPORTANT RULES:
1. This screening tool does NOT diagnose autism.
2. Never say the child has autism.
3. Use reassuring, parent-friendly language.
4. Avoid technical terms like machine learning or AI.
5. Provide practical next steps based on the risk level.
6. Encourage professional consultation only when appropriate.
7. Do not mention Groq, Llama, or that you are an AI model.

Risk Levels:
- No Risk
- Mild Risk
- Moderate Risk
- Severe Risk

Adjust your recommendations based on the risk level:
- No Risk -> reassure parents and suggest monitoring development.
- Mild Risk -> suggest observation and optional professional consultation.
- Moderate Risk -> recommend speaking with a pediatrician or specialist.
- Severe Risk -> strongly encourage professional developmental evaluation.

Write the report in clear sections.
"""

SYSTEM_PROMPT_UR = """
You are a supportive assistant generating an autism pre-screening feedback report for parents.

IMPORTANT RULES:
1. This screening tool does NOT diagnose autism.
2. Never say the child has autism.
3. Use reassuring, parent-friendly language.
4. Avoid technical terms like machine learning or AI.
5. Provide practical next steps based on the risk level.
6. Encourage professional consultation only when appropriate.
7. Do not mention Groq, Llama, or that you are an AI model.
8. Write the entire response in Urdu script.
9. Use clear, natural, parent-friendly Urdu.
10. Do not transliterate Urdu into English letters.

Write the report in clear sections with Urdu headings.
"""

RISK_LABELS_UR = {
    "No Risk": "کوئی نمایاں خطرہ نہیں",
    "Mild Risk": "ہلکا خطرہ",
    "Moderate Risk": "درمیانی خطرہ",
    "Severe Risk": "زیادہ خطرہ",
}

VALUE_MAP_UR = {
    "male": "مرد",
    "female": "عورت",
    "other": "غیر متعین",
    "yes": "ہاں",
    "no": "نہیں",
}


def normalize_language(language: str | None) -> str:
    return "ur" if str(language or "").strip().lower().startswith("ur") else "en"


def localize_simple_value(value: Any, language: str) -> str:
    text = str(value)
    if language == "ur":
        return VALUE_MAP_UR.get(text.strip().lower(), text)
    return text


def localize_risk_label(value: Any, language: str) -> str:
    text = str(value)
    if language == "ur":
        return RISK_LABELS_UR.get(text, text)
    return text


def build_user_prompt(inference_result: Dict[str, Any], language: str = "en") -> str:
    language = normalize_language(language)
    inputs = inference_result["inputs_used"]

    age_mons = inputs["age_mons"]
    gender = localize_simple_value(inputs.get("gender", inputs.get("sex", "unknown")), language)
    jaundice = localize_simple_value(inputs["jaundice"], language)
    family_asd = localize_simple_value(inputs["family_mem_with_asd"], language)

    score = inference_result["screening_score"]
    score_max = inference_result["screening_score_max"]
    score_risk = localize_risk_label(inference_result["score_risk_level"], language)
    referral = inference_result["referral_interpretation"]
    class_probs = inference_result["class_probabilities"]

    if language == "ur":
        return f"""
Generate a supportive autism pre-screening feedback report for parents.
Write the entire report in Urdu script.
Use Urdu headings for every section.

Child Information:
Age: {age_mons} months
Gender: {gender}
Jaundice: {jaundice}
Family ASD: {family_asd}

Screening Results:
Total Score: {score}/{score_max}
Risk Level: {score_risk}
Referral Guidance: {referral}

Probability estimates:
No Risk: {class_probs.get('No Risk')}
Mild Risk: {class_probs.get('Mild Risk')}
Moderate Risk: {class_probs.get('Moderate Risk')}
Severe Risk: {class_probs.get('Severe Risk')}

Write the report using these sections, but present the headings in Urdu:
1. Understanding Your Screening Result
2. What This Result Means
3. What Should Parents Do Next?
4. Why Professional Consultation Can Help
5. What Happens During an Initial Screening Consultation
6. Final Reassurance

Length: 250-350 words.
Tone: supportive, reassuring, clear.
"""

    return f"""
Generate a supportive autism pre-screening feedback report for parents.

Child Information:
Age: {age_mons} months
Gender: {gender}
Jaundice: {jaundice}
Family ASD: {family_asd}

Screening Results:
Total Score: {score}/{score_max}
Risk Level: {score_risk}
Referral Guidance: {referral}

Probability estimates:
No Risk: {class_probs.get('No Risk')}
Mild Risk: {class_probs.get('Mild Risk')}
Moderate Risk: {class_probs.get('Moderate Risk')}
Severe Risk: {class_probs.get('Severe Risk')}

Write the report using these sections:

1. Understanding Your Screening Result
Explain that this screening identifies common signs and is not a diagnosis.

2. What This Result Means
Explain the meaning of the risk level: {score_risk}

3. What Should Parents Do Next?
Provide appropriate recommendations based on the risk level.

4. Why Professional Consultation Can Help
Explain benefits of speaking with developmental specialists.

5. What Happens During an Initial Screening Consultation
Briefly explain how such consultations usually work.

6. Final Reassurance
Remind parents that early screening is helpful and encourage monitoring development.

Length: 250-350 words.
Tone: supportive, reassuring, clear.
"""


def generate_risk_report(inference_result: Dict[str, Any], language: str = "en") -> str:
    language = normalize_language(language)
    prompt = build_user_prompt(inference_result, language=language)
    system_prompt = SYSTEM_PROMPT_UR if language == "ur" else SYSTEM_PROMPT_EN

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=0.2,
        max_tokens=900,
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": prompt.strip()},
        ],
    )

    return response.choices[0].message.content.strip()
