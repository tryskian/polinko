import unittest

from polinko.api.manual_eval_contracts import SOURCE_FIRST_SCHEMA_VERSION
from tools import api_smoke


def _source_first_payload() -> dict[str, object]:
    return {
        "schema_version": SOURCE_FIRST_SCHEMA_VERSION,
        "contract": {
            "summary_unit": "lane_summary",
            "promotion_gate": "repeated_lane_signal",
        },
    }


def _data_freshness_payload() -> dict[str, object]:
    return {
        "state": "current",
        "manual_evals_db": {
            "schema_current": True,
        },
    }


class ApiSmokeTests(unittest.TestCase):
    def test_manual_evals_surface_validation_accepts_versioned_source_first(
        self,
    ) -> None:
        api_smoke._validate_manual_evals_surface_payload(
            {
                "available": False,
                "source_first": _source_first_payload(),
                "data_freshness": _data_freshness_payload(),
            }
        )

    def test_pass_fail_data_validation_accepts_versioned_source_first(self) -> None:
        api_smoke._validate_pass_fail_data_payload(
            {
                "source_first": _source_first_payload(),
                "data_freshness": _data_freshness_payload(),
            }
        )

    def test_source_first_validation_rejects_retired_rollup_alias(self) -> None:
        payload = _source_first_payload()
        contract = payload["contract"]
        assert isinstance(contract, dict)
        contract["rollup_unit"] = "lane_summary"

        with self.assertRaisesRegex(RuntimeError, "rollup_unit"):
            api_smoke._validate_pass_fail_data_payload(
                {
                    "source_first": payload,
                    "data_freshness": _data_freshness_payload(),
                }
            )

    def test_data_freshness_validation_accepts_stale_local_manual_eval_db(
        self,
    ) -> None:
        api_smoke._validate_manual_evals_surface_payload(
            {
                "available": True,
                "source_first": _source_first_payload(),
                "data_freshness": {
                    "state": "stale",
                    "manual_evals_db": {
                        "schema_current": False,
                    },
                },
            }
        )


if __name__ == "__main__":
    unittest.main()
