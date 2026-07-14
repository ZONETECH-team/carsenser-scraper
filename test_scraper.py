import subprocess
import unittest
from unittest.mock import patch

import scraper


class FakePage:
    def goto(self, *args, **kwargs):
        return None

    def wait_for_timeout(self, *args, **kwargs):
        return None


class FakeContext:
    def new_page(self):
        return FakePage()


class FakeBrowser:
    def new_context(self, *args, **kwargs):
        return FakeContext()

    def close(self):
        return None


class FakeChromium:
    def launch(self, *args, **kwargs):
        return FakeBrowser()


class FakePlaywright:
    def __enter__(self):
        self.chromium = FakeChromium()
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False


class ScrapeInventoryTest(unittest.TestCase):
    def test_returns_inventory_when_all_detail_pages_succeed(self):
        car_links = [
            "https://example.test/usedcar/detail/1/",
            "https://example.test/usedcar/detail/2/",
        ]
        cars = [
            {"name": "車両1", "detail_link": car_links[0]},
            {"name": "車両2", "detail_link": car_links[1]},
        ]

        with (
            patch.object(scraper, "sync_playwright", return_value=FakePlaywright()),
            patch.object(scraper, "extract_car_links", return_value=car_links),
            patch.object(scraper, "extract_car_details", side_effect=cars),
            patch.object(scraper, "DETAIL_MAX_RETRIES", 1),
            patch.object(scraper.time, "sleep"),
        ):
            self.assertEqual(scraper.scrape_inventory(), cars)

    def test_retries_detail_page_until_success(self):
        car_links = ["https://example.test/usedcar/detail/1/"]
        car_data = {"name": "車両1", "detail_link": car_links[0]}

        with (
            patch.object(scraper, "sync_playwright", return_value=FakePlaywright()),
            patch.object(scraper, "extract_car_links", return_value=car_links),
            patch.object(scraper, "extract_car_details", side_effect=[None, car_data]) as extract_details,
            patch.object(scraper, "DETAIL_MAX_RETRIES", 2),
            patch.object(scraper, "RETRY_DELAY", 0),
            patch.object(scraper.time, "sleep"),
        ):
            self.assertEqual(scraper.scrape_inventory(), [car_data])
            self.assertEqual(extract_details.call_count, 2)

    def test_returns_empty_when_any_detail_page_fails_after_retries(self):
        car_links = [
            "https://example.test/usedcar/detail/1/",
            "https://example.test/usedcar/detail/2/",
        ]
        car_data = {
            "name": "車両1",
            "detail_link": car_links[0],
        }

        with (
            patch.object(scraper, "sync_playwright", return_value=FakePlaywright()),
            patch.object(scraper, "extract_car_links", return_value=car_links),
            patch.object(scraper, "extract_car_details", side_effect=[car_data, None, None]),
            patch.object(scraper, "DETAIL_MAX_RETRIES", 2),
            patch.object(scraper, "RETRY_DELAY", 0),
            patch.object(scraper.time, "sleep"),
        ):
            self.assertEqual(scraper.scrape_inventory(), [])


class GitCommitAndPushTest(unittest.TestCase):
    def test_returns_success_without_commit_when_inventory_file_has_no_staged_diff(self):
        calls = []

        def fake_run(args, **kwargs):
            calls.append(args)
            if args == ['git', 'diff', '--cached', '--quiet', '--', scraper.OUTPUT_FILE]:
                return subprocess.CompletedProcess(args, 0)
            return subprocess.CompletedProcess(args, 0, stdout="")

        with (
            patch.dict(scraper.os.environ, {"GITHUB_TOKEN": "token"}),
            patch.object(scraper.subprocess, "run", side_effect=fake_run),
        ):
            self.assertTrue(scraper.git_commit_and_push())

        self.assertIn(['git', 'add', scraper.OUTPUT_FILE], calls)
        self.assertNotIn(['git', 'commit', '-m'], [call[:3] for call in calls])
        self.assertNotIn(['git', 'push'], calls)

    def test_commits_and_pushes_when_inventory_file_has_staged_diff(self):
        calls = []

        def fake_run(args, **kwargs):
            calls.append(args)
            if args == ['git', 'diff', '--cached', '--quiet', '--', scraper.OUTPUT_FILE]:
                return subprocess.CompletedProcess(args, 1)
            if args == ['git', 'config', '--get', 'remote.origin.url']:
                return subprocess.CompletedProcess(args, 0, stdout="git@github.com:example/repo.git\n")
            return subprocess.CompletedProcess(args, 0, stdout="")

        with (
            patch.dict(scraper.os.environ, {"GITHUB_TOKEN": "token"}),
            patch.object(scraper.subprocess, "run", side_effect=fake_run),
        ):
            self.assertTrue(scraper.git_commit_and_push())

        self.assertIn(['git', 'add', scraper.OUTPUT_FILE], calls)
        self.assertTrue(any(call[:3] == ['git', 'commit', '-m'] for call in calls))
        self.assertIn(['git', 'push'], calls)


if __name__ == "__main__":
    unittest.main()
