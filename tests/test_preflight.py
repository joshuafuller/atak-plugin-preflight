import unittest

import preflight


class PreflightTests(unittest.TestCase):
    def test_gaps_block_clean_result_unless_explicitly_allowed(self):
        result = {"findings": [{"severity": "GAP"}]}
        self.assertFalse(preflight.is_clean(result))

    def test_warnings_block_clean_result(self):
        self.assertFalse(preflight.is_clean({"findings": [{"severity": "WARN"}]}))

    def test_json_scan_keeps_captured_stdout(self):
        from pathlib import Path
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "report.json"
            log = Path(directory) / "scan.log"
            code = preflight.run_json_scan(["/bin/sh", "-c", "printf '{\"ok\":true}'"], report, log)
            self.assertEqual(code, 0)
            self.assertEqual(report.read_text(), '{"ok":true}')

    def test_manifest_does_not_need_a_src_directory(self):
        from pathlib import Path
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "atak_plugin").mkdir()
            (root / "build.gradle").write_text("plugins {}")
            (root / "atak_plugin/AndroidManifest.xml").write_text("<manifest />")
            result = {"findings": []}
            preflight.inspect_source(root, result)
            self.assertEqual(result["source_manifest"], "atak_plugin/AndroidManifest.xml")
            self.assertNotIn("Android manifest missing", [f["title"] for f in result["findings"]])

    def test_sha256_reads_in_chunks(self):
        from pathlib import Path
        path = Path(self.id().replace(".", "-") + ".tmp")
        try:
            path.write_bytes(b"atak-plugin-preflight")
            self.assertEqual(
                preflight.sha256(path),
                "9f578df7e03b0a97b869cff2af320191fa559145b82bfc0a91afda34fed8b334",
            )
        finally:
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
