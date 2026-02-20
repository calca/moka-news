#!/usr/bin/env python3
"""
Example: Poster generation with PosterContentGenerator

This example demonstrates:
1. Using PosterContentGenerator to distil an editorial into a concise poster summary
2. Customising the AI prompt (inline or via config file)
3. Generating the final 9:16 PNG poster with PosterGenerator

Press 'g' inside the TUI to trigger the same flow interactively.
"""

import tempfile
from pathlib import Path
from moka_news.barista import SimpleBarista
from moka_news.poster import PosterContentGenerator, PosterGenerator


# ── sample editorial ──────────────────────────────────────────────────────────

SAMPLE_EDITORIAL = {
    "title": "The Week in Tech: Breakthroughs and Bold Moves",
    "content": """\
The past week has been one of the most eventful in recent memory for the
technology sector. Across the Atlantic, legislators finalised a sweeping AI
governance framework that obligates large model providers to publish safety
audits — a move that analysts say will reshape how frontier labs operate.

Meanwhile, quantum computing edged closer to practical relevance. A joint team
from two leading universities demonstrated a 1,000-qubit processor running
real-world optimisation algorithms with error rates below one percent. The
implications for logistics, drug discovery, and cryptography are hard to
overstate.

On the open-source front, a new programming language designed exclusively for
AI workloads attracted fifteen thousand GitHub stars within its first
forty-eight hours. Its core promise — eliminating an entire class of memory
bugs common in GPU kernels — resonated with engineers tired of debugging
CUDA crashes at 2 AM.

Finally, the social-media landscape witnessed another reshuffling. A previously
niche, chronological-feed platform surpassed fifty million daily active users,
suggesting that not everyone has made peace with algorithmic curation.

The thread running through all of these stories is acceleration: faster chips,
faster regulation, faster adoption. Whether the guardrails keep pace remains the
defining question of this technological era.
""",
}


# ── demo 1: PosterContentGenerator with SimpleBarista (no real AI) ───────────

def demo_no_ai():
    """Without an AI provider the full editorial text is returned as-is."""
    print("=" * 70)
    print("Demo 1: PosterContentGenerator — no AI provider (passthrough)")
    print("=" * 70)

    gen = PosterContentGenerator(ai_provider=None)
    text = gen.generate(SAMPLE_EDITORIAL)

    print(f"Content length: {len(text.split())} words")
    print(f"First 200 chars: {text[:200]}…\n")


# ── demo 2: PosterContentGenerator with a real AIProvider ────────────────────

def demo_with_ai(ai_provider):
    """With an AI provider the editorial is condensed to ≤300 words."""
    print("=" * 70)
    print("Demo 2: PosterContentGenerator — with AI provider (English)")
    print("=" * 70)

    gen = PosterContentGenerator(ai_provider=ai_provider, language="en")
    text = gen.generate(SAMPLE_EDITORIAL)

    word_count = len(text.split())
    print(f"AI-generated summary  ({word_count} words):")
    print("-" * 40)
    print(text)
    print()


def demo_language(ai_provider):
    """Language is inherited from the editorial config — poster summary matches."""
    print("=" * 70)
    print("Demo 2b: PosterContentGenerator — language injection (Italian)")
    print("=" * 70)

    # Simulate an editorial generator configured for Italian.
    # In production this is taken automatically from editorial_generator.language.
    gen = PosterContentGenerator(ai_provider=ai_provider, language="it")
    print(f"Effective system_message (truncated):")
    print("  ", gen.prompt_config["system_message"][:120], "…")
    text = gen.generate(SAMPLE_EDITORIAL)
    word_count = len(text.split())
    print(f"Summary ({word_count} words — would be Italian with a real AI provider):")
    print("-" * 40)
    print(text[:300], "…")
    print()


# ── demo 3: custom prompt ─────────────────────────────────────────────────────

def demo_custom_prompt(ai_provider):
    """Custom prompt — more punchy, social-media style."""
    print("=" * 70)
    print("Demo 3: PosterContentGenerator — custom prompt")
    print("=" * 70)

    custom_prompt = {
        "system_message": (
            "You write razor-sharp, social-media-ready news bullets. "
            "Your sentences are short, punchy, and never exceed 15 words each."
        ),
        "user_prompt": (
            "Summarise this editorial in 5 punchy bullet points (each ≤ 15 words).\n"
            "Return only the bullets, no introduction.\n\n{content}"
        ),
    }

    gen = PosterContentGenerator(ai_provider=ai_provider, prompt_config=custom_prompt)
    text = gen.generate(SAMPLE_EDITORIAL)

    print("Custom-style summary:")
    print("-" * 40)
    print(text)
    print()


# ── demo 4: end-to-end poster PNG generation ─────────────────────────────────

def demo_generate_poster(ai_provider):
    """Full pipeline: AI summary → PIL poster → saves PNG to a temp directory."""
    print("=" * 70)
    print("Demo 4: Full pipeline — AI summary + PosterGenerator")
    print("=" * 70)

    try:
        from PIL import Image  # noqa: F401
    except ImportError:
        print("⚠️  Pillow not installed – skipping poster render.")
        print("   Install with: pip install Pillow\n")
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        poster_config = {
            "method": "local",
            "default_template": "minimal",
            # Override the AI prompt inline (mirrors moka-news.yaml poster.content_prompt)
            "content_prompt": {
                "system_message": "You are a sharp news editor writing poster captions.",
                "user_prompt": (
                    "Write a 100-word max poster caption for this editorial.\n\n{content}"
                ),
            },
        }

        # 1. Generate AI content
        content_gen = PosterContentGenerator(
            ai_provider=ai_provider,
            prompt_config=poster_config.get("content_prompt"),
        )
        poster_content = content_gen.generate(SAMPLE_EDITORIAL)

        # 2. Generate poster image
        poster_gen = PosterGenerator(
            config=poster_config,
            posters_dir=Path(tmpdir),
        )
        editorial_data = {
            "title": SAMPLE_EDITORIAL["title"],
            "content": poster_content,
        }
        poster_path = poster_gen.generate_poster(editorial_data, template_name="minimal")

        print(f"✓ Poster saved: {poster_path}")
        print(f"  File size:  {poster_path.stat().st_size // 1024} KB")
        print()


# ── demo 5: configuration via YAML ───────────────────────────────────────────

def demo_yaml_config():
    """Show what the YAML config section looks like."""
    print("=" * 70)
    print("Demo 5: Configure poster content_prompt in moka-news.yaml")
    print("=" * 70)
    print("""
poster:
  method: local
  default_template: minimal

  # Customise the AI prompt that condenses the editorial for the poster.
  # Placeholder: {content} → full editorial markdown body.
  content_prompt:
    system_message: >
      You are an expert editorial journalist.
      Write a concise, impactful summary intended for a visual news poster.
    user_prompt: |
      Create a poster summary of the following editorial.
      Use clear, direct sentences.
      Maximum 300 words. Return only the summary text, no titles or labels.

      {content}

# Tips:
#   • Omit content_prompt entirely to keep the built-in default.
#   • Change the 300-word cap in user_prompt to any limit you prefer.
#   • Add a keywords_section key to nudge the AI toward specific topics.
""")


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    print("☕ MoKa News — Poster Generation Examples\n")

    # SimpleBarista works without any API key (pass-through, no real AI calls).
    # Replace with OpenAIBarista(), GeminiBarista(), etc. for real AI summaries.
    ai_provider = SimpleBarista()

    demo_no_ai()
    demo_with_ai(ai_provider)
    demo_language(ai_provider)
    demo_custom_prompt(ai_provider)
    demo_generate_poster(ai_provider)
    demo_yaml_config()

    print("=" * 70)
    print("Press 'g' inside the MoKa News TUI to generate a poster from the")
    print("current editorial using the AI provider you configured.")
    print("=" * 70)


if __name__ == "__main__":
    main()
