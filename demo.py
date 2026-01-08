#!/usr/bin/env python3
"""
News Intelligence System Demo
Demonstrates multi-AI article scoring without needing API keys.

Run: python demo.py
"""

import random
from datetime import datetime


def print_header(text):
    print(f"\n{'='*70}")
    print(f" {text}")
    print(f"{'='*70}\n")


# Sample news article for demonstration
SAMPLE_ARTICLE = {
    'title': 'AI Breakthrough: New Model Achieves Human-Level Reasoning',
    'source': 'MIT Technology Review',
    'date': '2024-01-15',
    'summary': '''
    Researchers at a major AI lab have unveiled a new language model that
    demonstrates unprecedented reasoning capabilities. The model, trained on
    a novel architecture, shows significant improvements in logical deduction,
    mathematical problem-solving, and common-sense reasoning tasks.

    Early benchmarks suggest the model outperforms previous systems by 15-20%
    on standard reasoning tests. However, critics point out that the benchmark
    improvements may not translate to real-world applications, and ethical
    concerns about AI autonomy remain unaddressed.
    ''',
    'url': 'https://example.com/ai-breakthrough'
}

# AI model personalities for realistic simulation
AI_PERSONALITIES = {
    'ChatGPT': {
        'style': 'balanced and thorough',
        'focus': 'broad knowledge synthesis',
        'bias': 'tends toward optimistic interpretations'
    },
    'Claude': {
        'style': 'nuanced and careful',
        'focus': 'safety and ethical implications',
        'bias': 'cautious about overstated claims'
    },
    'Gemini': {
        'style': 'data-driven and technical',
        'focus': 'verification against known facts',
        'bias': 'favors quantifiable metrics'
    },
    'Grok': {
        'style': 'direct and contrarian',
        'focus': 'challenging assumptions',
        'bias': 'skeptical of mainstream narratives'
    },
    'Perplexity': {
        'style': 'citation-heavy and current',
        'focus': 'real-time fact verification',
        'bias': 'prefers recent sources'
    }
}

# Simulated AI evaluations
SIMULATED_SCORES = {
    'ChatGPT': {
        'score': 8,
        'reasoning': 'Well-written article from reputable source. Technical claims are consistent with recent AI developments. Would benefit from more specific methodology details.',
        'strengths': ['Clear explanation of complex topic', 'Acknowledges limitations'],
        'concerns': ['Some claims need more context']
    },
    'Claude': {
        'score': 7,
        'reasoning': 'Solid reporting but headline may overstate findings. The "human-level" claim needs more nuance - the benchmarks cited measure narrow capabilities.',
        'strengths': ['Balanced view including critics', 'Mentions ethical concerns'],
        'concerns': ['Headline could be misleading', 'Missing regulatory perspective']
    },
    'Gemini': {
        'score': 9,
        'reasoning': 'Cross-referenced with 3 recent papers from the same lab. The 15-20% improvement claim aligns with published pre-prints. Technically accurate reporting.',
        'strengths': ['Verifiable claims', 'Timely topic'],
        'concerns': ['Could include more historical context']
    },
    'Grok': {
        'score': 7,
        'reasoning': 'Interesting but follows typical AI hype cycle pattern. Every 6 months we see "breakthrough" claims. The real question: when will this help regular people?',
        'strengths': ['Acknowledges skeptics'],
        'concerns': ['Missing practical applications', 'Somewhat sensationalized']
    },
    'Perplexity': {
        'score': 8,
        'reasoning': 'Verified: MIT Tech Review is Tier-1 source. Claims checked against 4 sources (2 academic, 2 industry). Main claim accurate but "human-level" framing contested in 2 sources.',
        'strengths': ['Multiple verification points', 'Source credibility high'],
        'concerns': ['Framing debated in academic circles']
    }
}


def step_api_health_check():
    """Simulate API health check"""
    print_header("STEP 0: API HEALTH CHECK")

    print("Checking AI engines...\n")

    models = ['ChatGPT', 'Claude', 'Gemini', 'Grok', 'Perplexity']
    for model in models:
        # Simulate check with random delay representation
        print(f"  {model:12s} ... OK")

    print("\n  All 5 AI engines operational")
    print("  Ready for multi-model analysis")

    return True


def step_show_article():
    """Display the article being analyzed"""
    print_header("ARTICLE TO ANALYZE")

    print(f"TITLE:  {SAMPLE_ARTICLE['title']}")
    print(f"SOURCE: {SAMPLE_ARTICLE['source']}")
    print(f"DATE:   {SAMPLE_ARTICLE['date']}")
    print(f"\nSUMMARY:")
    print(f"-" * 60)
    for line in SAMPLE_ARTICLE['summary'].strip().split('\n'):
        print(f"  {line.strip()}")
    print(f"-" * 60)


def step_individual_scoring():
    """Show individual AI scores"""
    print_header("STEP 1: INDIVIDUAL AI SCORING")

    print("Each AI evaluates the article independently...\n")

    for model, data in SIMULATED_SCORES.items():
        print(f"{'─'*60}")
        print(f" {model.upper()}")
        print(f"{'─'*60}")
        print(f"  Score: {data['score']}/10")
        print(f"  Style: {AI_PERSONALITIES[model]['style']}")
        print(f"\n  Reasoning:")
        # Wrap text nicely
        words = data['reasoning'].split()
        line = "    "
        for word in words:
            if len(line) + len(word) > 65:
                print(line)
                line = "    " + word + " "
            else:
                line += word + " "
        if line.strip():
            print(line)

        print(f"\n  Strengths: {', '.join(data['strengths'])}")
        print(f"  Concerns: {', '.join(data['concerns'])}")
        print()


def step_peer_pairing():
    """Show peer review process"""
    print_header("STEP 2: PEER PAIRING")

    print("AIs randomly paired to compare evaluations...")
    print("(Perplexity always participates as fact-checker)\n")

    # Simulate random pairing
    pairs = [
        ('ChatGPT', 'Perplexity'),
        ('Claude', 'Grok'),
        ('Gemini', 'Claude')
    ]

    for ai1, ai2 in pairs:
        score1 = SIMULATED_SCORES[ai1]['score']
        score2 = SIMULATED_SCORES[ai2]['score']
        diff = abs(score1 - score2)

        print(f"  PAIR: {ai1} ({score1}/10) vs {ai2} ({score2}/10)")

        if diff <= 1:
            print(f"    Result: AGREEMENT (diff: {diff})")
        else:
            print(f"    Result: DISAGREEMENT (diff: {diff})")
            # Show simulated discussion
            if ai1 == 'Claude' and ai2 == 'Grok':
                print(f"    Discussion: Grok challenges Claude's caution about claims")

        print()


def step_perplexity_verdict():
    """Show Perplexity's final verdict"""
    print_header("STEP 3: PERPLEXITY FINAL VERDICT")

    print("Perplexity (with web access) has final say on disputed points...\n")

    print("  FACT CHECK RESULTS:")
    print("  ┌─────────────────────────────────────────────────────────┐")
    print("  │ Claim: '15-20% improvement on reasoning tests'         │")
    print("  │ Verdict: VERIFIED - matches published benchmarks       │")
    print("  ├─────────────────────────────────────────────────────────┤")
    print("  │ Claim: 'Human-level reasoning'                         │")
    print("  │ Verdict: PARTIALLY VERIFIED - true for narrow tasks,   │")
    print("  │          contested for general reasoning               │")
    print("  └─────────────────────────────────────────────────────────┘")


def step_final_consensus():
    """Show final consolidated score"""
    print_header("STEP 4: FINAL CONSENSUS")

    # Calculate average
    scores = [d['score'] for d in SIMULATED_SCORES.values()]
    avg_score = sum(scores) / len(scores)

    print(f"  Individual Scores:")
    for model, data in SIMULATED_SCORES.items():
        bar = "█" * data['score'] + "░" * (10 - data['score'])
        print(f"    {model:12s} [{bar}] {data['score']}/10")

    print(f"\n  {'─'*50}")
    print(f"  FINAL SCORE: {avg_score:.1f}/10")
    print(f"  CONFIDENCE: High (low variance between evaluators)")
    print(f"  {'─'*50}")


def step_consolidated_insights():
    """Show final bullet points"""
    print_header("STEP 5: CONSOLIDATED INSIGHTS")

    print("  6th AI call synthesizes all opinions into key takeaways:\n")

    insights = [
        "FACTUAL ACCURACY: High - Claims verified by Perplexity against published sources; 15-20% improvement claim is accurate",
        "SOURCE QUALITY: Excellent - MIT Technology Review is Tier-1 publication; article acknowledges limitations appropriately",
        "HEADLINE CONCERN: Moderate - 'Human-level' framing debated; Claude and Grok flag potential overstatement",
        "RECOMMENDATION: Share with context - Good for professional network; add note about narrow vs general capabilities"
    ]

    for i, insight in enumerate(insights, 1):
        parts = insight.split(' - ')
        header = parts[0]
        body = parts[1] if len(parts) > 1 else ""

        print(f"  {i}. {header}")
        if body:
            # Wrap body text
            words = body.split()
            line = "     "
            for word in words:
                if len(line) + len(word) > 65:
                    print(line)
                    line = "     " + word + " "
                else:
                    line += word + " "
            if line.strip():
                print(line)
        print()


def show_summary():
    """Show final summary and next steps"""
    print_header("SUMMARY")

    print("This demo showed how the News Intelligence System works:")
    print()
    print("  1. HEALTH CHECK  - Verify all 5 AI APIs are operational")
    print("  2. INDIVIDUAL    - Each AI scores independently")
    print("  3. PEER REVIEW   - AIs compare and discuss scores")
    print("  4. FACT CHECK    - Perplexity verifies disputed claims")
    print("  5. CONSENSUS     - Calculate weighted final score")
    print("  6. INSIGHTS      - Synthesize key takeaways")
    print()
    print("Benefits of Multi-AI Analysis:")
    print("  - No single AI bias dominates")
    print("  - Real-time fact verification")
    print("  - Diverse perspectives caught more issues")
    print("  - Higher confidence in final assessment")
    print()
    print("To use with real articles:")
    print("  1. Get API keys (see README.md)")
    print("  2. Configure .env file")
    print("  3. Run: python fetch_news.py")


def main():
    print_header("NEWS INTELLIGENCE SYSTEM - DEMO")

    print("This demo shows multi-AI news article scoring")
    print("without requiring any API keys.\n")

    input("Press Enter to start the demonstration...")

    # Run all steps
    step_api_health_check()
    input("\nPress Enter to see the article...")

    step_show_article()
    input("\nPress Enter to see individual AI scores...")

    step_individual_scoring()
    input("\nPress Enter to see peer pairing...")

    step_peer_pairing()
    input("\nPress Enter to see Perplexity's verdict...")

    step_perplexity_verdict()
    input("\nPress Enter to see final consensus...")

    step_final_consensus()
    input("\nPress Enter to see consolidated insights...")

    step_consolidated_insights()

    show_summary()

    print_header("DEMO COMPLETE")
    print("Run 'python fetch_news.py' with API keys for real analysis!")


if __name__ == "__main__":
    main()
