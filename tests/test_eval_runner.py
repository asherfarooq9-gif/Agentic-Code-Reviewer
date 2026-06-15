from src.agents.orchestrator import ReviewFinding
from src.db.models import Severity
from src.eval.dataset import load_cases
from src.eval.runner import run_eval
from src.llm.ollama_client import TokenUsage

CASES_DIR = "eval_data/cases"


def _reviewer_returning(findings):
    def reviewer(files, llm_client, *, deep=False):
        return findings, TokenUsage(0, 0, "fake")

    return reviewer


def test_load_seed_cases():
    cases = load_cases(CASES_DIR)
    assert len(cases) >= 2
    assert all(c.expected for c in cases)
    assert all(c.diff.strip() for c in cases)


def test_run_eval_perfect_score():
    cases = load_cases(CASES_DIR)
    case = cases[0]
    exp = case.expected[0]
    pred = [ReviewFinding(exp.file, exp.line, Severity.HIGH, exp.category, "m", None, 0.9)]
    report = run_eval([case], _reviewer_returning(pred), llm_client=None)
    assert report.overall.tp == 1
    assert report.overall.f1 == 1.0


def test_run_eval_empty_predictions():
    cases = load_cases(CASES_DIR)
    report = run_eval(cases, _reviewer_returning([]), llm_client=None)
    assert report.overall.tp == 0
    assert report.overall.recall == 0.0
    assert report.overall.fn >= 2
