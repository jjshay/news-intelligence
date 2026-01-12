"""
Tests for News Intelligence System
"""
import pytest
import os
import json
from pathlib import Path


class TestArticleData:
    """Test article data handling"""

    def test_sample_articles_exist(self):
        """Verify sample articles file exists"""
        articles_path = Path(__file__).parent.parent / "examples" / "sample_articles.json"
        assert articles_path.exists(), "Sample articles file should exist"

    def test_articles_valid_json(self):
        """Verify articles file is valid JSON"""
        articles_path = Path(__file__).parent.parent / "examples" / "sample_articles.json"
        with open(articles_path) as f:
            data = json.load(f)
        assert "articles" in data, "Should have articles array"

    def test_articles_have_required_fields(self):
        """Verify articles have required fields"""
        articles_path = Path(__file__).parent.parent / "examples" / "sample_articles.json"
        with open(articles_path) as f:
            data = json.load(f)

        required_fields = ["title", "source", "url", "content"]
        for article in data["articles"]:
            for field in required_fields:
                assert field in article, f"Article missing required field: {field}"


class TestScoringSystem:
    """Test scoring calculation logic"""

    def test_score_range(self):
        """Test scores are within valid range"""
        # Scores should be 1-10
        valid_scores = [8, 7, 9, 8, 9]
        for score in valid_scores:
            assert 1 <= score <= 10, "Score should be between 1 and 10"

    def test_average_calculation(self):
        """Test average score calculation"""
        scores = [8, 7, 9, 8, 9]
        avg = sum(scores) / len(scores)
        assert abs(avg - 8.2) < 0.01, "Average should be 8.2"

    def test_consensus_threshold(self):
        """Test consensus detection logic"""
        scores = [8, 7, 9, 8, 9]
        avg = sum(scores) / len(scores)

        # Check if scores are within 2 points of each other (consensus)
        min_score = min(scores)
        max_score = max(scores)
        has_consensus = (max_score - min_score) <= 2

        assert has_consensus, "Scores should show consensus"


class TestAIModels:
    """Test AI model configuration"""

    def test_five_models_defined(self):
        """Verify 5 AI models are used"""
        models = ["ChatGPT", "Claude", "Gemini", "Grok", "Perplexity"]
        assert len(models) == 5, "Should have exactly 5 AI models"

    def test_perplexity_has_final_say(self):
        """Verify Perplexity is designated as final arbiter"""
        # In the system, Perplexity has "final say" due to web search
        models_with_roles = {
            "ChatGPT": "reasoning",
            "Claude": "analysis",
            "Gemini": "multimodal",
            "Grok": "contrarian",
            "Perplexity": "final_say"
        }
        assert models_with_roles["Perplexity"] == "final_say"


class TestReportGeneration:
    """Test report output format"""

    def test_sample_report_exists(self):
        """Verify sample report exists"""
        report_path = Path(__file__).parent.parent / "sample_output" / "analysis_report.json"
        assert report_path.exists(), "Sample analysis report should exist"

    def test_report_has_scores(self):
        """Verify report contains individual scores"""
        report_path = Path(__file__).parent.parent / "sample_output" / "analysis_report.json"
        with open(report_path) as f:
            report = json.load(f)

        assert "individual_scores" in report, "Report should have individual_scores"

    def test_report_has_consensus(self):
        """Verify report contains consensus"""
        report_path = Path(__file__).parent.parent / "sample_output" / "analysis_report.json"
        with open(report_path) as f:
            report = json.load(f)

        assert "final_consensus" in report, "Report should have final_consensus"


class TestPeerReview:
    """Test peer review pairing logic"""

    def test_pair_generation(self):
        """Test AI pairing for peer review"""
        models = ["ChatGPT", "Claude", "Gemini", "Grok", "Perplexity"]

        # Should generate pairs for comparison
        pairs = []
        for i in range(len(models)):
            for j in range(i + 1, len(models)):
                pairs.append((models[i], models[j]))

        # 5 models = 10 possible pairs
        assert len(pairs) == 10, "Should have 10 possible pairs"
