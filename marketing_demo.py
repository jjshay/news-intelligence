#!/usr/bin/env python3
"""Marketing Demo - News Intelligence"""
import time
import sys

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich import box
    console = Console()
except ImportError:
    print("Run: pip install rich")
    sys.exit(1)

def pause(seconds=2):
    time.sleep(seconds)

def clear():
    console.clear()

# SCENE 1: Hook
clear()
console.print("\n" * 5)
console.print("[bold yellow]                    TIRED OF READING FAKE NEWS?[/bold yellow]", justify="center")
pause(2)

# SCENE 2: Problem
clear()
console.print("\n" * 3)
console.print(Panel("""
[bold red]THE PROBLEM:[/bold red]

   • One AI can be wrong
   • Bias exists in every model
   • No single source of truth

[dim]You need MULTIPLE perspectives.[/dim]
""", title="❌ Single AI = Single Point of Failure", border_style="red", width=60), justify="center")
pause(3)

# SCENE 3: Solution
clear()
console.print("\n" * 3)
console.print(Panel("""
[bold green]THE SOLUTION:[/bold green]

   ✓ 5 AI models analyze every article
   ✓ They debate and fact-check each other
   ✓ You get the CONSENSUS score

[bold]Only trust news when 4+ AIs agree.[/bold]
""", title="✅ News Intelligence = 5 AIs Working Together", border_style="green", width=60), justify="center")
pause(3)

# SCENE 4: Example
clear()
console.print("\n\n")
console.print("[bold cyan]              📰 WATCH IT IN ACTION[/bold cyan]", justify="center")
console.print()
pause(1)

console.print(Panel("""
[bold]"AI Breakthrough: New Model Achieves Human-Level Reasoning"[/bold]

Source: MIT Technology Review
""", title="Article to Analyze", border_style="cyan", width=70), justify="center")
pause(2)

# SCENE 5: AI Scoring
clear()
console.print("\n\n")
console.print("[bold magenta]              🤖 5 AIs SCORE THE ARTICLE[/bold magenta]", justify="center")
console.print()
pause(1)

table = Table(box=box.ROUNDED, width=60)
table.add_column("AI Model", style="cyan", justify="center")
table.add_column("Score", justify="center")
table.add_column("Verdict", justify="center")

models = [
    ("ChatGPT", "8/10", "[green]✓ Trustworthy[/green]"),
    ("Claude", "7/10", "[green]✓ Trustworthy[/green]"),
    ("Gemini", "9/10", "[green]✓ Verified[/green]"),
    ("Grok", "7/10", "[yellow]⚠ Some Hype[/yellow]"),
    ("Perplexity", "8/10", "[green]✓ Fact-Checked[/green]"),
]

for model, score, verdict in models:
    table.add_row(model, score, verdict)
    console.print(table, justify="center")
    pause(0.5)
    console.clear()
    console.print("\n\n")
    console.print("[bold magenta]              🤖 5 AIs SCORE THE ARTICLE[/bold magenta]", justify="center")
    console.print()

console.print(table, justify="center")
pause(2)

# SCENE 6: Result
clear()
console.print("\n" * 3)
console.print(Panel("""
[bold green]
                    ████████████████████████
                    ██                    ██
                    ██    FINAL SCORE     ██
                    ██                    ██
                    ██      7.8 / 10      ██
                    ██                    ██
                    ██   ✅ SHARE THIS    ██
                    ██                    ██
                    ████████████████████████
[/bold green]

[bold]CONSENSUS:[/bold] 4 out of 5 AIs agree - this article is reliable.
""", title="📊 THE VERDICT", border_style="green", width=60), justify="center")
pause(3)

# SCENE 7: CTA
clear()
console.print("\n" * 4)
console.print("[bold yellow]         ⭐ NEVER SHARE FAKE NEWS AGAIN ⭐[/bold yellow]", justify="center")
console.print()
console.print("[bold white]           github.com/jjshay/news-intelligence[/bold white]", justify="center")
console.print()
console.print("[dim]                  pip install -r requirements.txt[/dim]", justify="center")
console.print("[dim]                  python demo.py[/dim]", justify="center")
pause(3)
