#!/usr/bin/env python3
"""News Intelligence - Marketing Demo"""
import time
import sys

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.align import Align
    from rich import box
except ImportError:
    print("Run: pip install rich")
    sys.exit(1)

console = Console()

def pause(s=1.5):
    time.sleep(s)

def step(text):
    console.print(f"\n[bold white on #1a1a2e]  {text}  [/]\n")
    pause(0.8)

# INTRO
console.clear()
console.print()
intro = Panel(
    Align.center("[bold yellow]NEWS INTELLIGENCE[/]\n\n[white]Multi-AI Article Scoring System[/]"),
    border_style="cyan",
    width=60,
    padding=(1, 2)
)
console.print(intro)
pause(2)

# STEP 1
step("STEP 1: SUBMIT ARTICLE URL")

console.print("[dim]$[/] python news_scorer.py [cyan]\"https://reuters.com/ai-breakthrough\"[/]\n")
pause(1)

console.print("  Fetching article.........", end="")
pause(0.6)
console.print(" [green]Done[/]")

console.print("  Extracting text..........", end="")
pause(0.5)
console.print(" [green]1,247 words[/]")

console.print("  Detecting language.......", end="")
pause(0.3)
console.print(" [green]English[/]")

pause(0.8)

article = Panel(
    "[bold]AI Diagnostics Outperform Doctors in Trial[/]\n\n"
    "[dim]Source:[/]     Reuters Health\n"
    "[dim]Author:[/]     Dr. Emily Watson\n"
    "[dim]Published:[/]  January 11, 2024",
    title="[cyan]Article Loaded[/]",
    border_style="cyan",
    width=55
)
console.print(article)
pause(1.5)

# STEP 2
step("STEP 2: QUERY 5 AI MODELS")

models = [
    ("Claude 3.5", "Anthropic", 9.2),
    ("GPT-4", "OpenAI", 8.8),
    ("Gemini", "Google", 9.0),
    ("Grok-2", "xAI", 8.6),
    ("Perplexity", "Perplexity AI", 9.1),
]

for i, (name, provider, score) in enumerate(models, 1):
    console.print(f"  [{i}/5] [bold]{name}[/] ({provider})...", end="")
    pause(0.7)
    bar = "[green]" + "█" * int(score) + "[/][dim]" + "░" * (10 - int(score)) + "[/]"
    console.print(f" {bar} [cyan]{score}[/]")
    pause(0.2)

pause(1)

# STEP 3
step("STEP 3: AGGREGATE RESULTS")

table = Table(box=box.ROUNDED, width=58)
table.add_column("Model", style="white")
table.add_column("Score", justify="center", style="cyan")
table.add_column("Bias", justify="center")
table.add_column("Trust", justify="center")

table.add_row("Claude 3.5", "9.2", "[green]Low[/]", "[green]94%[/]")
table.add_row("GPT-4", "8.8", "[yellow]Med[/]", "[green]89%[/]")
table.add_row("Gemini", "9.0", "[green]Low[/]", "[green]91%[/]")
table.add_row("Grok-2", "8.6", "[green]Low[/]", "[yellow]87%[/]")
table.add_row("Perplexity", "9.1", "[green]Low[/]", "[green]92%[/]")

console.print(table)
pause(1.5)

# STEP 4
step("STEP 4: CONSENSUS SCORE")

console.print("  Model Agreement:    [bold green]HIGH[/] (4/5 within 0.5 pts)")
pause(0.4)
console.print("  Outlier Detection:  [green]None[/]")
pause(0.4)
console.print("  Confidence Level:   [bold green]94%[/]\n")
pause(0.8)

score_panel = Panel(
    Align.center(
        "[bold green]8.9 / 10[/]\n\n"
        "[green]" + "█" * 36 + "[/][dim]" + "░" * 4 + "[/]\n\n"
        "[bold]VERDICT: HIGHLY RELIABLE[/]"
    ),
    title="[bold yellow]CONSENSUS SCORE[/]",
    border_style="green",
    width=55
)
console.print(score_panel)
pause(2)

# STEP 5
step("STEP 5: FACT CHECK CLAIMS")

claims = Table(box=box.SIMPLE, width=58)
claims.add_column("Claim", style="white", width=32)
claims.add_column("Status", justify="center", width=12)
claims.add_column("Source", width=12)

claims.add_row("AI accuracy of 94.2%", "[green]Verified[/]", "NIH Study")
claims.add_row("FDA approval pending", "[green]Verified[/]", "FDA.gov")
claims.add_row("10,000 patient trial", "[green]Verified[/]", "ClinicalTrials")
claims.add_row("Cost reduction 60%", "[yellow]Partial[/]", "Estimate")

console.print(claims)
pause(1.5)

# STEP 6
step("STEP 6: EXPORT REPORT")

console.print("  [green]>[/] Report saved: [cyan]./reports/analysis.json[/]")
console.print("  [green]>[/] PDF export:   [cyan]./reports/analysis.pdf[/]")
pause(1)

# FOOTER
console.print()
footer = Panel(
    Align.center(
        "[dim]Claude | GPT-4 | Gemini | Grok | Perplexity[/]\n"
        "[bold cyan]github.com/jjshay/news-intelligence[/]"
    ),
    title="[dim]News Intelligence v2.1[/]",
    border_style="dim",
    width=55
)
console.print(footer)
pause(3)
