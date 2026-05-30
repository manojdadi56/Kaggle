import json
import glob
import unittest

class TestKernelMetadata(unittest.TestCase):
    def test_metadata_no_placeholders_and_valid_sources(self):
        files = glob.glob("competitions/nvidia-nemotron-model-reasoning-challenge/kernels/**/kernel-metadata.json", recursive=True)
        self.assertTrue(len(files) > 0, "No kernel-metadata.json found.")
        for file in files:
            with open(file, 'r') as f:
                content = f.read()

            self.assertNotIn("TODO", content)
            self.assertNotIn("REPLACE", content)
            self.assertNotIn("placeholder", content)

            data = json.loads(content)
            self.assertNotIn("dataset_sources", data)
            self.assertIn("competition_sources", data)
            self.assertIn("nvidia-nemotron-model-reasoning-challenge", data["competition_sources"])
            self.assertIn("model_sources", data)

if __name__ == '__main__':
    unittest.main()
