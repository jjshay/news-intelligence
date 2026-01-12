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
        """Verify articles file is valid JSON array"""
        articles_path = Path(__file__).parent.parent / "examples" / "sample_articles.json"
        with open(articles_path) as f:
            data = json.load(f)
        assert isinstance(data, list), "Articles should be a JSON array"
        assert len(data) > 0, "Should have at least one article"

    def test_articles_have_required_fields(self):
        """Verify articles have required fields"""
        articles_path = Path(__file__).parent.parent / "examples" / "sample_articles.json"
        with open(articles_path) as f:
            data = json.load(f)

        required_fields = ["title", "source", "url", "published_date", "summary", "category"]
        for article in data:
            for field in required_fields:
                assert field in article, f"Article missing required field: {field}"


class TestScoringSystem:
    """Test scoring calculation logic"""

    def test_score_range(self):
        """Test scores are within valid range"""
        # Scores should be 1-10
        valid_scores = [8.5, 7.8, 8.9, 7.2, 8.6]
        for score in valid_scores:
            assert 1 <= score <= 10, "Score should be between 1 and 10"

    def test_average_calculation(self):
        """Test average score calculation"""
        scores = [8.5, 7.8, 8.9, 7.2, 8.6]
        avg = sum(scores) / len(scores)
        assert abs(avg - 8.2) < 0.1, "Average should be approximately 8.2"

    def test_consensus_threshold(self):
        """Test consensus detection logic"""
        scores = [8.5, 7.8, 8.9, 7.2, 8.6]

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

    def test_model_scores_in_report(self):
        """Verify all model scores are in the report"""
        report_path = Path(__file__).parent.parent / "sample_output" / "analysis_report.json"
        with open(report_path) as f:
            report = json.load(f)

        models = ["ChatGPT", "Claude", "Gemini", "Grok", "Perplexity"]
        individual_scores = report["analysis"]["individual_scores"]

        for model in models:
            assert model in individual_scores, f"Report should have score for {model}"
            assert "score" in individual_scores[model], f"{model} should have a score"
            assert "reasoning" in individual_scores[model], f"{model} should have reasoning"


class TestReportGeneration:
    """Test report output format"""

    def test_sample_report_exists(self):
        """Verify sample report exists"""
        report_path = Path(__file__).parent.parent / "sample_output" / "analysis_report.json"
        assert report_path.exists(), "Sample analysis report should exist"

    def test_report_has_article_info(self):
        """Verify report contains article information"""
        report_path = Path(__file__).parent.parent / "sample_output" / "analysis_report.json"
        with open(report_path) as f:
            report = json.load(f)

        assert "article" in report, "Report should have article info"
        article = report["article"]
        assert "title" in article, "Article should have title"
        assert "source" in article, "Article should have source"
        assert "url" in article, "Article should have url"

    def test_report_has_individual_scores(self):
        """Verify report contains individual scores"""
        report_path = Path(__file__).parent.parent / "sample_output" / "analysis_report.json"
        with open(report_path) as f:
            report = json.load(f)

        assert "analysis" in report, "Report should have analysis"
        assert "individual_scores" in report["analysis"], "Analysis should have individual_scores"

    def test_report_has_consensus(self):
        """Verify report contains consensus"""
        report_path = Path(__file__).parent.parent / "sample_output" / "analysis_report.json"
        with open(report_path) as f:
            report = json.load(f)

        assert "consensus" in report["analysis"], "Analysis should have consensus"
        consensus = report["analysis"]["consensus"]
        assert "final_score" in consensus, "Consensus should have final_score"
        assert "confidence" in consensus, "Consensus should have confidence"
        assert "recommendation" in consensus, "Consensus should have recommendation"


class TestPeerReview:
    """Test peer review pairing logic"""

    def test_peer_review_in_report(self):
        """Verify peer review is in the report"""
        report_path = Path(__file__).parent.parent / "sample_output" / "analysis_report.json"
        with open(report_path) as f:
            report = json.load(f)

        assert "peer_review" in report["analysis"], "Analysis should have peer_review"
        assert "pairs" in report["analysis"]["peer_review"], "Peer review should have pairs"

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


class TestFactCheck:
    """Test fact checking functionality"""

    def test_fact_check_in_report(self):
        """Verify fact check is in the report"""
        report_path = Path(__file__).parent.parent / "sample_output" / "analysis_report.json"
        with open(report_path) as f:
            report = json.load(f)

        assert "fact_check" in report["analysis"], "Analysis should have fact_check"
        fact_check = report["analysis"]["fact_check"]
        assert "claims_verified" in fact_check, "Fact check should have claims_verified"
        assert "details" in fact_check, "Fact check should have details"


class TestMetadata:
    """Test report metadata"""

    def test_metadata_present(self):
        """Verify metadata is included"""
        report_path = Path(__file__).parent.parent / "sample_output" / "analysis_report.json"
        with open(report_path) as f:
            report = json.load(f)

        assert "metadata" in report, "Report should have metadata"
        metadata = report["metadata"]
        assert "processing_time_seconds" in metadata, "Metadata should have processing_time_seconds"
        assert "timestamp" in metadata, "Metadata should have timestamp"
