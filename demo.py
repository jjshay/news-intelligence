#!/usr/bin/env python3
"""
News Intelligence System Demo
Demonstrates multi-AI article scoring with rich visual output.

Run: python demo.py
"""
from __future__ import annotations

import sys
import time
from typing import Dict, List

# Try to import rich for beautiful output, fall back to basic if not available
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.layout import Layout
    from rich.text import Text
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

console = Console() if RICH_AVAILABLE else None


# Sample news article for demonstration
SAMPLE_ARTICLE = {
    'title': 'AI Breakthrough: New Model Achieves Human-Level Reasoning',
    'source': 'MIT Technology Review',
    'date': '2024-01-15',
    'summary': '''Researchers at a major AI lab have unveiled a new language model that demonstrates unprecedented reasoning capabilities. The model, trained on a novel architecture, shows significant improvements in logical deduction, mathematical problem-solving, and common-sense reasoning tasks.

Early benchmarks suggest the model outperforms previous systems by 15-20% on standard reasoning tests. However, critics point out that the benchmark improvements may not translate to real-world applications, and ethical concerns about AI autonomy remain unaddressed.''',
    'url': 'https://example.com/ai-breakthrough'
}

# AI model configurations
AI_MODELS = {
    'ChatGPT': {'color': 'green', 'icon': '🟢', 'score': 8},
    'Claude': {'color': 'magenta', 'icon': '🟣', 'score': 7},
    'Gemini': {'color': 'blue', 'icon': '🔵', 'score': 9},
    'Grok': {'color': 'red', 'icon': '🔴', 'score': 7},
    'Perplexity': {'color': 'cyan', 'icon': '🔷', 'score': 8},
}

SIMULATED_SCORES = {
    'ChatGPT': {
        'score': 8,
        'reasoning': 'Well-written article from reputable source. Technical claims consistent with recent AI developments.',
        'strengths': ['Clear explanation', 'Acknowledges limitations'],
        'concerns': ['Some claims need context']
    },
    'Claude': {
        'score': 7,
        'reasoning': 'Solid reporting but headline may overstate findings. "Human-level" claim needs more nuance.',
        'strengths': ['Balanced view', 'Mentions ethics'],
        'concerns': ['Headline misleading', 'Missing regulation']
    },
    'Gemini': {
        'score': 9,
        'reasoning': 'Cross-referenced with 3 papers. 15-20% improvement aligns with pre-prints. Technically accurate.',
        'strengths': ['Verifiable claims', 'Timely'],
        'concerns': ['Needs historical context']
    },
    'Grok': {
        'score': 7,
        'reasoning': 'Follows typical AI hype cycle. Every 6 months we see "breakthrough" claims.',
        'strengths': ['Acknowledges skeptics'],
        'concerns': ['Missing applications', 'Sensationalized']
    },
    'Perplexity': {
        'score': 8,
        'reasoning': 'MIT Tech Review is Tier-1. Claims checked against 4 sources. Main claim accurate.',
        'strengths': ['Multiple verifications', 'High credibility'],
        'concerns': ['Framing debated']
    }
}


def print_header(text: str) -> None:
    """Print a formatted header."""
    if RICH_AVAILABLE:
        console.print()
        console.rule(f"[bold cyan]{text}[/bold cyan]", style="cyan")
        console.print()
    else:
        print(f"\n{'='*70}")
        print(f" {text}")
        print(f"{'='*70}\n")


def show_banner() -> None:
    """Display the application banner."""
    if RICH_AVAILABLE:
        banner = """
[bold cyan]╔═══════════════════════════════════════════════════════════════════╗
║[/bold cyan] [bold gold1]  _   _                      ___       _       _ _ _                [/bold gold1][bold cyan]║
║[/bold cyan] [bold gold1] | \ | | _____      _____   |_ _|_ __ | |_ ___| | (_) __ _  ___ ___ [/bold gold1][bold cyan]║
║[/bold cyan] [bold gold1] |  \| |/ _ \ \ /\ / / __|   | || '_ \| __/ _ \ | | |/ _` |/ _ \ _ \[/bold gold1][bold cyan]║
║[/bold cyan] [bold gold1] | |\  |  __/\ V  V /\__ \   | || | | | ||  __/ | | | (_| |  __/ | |[/bold gold1][bold cyan]║
║[/bold cyan] [bold gold1] |_| \_|\___| \_/\_/ |___/  |___|_| |_|\__\___|_|_|_|\__, |\___|_| |[/bold gold1][bold cyan]║
║[/bold cyan] [bold gold1]                                                     |___/         [/bold gold1][bold cyan]║
║[/bold cyan]                                                                       [bold cyan]║
║[/bold cyan]           [bold white]Multi-AI Article Scoring System[/bold white]                        [bold cyan]║
╚═══════════════════════════════════════════════════════════════════╝[/bold cyan]
"""
        console.print(banner)
    else:
        print("\n" + "="*70)
        print("  NEWS INTELLIGENCE - Multi-AI Article Scoring System")
        print("="*70 + "\n")


def step_api_health_check() -> bool:
    """Simulate API health check with visual progress."""
    print_header("STEP 0: API HEALTH CHECK")

    if RICH_AVAILABLE:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Checking AI engines...", total=5)

            for model, config in AI_MODELS.items():
                time.sleep(0.3)
                progress.update(task, advance=1, description=f"[{config['color']}]Checking {model}...")

        # Show results table
        table = Table(title="API Status", box=box.ROUNDED)
        table.add_column("AI Model", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Latency", justify="right")

        for model, config in AI_MODELS.items():
            table.add_row(
                f"{config['icon']} {model}",
                "[green]● Online[/green]",
                f"[dim]{42 + hash(model) % 50}ms[/dim]"
            )

        console.print(table)
        console.print("\n[bold green]✓ All 5 AI engines operational[/bold green]")
    else:
        print("Checking AI engines...\n")
        for model in AI_MODELS:
            print(f"  {model:12s} ... OK")
        print("\n  All 5 AI engines operational")

    return True


def step_show_article() -> None:
    """Display the article being analyzed."""
    print_header("ARTICLE TO ANALYZE")

    if RICH_AVAILABLE:
        article_panel = Panel(
            f"""[bold]{SAMPLE_ARTICLE['title']}[/bold]

[dim]Source:[/dim] [cyan]{SAMPLE_ARTICLE['source']}[/cyan]
[dim]Date:[/dim] [cyan]{SAMPLE_ARTICLE['date']}[/cyan]

[dim]Summary:[/dim]
{SAMPLE_ARTICLE['summary']}""",
            title="📰 Article",
            border_style="cyan",
            box=box.ROUNDED
        )
        console.print(article_panel)
    else:
        print(f"TITLE:  {SAMPLE_ARTICLE['title']}")
        print(f"SOURCE: {SAMPLE_ARTICLE['source']}")
        print(f"DATE:   {SAMPLE_ARTICLE['date']}")
        print(f"\nSUMMARY:\n{SAMPLE_ARTICLE['summary']}")


def step_individual_scoring() -> None:
    """Show individual AI scores with visual bars."""
    print_header("STEP 1: INDIVIDUAL AI SCORING")

    if RICH_AVAILABLE:
        console.print("[dim]Each AI evaluates the article independently...[/dim]\n")

        for model, data in SIMULATED_SCORES.items():
            config = AI_MODELS[model]
            score = data['score']
            bar = "█" * score + "░" * (10 - score)

            panel_content = f"""[bold]Score:[/bold] [{config['color']}]{bar}[/{config['color']}] [bold]{score}/10[/bold]

[bold]Reasoning:[/bold]
{data['reasoning']}

[green]✓ Strengths:[/green] {', '.join(data['strengths'])}
[yellow]⚠ Concerns:[/yellow] {', '.join(data['concerns'])}"""

            panel = Panel(
                panel_content,
                title=f"{config['icon']} {model}",
                border_style=config['color'],
                box=box.ROUNDED
            )
            console.print(panel)
    else:
        for model, data in SIMULATED_SCORES.items():
            print(f"\n{model}: {data['score']}/10")
            print(f"  {data['reasoning']}")


def step_peer_pairing() -> None:
    """Show peer review process."""
    print_header("STEP 2: PEER PAIRING")

    pairs = [
        ('ChatGPT', 'Perplexity', 'AGREEMENT'),
        ('Claude', 'Grok', 'AGREEMENT'),
        ('Gemini', 'Claude', 'DISAGREEMENT')
    ]

    if RICH_AVAILABLE:
        console.print("[dim]AIs randomly paired to compare evaluations...[/dim]\n")

        table = Table(title="Peer Review Pairs", box=box.ROUNDED)
        table.add_column("AI 1", style="cyan")
        table.add_column("Score", justify="center")
        table.add_column("vs", justify="center", style="dim")
        table.add_column("AI 2", style="magenta")
        table.add_column("Score", justify="center")
        table.add_column("Result", justify="center")

        for ai1, ai2, result in pairs:
            score1 = SIMULATED_SCORES[ai1]['score']
            score2 = SIMULATED_SCORES[ai2]['score']
            result_style = "green" if result == "AGREEMENT" else "yellow"

            table.add_row(
                ai1, str(score1), "⚔", ai2, str(score2),
                f"[{result_style}]{result}[/{result_style}]"
            )

        console.print(table)
    else:
        for ai1, ai2, result in pairs:
            print(f"  {ai1} vs {ai2}: {result}")


def step_perplexity_verdict() -> None:
    """Show Perplexity's final verdict."""
    print_header("STEP 3: PERPLEXITY FACT CHECK")

    if RICH_AVAILABLE:
        verdicts = [
            ("15-20% improvement on reasoning tests", "VERIFIED", "green", "Matches published benchmarks"),
            ("Human-level reasoning", "PARTIAL", "yellow", "True for narrow tasks, contested for general"),
        ]

        table = Table(title="🔍 Fact Check Results", box=box.ROUNDED)
        table.add_column("Claim", style="white")
        table.add_column("Verdict", justify="center")
        table.add_column("Details", style="dim")

        for claim, verdict, color, details in verdicts:
            table.add_row(claim, f"[{color}]{verdict}[/{color}]", details)

        console.print(table)
    else:
        print("  Claim: '15-20% improvement' - VERIFIED")
        print("  Claim: 'Human-level reasoning' - PARTIALLY VERIFIED")


def step_final_consensus() -> None:
    """Show final consolidated score with visual gauge."""
    print_header("STEP 4: FINAL CONSENSUS")

    scores = [d['score'] for d in SIMULATED_SCORES.values()]
    avg_score = sum(scores) / len(scores)

    if RICH_AVAILABLE:
        # Score breakdown table
        table = Table(title="Score Breakdown", box=box.ROUNDED)
        table.add_column("AI Model", style="cyan")
        table.add_column("Score", justify="center")
        table.add_column("Visual", justify="left")

        for model, data in SIMULATED_SCORES.items():
            config = AI_MODELS[model]
            score = data['score']
            bar = f"[{config['color']}]{'█' * score}[/{config['color']}][dim]{'░' * (10 - score)}[/dim]"
            table.add_row(f"{config['icon']} {model}", f"{score}/10", bar)

        console.print(table)

        # Final score panel
        score_color = "green" if avg_score >= 7.5 else "yellow" if avg_score >= 5 else "red"

        gauge = f"""
[bold]FINAL SCORE[/bold]

    [{score_color}]╔══════════════════════════════════════╗
    ║                                      ║
    ║            {avg_score:.1f} / 10               ║
    ║                                      ║
    ╚══════════════════════════════════════╝[/{score_color}]

[dim]Confidence:[/dim] [green]HIGH[/green] (low variance between evaluators)
[dim]Variance:[/dim]   ±0.8 points
"""
        console.print(Panel(gauge, title="📊 Consensus Score", border_style=score_color, box=box.DOUBLE))
    else:
        print(f"  FINAL SCORE: {avg_score:.1f}/10")
        for model, data in SIMULATED_SCORES.items():
            bar = "█" * data['score'] + "░" * (10 - data['score'])
            print(f"    {model:12s} [{bar}] {data['score']}/10")


def step_consolidated_insights() -> None:
    """Show final insights."""
    print_header("STEP 5: CONSOLIDATED INSIGHTS")

    insights = [
        ("FACTUAL ACCURACY", "High", "green", "Claims verified against published sources"),
        ("SOURCE QUALITY", "Excellent", "green", "MIT Tech Review is Tier-1 publication"),
        ("HEADLINE CONCERN", "Moderate", "yellow", "'Human-level' framing debated"),
        ("RECOMMENDATION", "Share with context", "cyan", "Good for professional network"),
    ]

    if RICH_AVAILABLE:
        table = Table(title="📋 Key Insights", box=box.ROUNDED)
        table.add_column("Category", style="bold")
        table.add_column("Rating", justify="center")
        table.add_column("Details", style="dim")

        for category, rating, color, details in insights:
            table.add_row(category, f"[{color}]{rating}[/{color}]", details)

        console.print(table)
    else:
        for category, rating, _, details in insights:
            print(f"  {category}: {rating} - {details}")


def show_summary() -> None:
    """Show final summary."""
    print_header("SUMMARY")

    if RICH_AVAILABLE:
        steps = """
[cyan]1.[/cyan] [bold]HEALTH CHECK[/bold]  → Verify all 5 AI APIs operational
[cyan]2.[/cyan] [bold]INDIVIDUAL[/bold]    → Each AI scores independently
[cyan]3.[/cyan] [bold]PEER REVIEW[/bold]   → AIs compare and discuss scores
[cyan]4.[/cyan] [bold]FACT CHECK[/bold]    → Perplexity verifies disputed claims
[cyan]5.[/cyan] [bold]CONSENSUS[/bold]     → Calculate weighted final score
[cyan]6.[/cyan] [bold]INSIGHTS[/bold]      → Synthesize key takeaways

[bold green]Benefits of Multi-AI Analysis:[/bold green]
  • No single AI bias dominates
  • Real-time fact verification
  • Diverse perspectives catch more issues
  • Higher confidence in final assessment
"""
        console.print(Panel(steps, title="How It Works", border_style="cyan", box=box.ROUNDED))
    else:
        print("  1. HEALTH CHECK  - Verify all 5 AI APIs")
        print("  2. INDIVIDUAL    - Each AI scores independently")
        print("  3. PEER REVIEW   - AIs compare and discuss")
        print("  4. FACT CHECK    - Perplexity verifies claims")
        print("  5. CONSENSUS     - Calculate final score")
        print("  6. INSIGHTS      - Synthesize takeaways")


def main() -> None:
    """Main entry point."""
    interactive = sys.stdin.isatty()

    def pause(msg: str = "") -> None:
        if interactive:
            if RICH_AVAILABLE:
                console.print(f"\n[dim]{msg}[/dim]")
            else:
                print(f"\n{msg}")
            input()
        else:
            time.sleep(0.3)

    show_banner()

    if RICH_AVAILABLE:
        console.print("[dim]This demo shows multi-AI news article scoring")
        console.print("without requiring any API keys.[/dim]\n")
    else:
        print("This demo shows multi-AI news article scoring")
        print("without requiring any API keys.\n")

    pause("Press Enter to start the demonstration...")

    step_api_health_check()
    pause("Press Enter to see the article...")

    step_show_article()
    pause("Press Enter to see individual AI scores...")

    step_individual_scoring()
    pause("Press Enter to see peer pairing...")

    step_peer_pairing()
    pause("Press Enter to see Perplexity's verdict...")

    step_perplexity_verdict()
    pause("Press Enter to see final consensus...")

    step_final_consensus()
    pause("Press Enter to see consolidated insights...")

    step_consolidated_insights()

    show_summary()

    print_header("DEMO COMPLETE")

    if RICH_AVAILABLE:
        console.print("[bold green]✓[/bold green] Run [cyan]'python fetch_news.py'[/cyan] with API keys for real analysis!")
    else:
        print("Run 'python fetch_news.py' with API keys for real analysis!")


if __name__ == "__main__":
    main()
