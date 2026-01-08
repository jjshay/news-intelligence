"""
Process checked articles from NEWS IN with AI scores
"""

import time
import requests
from datetime import datetime
from sheet_manager import SheetManager
from gamma_carousel_generator import GammaCarouselGenerator, classify_topic, JJSHAY_TEMPLATE_ID
from linkedin_api import LinkedInAPI, build_new_caption
from evernote_auto_poster import add_logo_to_pdf, shorten_url, log_post, extract_article_info_with_ai, generate_grok_teaser, generate_grok_keywords
from ai_rationale_generator import generate_all_rationales

LOGO_PATH = "/Users/johnshay/jj_shay_takeaways/jjshayt.png"

# Archive sheet for fully processed articles
ARCHIVE3_SHEET = 'ARCHIVE3'

# NEWS IN column indices (0-based)
# Headers: TOPIC, SELECT, SCORE, DATE, TITLE, LINK, PUBLIHER, GPT Score, Claude Score, Gemini Score, Grok Score, Perplexity Score, Source Score, AI Avg, GPT POV
# NOTE: Data is shifted - actual TITLE is in DATE column (3), LINK in TITLE column (4), etc.
COL = {
    'topic': 0,       # TOPIC - correct
    'select': 1,      # SELECT (TRUE/FALSE) - correct
    'score': 2,       # SCORE - correct
    'date': -1,       # DATE column doesn't exist in data (title is there instead)
    'title': 3,       # Actual title is in column 3 (DATE header)
    'link': 4,        # Actual link is in column 4 (TITLE header)
    'publisher': 5,   # Actual publisher is in column 5 (LINK header)
    'author': 6,      # Author is in column 6 (PUBLIHER header)
    'gpt_score': 7,
    'claude_score': 8,
    'gemini_score': 9,
    'grok_score': 10,
    'perplexity_score': 11,
    'source_score': 12,
    'ai_avg': 13,
    'gpt_pov': 14,
    'claude_pov': -1,  # No Claude POV in NEWS IN
    'gemini_pov': -1,  # No Gemini POV in NEWS IN
    'grok_pov': -1,    # No Grok POV in NEWS IN
    'perplexity_pov': -1,  # No Perplexity POV in NEWS IN
    'source': -1,
}


def get_cell(row, col_name):
    """Safely get cell value"""
    idx = COL.get(col_name, -1)
    if idx >= 0 and idx < len(row):
        return row[idx]
    return ''


def archive_to_archive3(sm, row, row_num, short_link, short_linkedin_url, gamma_url, topic_display=''):
    """Move processed article from NEWS IN to ARCHIVE3 with completion data and topic"""
    try:
        # Get or create ARCHIVE3 sheet
        try:
            archive_sheet = sm.spreadsheet.worksheet(ARCHIVE3_SHEET)
        except:
            archive_sheet = sm.spreadsheet.add_worksheet(ARCHIVE3_SHEET, rows=1000, cols=30)
            # Add headers with Topic column
            headers = ['x', 'SCORE', 'Date', 'Title', 'Link', 'Publisher', 'Author',
                      'GPT Score', 'Claude Score', 'Gemini Score', 'Grok Score', 'Perplexity Score',
                      'AI Avg', 'Source Score', 'GPT POV', 'Claude POV', 'Gemini POV', 'Grok POV',
                      'Perplexity POV', 'Source', 'Bit.ly Link', 'LinkedIn URL', 'Gamma URL', 'Topic', 'Posted Date']
            archive_sheet.append_row(headers)

        # Ensure headers exist
        if archive_sheet.row_count == 0 or not archive_sheet.cell(1, 1).value:
            headers = ['x', 'SCORE', 'Date', 'Title', 'Link', 'Publisher', 'Author',
                      'GPT Score', 'Claude Score', 'Gemini Score', 'Grok Score', 'Perplexity Score',
                      'AI Avg', 'Source Score', 'GPT POV', 'Claude POV', 'Gemini POV', 'Grok POV',
                      'Perplexity POV', 'Source', 'Bit.ly Link', 'LinkedIn URL', 'Gamma URL', 'Topic', 'Posted Date']
            archive_sheet.append_row(headers)

        # Build archive row: original data + completion columns
        archive_row = list(row)
        # Pad to ensure we have enough columns
        while len(archive_row) < 20:
            archive_row.append('')

        # Add completion data including topic
        archive_row.append(short_link)           # Bit.ly Link (article)
        archive_row.append(short_linkedin_url)   # LinkedIn URL
        archive_row.append(gamma_url)            # Gamma URL
        archive_row.append(topic_display)        # Topic (e.g., "41 Artificial Intelligence")
        archive_row.append(datetime.now().strftime('%Y-%m-%d %H:%M'))  # Posted Date

        # Append to ARCHIVE3
        archive_sheet.append_row(archive_row)

        # Delete from NEWS IN
        source_sheet = sm.spreadsheet.worksheet('NEWS IN')
        source_sheet.delete_rows(row_num)

        print(f"✓ Archived to {ARCHIVE3_SHEET} and removed from NEWS IN")
        return True

    except Exception as e:
        print(f"Archive error: {e}")
        return False


def process_news_in_article(sm, row, row_num):
    """Process a single article from NEWS IN sheet with AI scores"""

    title = get_cell(row, 'title') or 'News Update'
    link = get_cell(row, 'link') or ''
    publisher = get_cell(row, 'publisher') or 'News'
    author = get_cell(row, 'author') or ''

    # ========================================
    # CONTENT VALIDATION - Skip incomplete articles
    # ========================================
    try:
        from content_validator import ContentValidator, INSUFFICIENT_CONTENT_PENALTY

        print(f"\n📋 Validating content for: {title[:40]}...")
        validator = ContentValidator()
        validation = validator.validate_article(link)

        if not validation.is_sufficient:
            print(f"⚠️  SKIPPING - Insufficient content:")
            print(f"   Reason: {validation.reason}")
            print(f"   Word count: {validation.word_count} (min: 300)")
            print(f"   Data points: {validation.data_points_count} (min: 2)")
            print(f"   → Article would receive -{INSUFFICIENT_CONTENT_PENALTY} penalty")
            print(f"   → Skipping to prevent hallucinated 'By The Numbers' data")
            return None  # Skip this article
        else:
            print(f"✅ Content validated: {validation.word_count} words, {validation.data_points_count} data points")
            # Store extracted data points for use in carousel
            row_data_points = validation.data_points_found[:3] if validation.data_points_found else []
    except ImportError:
        print("⚠️  Content validator not available - proceeding without validation")
        row_data_points = []
    except Exception as e:
        print(f"⚠️  Content validation error: {e} - proceeding anyway")
        row_data_points = []

    # Get AI scores and POVs - 5 AI models (80% weighting) + 2 news sources (20% weighting)
    # Each AI model contributes 16% (80% / 5 models)
    # News reliability contributes 20% total (split between available sources)
    ai_scores = {}

    gpt_score = get_cell(row, 'gpt_score')
    if gpt_score:
        ai_scores['ChatGPT'] = {
            'score': gpt_score,
            'weighting': '16%',
            'rationale': get_cell(row, 'gpt_pov')
        }

    claude_score = get_cell(row, 'claude_score')
    if claude_score:
        ai_scores['Claude'] = {
            'score': claude_score,
            'weighting': '16%',
            'rationale': get_cell(row, 'claude_pov')
        }

    gemini_score = get_cell(row, 'gemini_score')
    if gemini_score:
        ai_scores['Gemini'] = {
            'score': gemini_score,
            'weighting': '16%',
            'rationale': get_cell(row, 'gemini_pov')
        }

    grok_score = get_cell(row, 'grok_score')
    if grok_score:
        ai_scores['Grok'] = {
            'score': grok_score,
            'weighting': '16%',
            'rationale': get_cell(row, 'grok_pov')
        }

    perplexity_score = get_cell(row, 'perplexity_score')
    if perplexity_score:
        ai_scores['Perplexity'] = {
            'score': perplexity_score,
            'weighting': '16%',
            'rationale': get_cell(row, 'perplexity_pov')
        }

    # Add both news sources - 20% total (10% each)
    # Source score from sheet, default to 85 if not provided
    source_score = get_cell(row, 'source_score') or '85'

    ai_scores['NewsAPI'] = {
        'score': source_score,
        'weighting': '10%',
        'rationale': 'News aggregator reliability'
    }
    ai_scores['NewsData'] = {
        'score': source_score,
        'weighting': '10%',
        'rationale': 'News aggregator reliability'
    }

    # Calculate consensus score as weighted average from actual AI scores
    # 5 AI models = 80% (16% each), 2 news sources = 20% (10% each)
    total_weighted = 0
    total_weight = 0

    for name, data in ai_scores.items():
        try:
            score = float(data.get('score', 0))
            weight_str = data.get('weighting', '0%').replace('%', '')
            weight = float(weight_str) / 100
            total_weighted += score * weight
            total_weight += weight
        except (ValueError, TypeError):
            pass

    if total_weight > 0:
        consensus_score = round(total_weighted / total_weight)
    else:
        consensus_score = get_cell(row, 'ai_avg') or get_cell(row, 'score') or '85'

    consensus_score = str(consensus_score)

    # Classify topic into second-level category
    topic = classify_topic(title)
    topic_display = topic['display'] if topic else 'Uncategorized'
    topic_section = topic['section_name'] if topic else ''

    print(f"\n{'='*60}")
    print(f"Processing: {title[:50]}...")
    print(f"Topic: {topic_display} ({topic_section})")
    print(f"AI Radar Score: {consensus_score}")
    print(f"{'='*60}")

    # Fetch article content for AI extraction
    print("Fetching article content...")
    try:
        response = requests.get(link, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        content = response.text[:5000]
    except:
        content = title

    # Use AI to extract key info
    print("Extracting info with AI...")
    extracted = extract_article_info_with_ai(title, content, author)

    # Generate fresh rationales from each AI model (GPT-4o, Claude 3.5, Gemini 1.5, Grok)
    print("Generating AI rationales from latest models...")
    summary_text = extracted.get('summary', title)
    ai_input_scores = {
        'claude': get_cell(row, 'claude_score') or '90',
        'chatgpt': get_cell(row, 'gpt_score') or '90',
        'grok': get_cell(row, 'grok_score') or '90',
        'gemini': get_cell(row, 'gemini_score') or '90'
    }

    consensus_explanation = ''  # Initialize before try block
    try:
        rationale_results = generate_all_rationales(title, summary_text, ai_input_scores)

        # Update ai_scores with fresh rationales
        if rationale_results:
            if 'Claude' in ai_scores and rationale_results.get('claude', {}).get('rationale'):
                ai_scores['Claude']['rationale'] = rationale_results['claude']['rationale']
            if 'ChatGPT' in ai_scores and rationale_results.get('chatgpt', {}).get('rationale'):
                ai_scores['ChatGPT']['rationale'] = rationale_results['chatgpt']['rationale']
            if 'Grok' in ai_scores and rationale_results.get('grok', {}).get('rationale'):
                ai_scores['Grok']['rationale'] = rationale_results['grok']['rationale']
            if 'Gemini' in ai_scores and rationale_results.get('gemini', {}).get('rationale'):
                ai_scores['Gemini']['rationale'] = rationale_results['gemini']['rationale']

            # Get consensus explanation
            consensus_explanation = rationale_results.get('consensus', {}).get('explanation', '')
            if rationale_results.get('consensus', {}).get('score'):
                consensus_score = str(rationale_results['consensus']['score'])
    except Exception as e:
        print(f"Warning: AI rationale generation failed: {e}")

    # Shorten article link with custom title slug
    short_link = shorten_url(link, title) if link else ''

    # Prepare article data for carousel WITH AI SCORES and TOPIC
    article_data = {
        'title': title,
        'publication': publisher,
        'author': author,
        'link': short_link,
        'summary': extracted.get('summary', ''),
        'data_points': extracted.get('data_points', []),
        'quote': extracted.get('quote', ''),
        'quote2': extracted.get('quote2', ''),
        'key_insights': extracted.get('key_insights', []),
        'strategic_take': extracted.get('strategic_take', ''),
        'ai_scores': ai_scores,
        'consensus_score': consensus_score,
        'consensus_explanation': consensus_explanation,
        'topic': topic  # Second-level category (e.g., "41 Artificial Intelligence")
    }

    # Generate carousel from JJ Shay v3 template (with logos)
    # Uses Claude Vision review loop - regenerates if issues found
    print("Generating carousel from template (with vision review)...")
    generator = GammaCarouselGenerator()
    result = generator.generate_with_review(JJSHAY_TEMPLATE_ID, article_data, export_format="pdf", max_attempts=2)

    if not result:
        print("ERROR: Carousel generation failed")
        return False

    gamma_url = result.get('gamma_url')
    pdf_url = result.get('export_url')
    print(f"Gamma URL: {gamma_url}")

    # Add logo to PDF and AI scores table on slide 7
    print("Adding logo to PDF...")
    pdf_with_logo = "/Users/johnshay/jj_shay_takeaways/carousel_with_logo.pdf"
    add_logo_to_pdf(pdf_url, pdf_with_logo, ai_scores=ai_scores)

    # Generate Grok teaser (2 sentences, executive-level, 100% truthful)
    summary = extracted.get('summary', '')
    print("Generating Grok teaser...")
    teaser = generate_grok_teaser(title, summary)
    print(f"Teaser: {teaser[:100]}...")

    # Generate keywords with Grok (3 only, no hashtags)
    print("Generating keywords...")
    keywords = generate_grok_keywords(title, summary)
    print(f"Keywords: {keywords}")

    # Build caption: Grok teaser, article link, Recent Posts, 3 keywords (NO consensus)
    caption = build_new_caption(teaser, short_link, keywords)

    # Post to LinkedIn
    print("Posting to LinkedIn...")
    linkedin = LinkedInAPI()

    if not linkedin.access_token:
        print("ERROR: LinkedIn not authenticated")
        return False

    post_urn = linkedin.create_carousel_post(pdf_with_logo, title, caption)

    if not post_urn:
        print("ERROR: LinkedIn post failed")
        return False

    linkedin_url = f"https://www.linkedin.com/feed/update/{post_urn}"
    short_linkedin_url = shorten_url(linkedin_url)
    print(f"Posted! {linkedin_url}")
    print(f"Short URL: {short_linkedin_url}")

    # Log the post with topic tracking
    log_post({
        "date_posted": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "title": title,
        "publication": publisher,
        "linkedin_urn": post_urn,
        "linkedin_url": linkedin_url,
        "short_url": short_linkedin_url,
        "article_link": short_link,  # Article bitly for Recent News section
        "gamma_url": gamma_url,
        "summary": extracted.get('summary', '')[:200],
        "consensus_score": consensus_score,
        "topic_code": topic['code'] if topic else None,
        "topic_name": topic['name'] if topic else 'Uncategorized',
        "topic_section": topic['section_name'] if topic else '',
        "status": "Posted"
    })

    # Archive to ARCHIVE3 (moves row from NEWS OUT, adds bit.ly links, gamma URL, and topic)
    archive_to_archive3(sm, row, row_num, short_link, short_linkedin_url, gamma_url, topic_display)

    print(f"✓ Complete! Archived row {row_num} to ARCHIVE3")
    return True


def process_all_checked():
    """Process all checked articles from NEWS IN"""
    sm = SheetManager()
    sheet = sm.spreadsheet.worksheet('NEWS IN')
    all_rows = sheet.get_all_values()

    checked_articles = []
    for i, row in enumerate(all_rows[1:], start=2):
        checkbox = get_cell(row, 'select')
        # Check for TRUE, true, or x
        if str(checkbox).upper() in ['TRUE', 'X']:
            checked_articles.append((i, row))

    print(f"Found {len(checked_articles)} checked articles to process")

    # Process in REVERSE order (highest row first) so deletions don't shift remaining indices
    processed = 0
    skipped = 0
    for row_num, row in reversed(checked_articles):
        result = process_news_in_article(sm, row, row_num)
        if result is None:
            skipped += 1
            print(f"   → Skipped (insufficient content)")
        else:
            processed += 1
        time.sleep(5)  # Brief pause between posts

    print("\n" + "="*60)
    print(f"ALL DONE! Processed: {processed}, Skipped: {skipped}")
    print("="*60)


if __name__ == "__main__":
    process_all_checked()
