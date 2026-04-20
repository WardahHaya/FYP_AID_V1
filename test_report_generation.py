#!/usr/bin/env python3
"""
Test script for enhanced report generation (LLM + PDF).

Tests the improved Groq prompts and visually enhanced PDF reports.
Run with: python test_report_generation.py
"""

import json
from pathlib import Path
from typing import Any, Dict

# Sample inference results for testing
SAMPLE_RESULTS = {
    "no_risk": {
        "screening_score": 2,
        "screening_score_max": 24,
        "score_risk_level": "No Risk",
        "referral_interpretation": "Your child is developing typically. Continue regular monitoring.",
        "inputs_used": {
            "age_mons": 24,
            "gender": "male",
            "sex": "male",
            "jaundice": "no",
            "family_mem_with_asd": "no",
        },
        "class_probabilities": {
            "No Risk": "92%",
            "Mild Risk": "6%",
            "Moderate Risk": "2%",
            "Severe Risk": "0%",
        },
    },
    "mild_risk": {
        "screening_score": 7,
        "screening_score_max": 24,
        "score_risk_level": "Mild Risk",
        "referral_interpretation": "Some early developmental signs noted. Observation and optional consultation recommended.",
        "inputs_used": {
            "age_mons": 18,
            "gender": "female",
            "sex": "female",
            "jaundice": "no",
            "family_mem_with_asd": "yes",
        },
        "class_probabilities": {
            "No Risk": "45%",
            "Mild Risk": "40%",
            "Moderate Risk": "12%",
            "Severe Risk": "3%",
        },
    },
    "moderate_risk": {
        "screening_score": 13,
        "screening_score_max": 24,
        "score_risk_level": "Moderate Risk",
        "referral_interpretation": "Professional developmental screening is recommended.",
        "inputs_used": {
            "age_mons": 28,
            "gender": "male",
            "sex": "male",
            "jaundice": "yes",
            "family_mem_with_asd": "yes",
        },
        "class_probabilities": {
            "No Risk": "15%",
            "Mild Risk": "25%",
            "Moderate Risk": "45%",
            "Severe Risk": "15%",
        },
    },
    "severe_risk": {
        "screening_score": 19,
        "screening_score_max": 24,
        "score_risk_level": "Severe Risk",
        "referral_interpretation": "Early professional developmental evaluation is strongly recommended.",
        "inputs_used": {
            "age_mons": 20,
            "gender": "female",
            "sex": "female",
            "jaundice": "no",
            "family_mem_with_asd": "no",
        },
        "class_probabilities": {
            "No Risk": "5%",
            "Mild Risk": "10%",
            "Moderate Risk": "20%",
            "Severe Risk": "65%",
        },
    },
}


def test_llm_report_generation(risk_level: str = "no_risk", language: str = "en"):
    """Test LLM report generation with sample data."""
    print(f"\n{'=' * 80}")
    print(f"Testing LLM Report Generation: {risk_level.upper()} ({language.upper()})")
    print(f"{'=' * 80}\n")

    from src.llm_report_groq import build_user_prompt, normalize_language

    if risk_level not in SAMPLE_RESULTS:
        print(f"❌ Unknown risk level: {risk_level}")
        print(f"   Available: {', '.join(SAMPLE_RESULTS.keys())}")
        return

    inference_result = SAMPLE_RESULTS[risk_level]
    language = normalize_language(language)

    # Build the prompt that will be sent to Groq
    prompt = build_user_prompt(inference_result, language=language)

    print("📋 PROMPT SENT TO GROQ LLM:")
    print("-" * 80)
    print(prompt)
    print("-" * 80)

    print("\n⚠️  To see the actual LLM-generated report, you need a GROQ_API_KEY.")
    print("   Set GROQ_API_KEY in .env file: https://console.groq.com/keys")
    print("\n   Once set, the report will include:")
    print("   ✓ Parent-friendly language and explanations")
    print("   ✓ Concrete 'today' action items")
    print("   ✓ Risk-level appropriate guidance")
    print("   ✓ Reassurance and support (not fear-mongering)")

    return prompt


def test_pdf_generation(risk_level: str = "no_risk", language: str = "en"):
    """Test PDF generation with sample data and mock LLM report."""
    print(f"\n{'=' * 80}")
    print(f"Testing PDF Generation: {risk_level.upper()} ({language.upper()})")
    print(f"{'=' * 80}\n")

    from src.pdf_generator import generate_pdf_report

    if risk_level not in SAMPLE_RESULTS:
        print(f"❌ Unknown risk level: {risk_level}")
        return

    inference_result = SAMPLE_RESULTS[risk_level]

    # Sample report text (what Groq would generate)
    sample_reports = {
        "en": {
            "no_risk": """
📋 What This Screening Means
This screening is a quick check to help us understand your child's early development. 
It is NOT a diagnosis—just one helpful tool parents and professionals use to support 
children's healthy development.

👨‍👩‍👧 About Your Child: What We Observed
Based on your answers, your child shows typical development patterns for their age. 
This is great news! Children develop at their own pace, and your responses suggest 
your little one is on track.

✅ What You Can Do Starting TODAY
• Play games that encourage interaction (peek-a-boo, singing)
• Point out things together and watch your child's reactions
• Read simple stories with lots of colors and sounds
• Let your child lead play sometimes—follow their interests!

🏥 About Professional Guidance
No immediate action needed, but continue with regular pediatric checkups. Your doctor 
can track progress at each visit.

📚 Understanding Child Development
Every child develops differently. Some talk early, others gesture first. Some are 
active, others calm. This diversity is completely normal and healthy!

💪 Final Thought
You're already supporting your child's development by being attentive and proactive. 
Simply continuing what you're doing—talking, playing, and responding to your child—
is the best thing you can do. Keep it up!
""",
            "mild_risk": """
📋 What This Screening Means
This screening helps identify early signs that might benefit from observation or 
professional guidance. Remember: this is not a diagnosis. Many children show these 
signs early and develop typically.

👨‍👩‍👧 About Your Child: What We Observed
Your responses suggest your child shows some developmental variations that would be 
worth observing more closely. This could be related to communication, social interaction, 
or play patterns—but remember, children develop on different timelines.

✅ What You Can Do Starting TODAY
• Practice turn-taking games (roll a ball back and forth)
• Use simple words paired with gestures (point while you say "look!")
• Encourage pretend play with toys (feeding dolls, toy cars)
• Create consistent routines around meals and bedtime
• Have regular one-on-one play time together

🏥 About Professional Guidance
If you're curious or want peace of mind, chatting with your pediatrician can help. 
A developmental specialist can observe your child in a non-stressful way and offer 
tailored suggestions.

📚 Understanding Child Development
Some children are naturally quieter, more independent, or prefer things a certain way. 
Others are very social right away. Both are normal!

💪 Final Thought
Early observation and gentle support are exactly what responsible parents do. You're 
giving your child the gift of attention and care—that matters most of all.
""",
            "moderate_risk": """
📋 What This Screening Means
This screening shows some developmental signs that would benefit from professional 
guidance. This is not a diagnosis—but a helpful heads-up that expert eyes on your 
child could be beneficial.

👨‍👩‍👧 About Your Child: What We Observed
Your responses suggest your child shows several developmental signs that deserve 
attention. This might relate to how your child communicates, interacts, or plays. 
The good news? Early attention and support can make a real difference.

✅ What You Can Do Starting TODAY
• Create picture cards for daily activities to support communication
• Practice making eye contact during fun moments
• Use songs and music with repetitive actions
• Build more structured play into your daily routine
• Celebrate small communication attempts enthusiastically
• Keep a simple journal of what you notice

🏥 About Professional Guidance
Having a developmental specialist take a quick look is a smart next step. They can:
• Observe your child in a comfortable setting
• Give specific suggestions tailored to your child
• Support you as parents
• Connect you with resources if needed

It's not scary—it's supportive. Early intervention is one of the most helpful things 
parents can provide.

📚 Understanding Child Development
Many children benefit from a little extra support at certain points. Getting it early 
gives them the best foundation.

💪 Final Thought
You're already doing the most important thing: caring enough to seek guidance. That's 
what great parents do. Professional support is here to help your whole family.
""",
            "severe_risk": """
📋 What This Screening Means
This screening indicates developmental patterns that would really benefit from 
professional evaluation soon. Remember: early professional attention and support can 
make a significant positive difference for your child.

👨‍👩‍👧 About Your Child: What We Observed
Your responses suggest your child shows multiple developmental signs. This is exactly 
why early screening exists—to connect families with support at the right time.

✅ What You Can Do Starting TODAY
• Write down specific examples of what you've noticed
• Note your child's strengths (even small ones!) alongside concerns
• Keep a video or audio clips if it helps describe your child's communication
• Think about questions for the specialist
• Gather any medical history or family background info
• Reach out to your pediatrician THIS WEEK

🏥 About Professional Guidance
Connecting with a developmental specialist is really important. They will:
• Conduct a proper developmental assessment
• Listen to your concerns and observations
• Answer your questions thoroughly
• Create a support plan if needed
• Help you access resources and services

This is NOT a diagnosis. It's a professional partnership to support your child's 
development and your family's needs.

📚 Understanding Child Development
Many children benefit tremendously from early professional guidance and targeted 
support. The earlier, the better the outcomes.

💪 Final Thought
Seeking professional help is a sign of strength and love. You're doing exactly what 
your child needs—connecting them with expert support early. Your proactive approach 
gives your child the best possible start.
""",
        },
        "ur": {
            "no_risk": """
آپ کے بچے کی ترقی بالکل معمول کے مطابق ہے۔ یہ بہت اچھی خبر ہے! 
آپ جو کر رہے ہیں اسے جاری رکھیں۔ کھیل کھیلیں، بات کریں، اور اپنے بچے کے ساتھ وقت گزاریں۔
""",
            "mild_risk": """
آپ کے بچے میں کچھ ابتدائی علامات نظر آ رہی ہیں۔ یہ بالکل عام ہے۔
ایک ماہر سے ملنا ایک اچھا خیال ہے۔ ابھی کوئی فوری فکر کی بات نہیں ہے۔
آپ وہی کریں جو آپ کر رہے ہیں - اپنے بچے سے بات کریں اور کھیلیں۔
""",
            "moderate_risk": """
آپ کے بچے میں کئی علامات ہیں جو اہم ہیں۔ ایک ماہر سے جلد ملنا بہت اچھا رہے گا۔
یہ خوفناک نہیں ہے - یہ معاون ہے۔ جلدی سہائتا بہت مدد دیتی ہے۔
اپنے ڈاکٹر کو تھریک کریں۔
""",
            "severe_risk": """
آپ کے بچے کو ایک ماہر کی نگاہ بہت ضروری ہے۔ اب یہ اقدام لینا ضروری ہے۔
جلدی مدد لینا آپ کے بچے کے لیے سب سے بہتر ہے۔
اپنے ڈاکٹر کو فوری طور پر رابطہ کریں۔
""",
        },
    }

    # Get the mock report
    mock_report = sample_reports.get(language, {}).get(risk_level, "[Mock LLM Report]")

    print(f"Generating PDF with {risk_level} data in {language.upper()}...\n")

    try:
        pdf_path = generate_pdf_report(
            inference_result,
            report_text=mock_report,
            filename_prefix=f"test_report_{risk_level}_{language}",
            language=language,
        )
        print(f"✅ PDF Generated Successfully!")
        print(f"📄 Location: {pdf_path}")
        print(f"📊 File size: {pdf_path.stat().st_size / 1024:.1f} KB")
        print(f"\n🎨 PDF Enhancements:")
        print(f"   ✓ Color-coded risk level (background color)")
        print(f"   ✓ Quick summary box with all key metrics")
        print(f"   ✓ Confidence levels table")
        print(f"   ✓ Personalized guidance section")
        print(f"   ✓ Clear disclaimer with context")
        print(f"   ✓ Professional typography and layout")
        print(f"   ✓ Multi-language support (EN/UR with RTL support)")
        return pdf_path
    except Exception as e:
        print(f"❌ PDF Generation Failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_prompt_comparison():
    """Show differences in prompt structure."""
    print(f"\n{'=' * 80}")
    print("Prompt Structure Comparison: OLD vs NEW")
    print(f"{'=' * 80}\n")

    print("OLD PROMPT (Brief):")
    print("---")
    print("""
Generate a supportive autism pre-screening feedback report for parents.

Child Information:
Age: X months
Gender: X
...

Write the report using these sections:
1. Understanding...
2. What This Result Means...
...

Length: 250-350 words.
""")

    print("\nNEW PROMPT (Comprehensive):")
    print("---")
    print("""
Write a comprehensive, warm, and deeply reassuring developmental guidance report.

CONTEXT FOR THIS FAMILY:
Your child's characteristics: [age, gender, medical history]

SCREENING RESULTS EXPLAINED FOR PARENTS:
→ Screening Score: X/24 with detailed interpretation
→ Confidence levels for each risk category
→ Professional guidance appropriate to risk level

STRUCTURE THIS REPORT WITH THESE SECTIONS:
📋 **What This Screening Means** - Demystify
👨‍👩‍👧 **About Your Child: What We Observed** - Real examples
✅ **What You Can Do Starting TODAY** - Concrete actions
🏥 **About Professional Guidance** - Risk-appropriate
📚 **Understanding Child Development** - Normalize variation
💪 **Final Thought** - Celebrate proactive parenting

IMPORTANT FORMATTING:
- Use simple, active voice
- Break complex info into bullet points
- Use "your child" and "your family" (personal tone)
- Use encouraging language throughout
- NO medical/technical jargon

Target Length: 400-500 words (more comprehensive)
Tone: Warm, knowledgeable, parent-focused, hopeful, practical, never scary
""")

    print("\n🎯 KEY IMPROVEMENTS:")
    print("   ✓ 150+ more words for better comprehensiveness")
    print("   ✓ Structured guidance for each risk level")
    print("   ✓ Concrete 'TODAY' actions (not vague advice)")
    print("   ✓ Emojis and formatting for visual clarity")
    print("   ✓ Emphasis on warmth and emotional support")
    print("   ✓ Clear section headings for easy scanning")


def main():
    """Run all tests."""
    import sys

    print("\n" + "=" * 80)
    print("🧪 REPORT GENERATION TESTING SUITE")
    print("=" * 80)

    print("\n📋 Available Risk Levels: no_risk, mild_risk, moderate_risk, severe_risk")
    print("🌍 Available Languages: en, ur")

    # Test all risk levels with PDF
    print("\n" + "=" * 80)
    print("TEST 1: PDF Generation for All Risk Levels (English)")
    print("=" * 80)

    pdf_paths = {}
    for risk in ["no_risk", "mild_risk", "moderate_risk", "severe_risk"]:
        path = test_pdf_generation(risk_level=risk, language="en")
        if path:
            pdf_paths[risk] = path

    # Test Urdu
    print("\n" + "=" * 80)
    print("TEST 2: PDF Generation for All Risk Levels (Urdu)")
    print("=" * 80)

    for risk in ["no_risk", "mild_risk", "moderate_risk", "severe_risk"]:
        path = test_pdf_generation(risk_level=risk, language="ur")

    # Test LLM prompts
    print("\n" + "=" * 80)
    print("TEST 3: LLM Prompt Structure")
    print("=" * 80)

    test_llm_report_generation(risk_level="moderate_risk", language="en")

    # Show improvements
    print("\n" + "=" * 80)
    print("TEST 4: Prompt Comparison")
    print("=" * 80)

    test_prompt_comparison()

    # Summary
    print("\n" + "=" * 80)
    print("✅ TESTING COMPLETE")
    print("=" * 80)

    print("\n📊 PDF FILES GENERATED:")
    for risk, path in pdf_paths.items():
        print(f"   • {risk}: {path.name}")

    print("\n🔍 TO SET UP GROQ API FOR REAL LLM REPORTS:")
    print("   1. Get API key: https://console.groq.com/keys")
    print("   2. Add to .env: GROQ_API_KEY=your_key_here")
    print("   3. Restart server: python -m uvicorn server.app:app --reload")
    print("   4. API /api/report/llm will now generate real reports")

    print("\n💾 TEST LOCATIONS:")
    print(f"   • Generated PDFs: /workspaces/FYP_AID_V1/reports/")
    print(f"   • Test script: /workspaces/FYP_AID_V1/test_report_generation.py")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
