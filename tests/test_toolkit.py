from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from openarena_eval.common import default_data_dir, read_json, write_jsonl_atomic
from openarena_eval.evaluator import OpenArenaEvaluator, extract_candidate
from openarena_eval.leaderboard import pull_leaderboard
from openarena_eval.sync import refresh


class ToolkitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data_dir = default_data_dir()
        cls.evaluator = OpenArenaEvaluator(cls.data_dir, timeout_seconds=30)

    def test_snapshot_validates(self) -> None:
        result = self.evaluator.validate()
        self.assertTrue(result["valid"], result["errors"])
        manifest = read_json(self.data_dir / "manifest.json")
        self.assertEqual(result["problems"], manifest["problem_count"])
        self.assertGreaterEqual(result["problems"], 17)

    def test_reproduces_difference_bases_score(self) -> None:
        result = self.evaluator.score_candidate(
            "difference-bases", {"set": [0, 1]}
        )
        self.assertTrue(result["valid"], result)
        self.assertEqual(result["raw_score"], 4.0)
        self.assertEqual(result["directional_score"], -4.0)

    def test_strict_model_output_parser(self) -> None:
        candidate, status = extract_candidate(
            'work\nFINAL_CANDIDATE_JSON:\n{"set":[0,1]}'
        )
        self.assertEqual(candidate, {"set": [0, 1]})
        self.assertEqual(status, "ok")
        candidate, status = extract_candidate(
            'FINAL_CANDIDATE_JSON:\n{"set":[0,1]}\nextra'
        )
        self.assertIsNone(candidate)
        self.assertEqual(status, "trailing_text_after_json")

    def test_offline_refresh_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copied = Path(directory) / "data"
            shutil.copytree(self.data_dir, copied)
            snapshot_dir = copied / "official_snapshot" / "problems"
            payloads = {
                path.stem: read_json(path)
                for path in snapshot_dir.glob("*.json")
            }
            listing = [
                {
                    "id": payload.get("id") or index,
                    "slug": slug,
                    "title": payload["title"],
                    "scoring": payload["scoring"],
                    "evaluationMode": "construction",
                }
                for index, (slug, payload) in enumerate(payloads.items(), start=1)
            ]
            result = refresh(
                copied,
                base_url="https://fixture.invalid",
                timeout=1,
                retries=0,
                problems_payload=listing,
                problem_payloads=payloads,
            )
            self.assertEqual(result["problem_count"], len(listing))
            self.assertEqual(result["new_problem_slugs"], [])
            validation = OpenArenaEvaluator(copied).validate()
            self.assertTrue(validation["valid"], validation["errors"])

    def test_offline_leaderboard_with_local_result(self) -> None:
        manifest = read_json(self.data_dir / "manifest.json")
        snapshot_dir = self.data_dir / "official_snapshot" / "problems"
        problem_payloads = {
            path.stem: read_json(path)
            for path in snapshot_dir.glob("*.json")
        }
        listing = []
        leaderboards = {}
        for index, slug in enumerate(manifest["open_problem_slugs"], start=1):
            payload = problem_payloads[slug]
            listing.append(
                {
                    "id": index,
                    "slug": slug,
                    "title": payload["title"],
                    "scoring": payload["scoring"],
                }
            )
            leaderboards[slug] = [
                {
                    "rank": 1,
                    "agentName": "fixture-agent",
                    "bestScore": 1.0,
                    "submissions": 1,
                }
            ]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            local_results = root / "results.jsonl"
            write_jsonl_atomic(
                local_results,
                [
                    {
                        "slug": "difference-bases",
                        "valid": True,
                        "raw_score": 4.0,
                    }
                ],
            )
            result = pull_leaderboard(
                self.data_dir,
                root / "outputs",
                top_k=1,
                leaderboard_limit=1,
                local_results=local_results,
                local_label="fixture-local",
                snapshot="fixture",
                problems_payload=listing,
                leaderboard_payloads=leaderboards,
            )
            output = Path(result["output_dir"])
            self.assertTrue((output / "overview.csv").is_file())
            self.assertTrue((output / "leaderboard.csv").is_file())
            self.assertTrue((output / "leaderboard.xlsx").is_file())
            raw = json.loads((output / "raw.json").read_text(encoding="utf-8"))
            self.assertEqual(raw["snapshot"], "fixture")


if __name__ == "__main__":
    unittest.main()
