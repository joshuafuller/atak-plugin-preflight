import unittest

import preflight


class PreflightTests(unittest.TestCase):
    def test_gaps_block_clean_result_unless_explicitly_allowed(self):
        result = {"findings": [{"severity": "GAP"}]}
        self.assertFalse(preflight.is_clean(result))
        self.assertTrue(preflight.is_clean(result, allow_gaps=True))

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
