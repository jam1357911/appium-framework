import json
import logging
import re
import time
from dataclasses import asdict, dataclass
from pathlib import Path

_ROOT = Path(__file__).parent.parent
REPORTS_DIR = _ROOT / "reports"

LOGGER_NAME = "appium_framework"
_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"

_logger = logging.getLogger(LOGGER_NAME)
_logger.setLevel(logging.INFO)

_current_run: "SessionRun | None" = None


def get_logger() -> logging.Logger:
    """Logger whose output is routed into the current case's log file."""
    return _logger


def _sanitize(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._") or "case"


@dataclass
class TestResult:
    nodeid: str
    name: str
    feature: str = ""
    scenario: str = ""
    outcome: str = "unknown"
    duration: float = 0.0
    error: str = ""


class SessionRun:
    """Collects the pass/fail results and per-case logs of one pytest session."""

    def __init__(self):
        self.dir = REPORTS_DIR / f"run_{time.strftime('%Y%m%d_%H%M%S')}"
        counter = 1
        while self.dir.exists():
            self.dir = REPORTS_DIR / f"run_{time.strftime('%Y%m%d_%H%M%S')}_{counter}"
            counter += 1
        self.logs_dir = self.dir / "logs"
        self.logs_dir.mkdir(parents=True)
        self.started_at = time.strftime("%Y-%m-%d %H:%M:%S")
        self.finished_at = ""
        self.results: dict[str, TestResult] = {}
        self.report_path: Path | None = None
        self._log_handler: logging.FileHandler | None = None

    def register_case(self, nodeid: str, name: str, feature: str, scenario: str):
        self.results[nodeid] = TestResult(nodeid=nodeid, name=name, feature=feature, scenario=scenario)

    def result_for(self, nodeid: str) -> TestResult | None:
        return self.results.get(nodeid)

    def open_case_log(self, case_name: str) -> Path:
        path = self.logs_dir / f"{_sanitize(case_name)}.log"
        handler = logging.FileHandler(path, mode="w", encoding="utf-8")
        handler.setFormatter(logging.Formatter(_LOG_FORMAT))
        _logger.addHandler(handler)
        self._log_handler = handler
        return path

    def close_case_log(self):
        if self._log_handler is not None:
            _logger.removeHandler(self._log_handler)
            self._log_handler.close()
            self._log_handler = None

    def counts(self) -> dict:
        summary = {"total": len(self.results), "passed": 0, "failed": 0, "error": 0, "skipped": 0, "unknown": 0}
        for result in self.results.values():
            key = result.outcome if result.outcome in summary else "unknown"
            summary[key] += 1
        return summary

    def write_report(self, exitstatus: int, platform: str) -> Path:
        self.finished_at = time.strftime("%Y-%m-%d %H:%M:%S")
        payload = {
            "session": {
                "started_at": self.started_at,
                "finished_at": self.finished_at,
                "platform": platform,
                "exitstatus": exitstatus,
            },
            "summary": self.counts(),
            "cases": [asdict(result) for result in self.results.values()],
        }
        self.report_path = self.dir / "session_report.json"
        self.report_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return self.report_path


def start_run() -> SessionRun:
    global _current_run
    _current_run = SessionRun()
    return _current_run


def current_run() -> SessionRun | None:
    return _current_run


def parse_feature_scenario(item) -> tuple[str, str]:
    """Extract (feature, scenario) from the docstring pytest-bdd puts on the test."""
    doc = getattr(getattr(item, "obj", None), "__doc__", "") or ""
    if ": " in doc:
        feature, scenario = doc.split(": ", 1)
        return feature.strip(), scenario.strip()
    return "", ""


def case_label(item) -> str:
    module = Path(item.nodeid.split("::")[0]).stem if "::" in item.nodeid else "case"
    return f"{module}__{item.name}"
