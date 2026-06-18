import unittest

from redteam_llm.catalog import list_suites, load_catalog, validate_catalog, validate_suite
from redteam_llm.runner import run_cases
from redteam_llm.targets import vulnerable_mock_target


class CatalogTests(unittest.TestCase):
    def test_catalog_is_valid(self) -> None:
        techniques = load_catalog()
        result = validate_catalog(techniques)
        self.assertEqual(result.errors, [])
        self.assertEqual(len(techniques), 88)

    def test_suites_reference_existing_techniques(self) -> None:
        techniques = load_catalog()
        for suite in list_suites():
            result = validate_suite(suite, techniques)
            self.assertEqual(result.errors, [], suite.id)

    def test_mock_runner_records_detector_findings(self) -> None:
        techniques = load_catalog()
        suite = next(suite for suite in list_suites() if suite.id == "quick-smoke")
        cases = run_cases(suite, techniques, vulnerable_mock_target, limit=1)
        self.assertEqual(len(cases), 1)
        self.assertTrue(cases[0].findings)


if __name__ == "__main__":
    unittest.main()
