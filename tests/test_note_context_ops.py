from __future__ import annotations

import json
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import finalize_analysis_coverage as finalize  # noqa: E402
import note_index  # noqa: E402
import sync_review_issue  # noqa: E402
import update_analysis_coverage as coverage  # noqa: E402


class CoverageMappingTests(unittest.TestCase):
    def test_baseline_351_mapping(self) -> None:
        catalog = json.loads((ROOT / "sources/note/catalog.json").read_text(encoding="utf-8"))
        baseline = json.loads(
            (ROOT / "analysis/BASELINE_NOTE_IDS.json").read_text(encoding="utf-8")
        )
        baseline_ids = set(baseline["note_ids"])
        self.assertEqual(351, len(baseline_ids))

        grouped = note_index.grouped_cards()
        counts: Counter[str] = Counter()
        unmapped: list[str] = []
        for note_id in baseline_ids:
            current = catalog["articles"][note_id]
            cards = grouped.get(note_id, [])
            card = note_index.choose_canonical(cards) if cards else None
            if card and card["status"] in {"analyzed", "reviewed"}:
                counts["individual_card"] += 1
                continue
            phase = coverage.phase_for(note_id, current.get("published_at", ""))
            if phase:
                counts[phase[0]] += 1
            else:
                unmapped.append(note_id)

        self.assertEqual([], unmapped)
        self.assertEqual(
            {
                "phase_01": 60,
                "phase_02": 93,
                "phase_03": 73,
                "phase_04": 26,
                "phase_05": 16,
                "phase_06": 10,
                "individual_card": 73,
            },
            dict(counts),
        )

    def test_body_change_requires_review(self) -> None:
        entry = {
            "analysis_state": "covered",
            "covered_content_hash": "old",
            "covered_title": "title",
            "covered_published_at": "2026-01-01",
            "covered_public_status": "public",
        }
        current = {
            "content_hash": "new",
            "title": "title",
            "published_at": "2026-01-01",
            "public_status": "public",
        }
        self.assertIn(
            "body_changed_after_coverage",
            coverage.review_reasons(entry, current),
        )

    def test_pending_entry_is_reviewed_as_new(self) -> None:
        entry = {
            "analysis_state": "pending",
            "covered_content_hash": "",
            "covered_title": "",
            "covered_published_at": "",
            "covered_public_status": "",
        }
        current = {
            "content_hash": "hash",
            "title": "title",
            "published_at": "2026-07-01",
            "public_status": "public",
        }
        self.assertIn("new_or_unassigned", coverage.review_reasons(entry, current))


class BaselineProtectionTests(unittest.TestCase):
    def run_finalize(
        self,
        coverage_payload: dict,
        baseline_payload: dict,
    ) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            coverage_path = tmp_path / "COVERAGE.json"
            baseline_path = tmp_path / "BASELINE_NOTE_IDS.json"
            coverage_path.write_text(json.dumps(coverage_payload), encoding="utf-8")
            baseline_path.write_text(json.dumps(baseline_payload), encoding="utf-8")

            old_coverage = finalize.COVERAGE_PATH
            old_baseline = finalize.BASELINE_PATH
            try:
                finalize.COVERAGE_PATH = coverage_path
                finalize.BASELINE_PATH = baseline_path
                self.assertEqual(0, finalize.main())
            finally:
                finalize.COVERAGE_PATH = old_coverage
                finalize.BASELINE_PATH = old_baseline

            return json.loads(coverage_path.read_text(encoding="utf-8"))

    def test_backdated_new_article_is_reset_to_pending(self) -> None:
        result = self.run_finalize(
            {
                "updated_at": "2026-07-01T00:00:00+00:00",
                "articles": {
                    "baseline": {"analysis_state": "covered"},
                    "new-backdated": {
                        "analysis_state": "covered",
                        "coverage_type": "phase_bundle",
                        "analysis_unit": "phase_03",
                        "analysis_label": "第3期",
                        "analysis_ref": "analysis/PHASE_03.md",
                        "role": "",
                        "covered_at": "2026-07-01T00:00:00+00:00",
                        "covered_content_hash": "hash",
                        "covered_title": "title",
                        "covered_published_at": "2026-03-10",
                        "covered_public_status": "public",
                    },
                },
            },
            {"note_ids": ["baseline"]},
        )
        entry = result["articles"]["new-backdated"]
        self.assertEqual("pending", entry["analysis_state"])
        self.assertEqual("unassigned", entry["coverage_type"])
        self.assertEqual("", entry["covered_content_hash"])

    def test_manually_accepted_nonbaseline_article_is_preserved(self) -> None:
        result = self.run_finalize(
            {
                "updated_at": "2026-07-02T00:00:00+00:00",
                "articles": {
                    "baseline": {"analysis_state": "covered"},
                    "accepted": {
                        "analysis_state": "covered",
                        "coverage_type": "individual_card",
                        "analysis_unit": "individual_card",
                        "analysis_label": "修正",
                        "analysis_ref": "articles/cards/example.md",
                        "role": "修正",
                        "covered_at": "2026-07-01T00:00:00+00:00",
                        "covered_content_hash": "hash",
                        "covered_title": "title",
                        "covered_published_at": "2026-07-01",
                        "covered_public_status": "public",
                    },
                },
            },
            {"note_ids": ["baseline"]},
        )
        self.assertEqual("covered", result["articles"]["accepted"]["analysis_state"])


class ReviewIssueTests(unittest.TestCase):
    def test_empty_queue_is_inactive(self) -> None:
        text = """- 確認待ち：0件
- 責任ある保留：0件
- 直近同期の取得失敗：0件
"""
        self.assertFalse(sync_review_issue.queue_active(text))

    def test_any_queue_count_is_active(self) -> None:
        text = """- 確認待ち：1件
- 責任ある保留：0件
- 直近同期の取得失敗：0件
"""
        self.assertTrue(sync_review_issue.queue_active(text))


if __name__ == "__main__":
    unittest.main()
