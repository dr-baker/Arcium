"""Product copy and translation fingerprints must use the same brand."""

import unittest
from unittest.mock import patch

import i18n_apply
import name_substitution
import name_substitution_utils as namesub


class ArciumBrandingTest(unittest.TestCase):
    def test_product_copy_and_attribution(self):
        name_substitution.replacement_sanity()
        for source, expected in (
            ("Meet Helium", "Meet Arcium"),
            ("Helium's settings", "Arcium's settings"),
            ("The Helium Authors", "The Helium Authors"),
            ("supports upstream Helium development", "supports upstream Helium development"),
            ("https://helium.computer/", "https://helium.computer/"),
            ("IDS_HELIUM_ONBOARDING_TITLE", "IDS_HELIUM_ONBOARDING_TITLE"),
            ("Chrome Web Store", "Chrome Web Store"),
        ):
            with self.subTest(source=source):
                self.assertEqual(expected, namesub.replace_text(source)[0])

    def test_translation_id_uses_displayed_english(self):
        with patch.object(namesub, "compute_fp", side_effect=lambda msg: msg.text):
            self.assertEqual("Meet Arcium", i18n_apply.get_id(
                "IDS_WELCOME", "Greeting", "Meet Helium", ""))

    def test_upstream_link_label_keeps_its_fingerprint(self):
        text = 'Built from <ph name="BEGIN_LINK_CHROMIUM">$1</ph>Chromium'
        with patch.object(namesub, "compute_fp", side_effect=lambda msg: msg.find("ph").tail):
            self.assertEqual("Chromium", i18n_apply.get_id("IDS_CREDIT", "Credit", text, ""))

    def test_translated_copy_matches_new_fingerprint(self):
        source = {"name": "IDS_WELCOME", "message": "Meet Helium", "context": "Greeting"}
        translations = {("IDS_WELCOME", "Meet Helium"): {"message": "Bienvenue dans Helium"}}
        with patch.object(namesub, "compute_fp", side_effect=lambda msg: msg.text), \
                patch.object(i18n_apply, "insert_into_xtb") as insert:
            self.assertEqual(1, i18n_apply.merge_into_xtb("unused.xtb", [source], translations))
            insert.assert_called_once_with("unused.xtb", [("Meet Arcium", "Bienvenue dans Arcium")])


if __name__ == "__main__":
    unittest.main()
