"""Polish navigation, catalog integrity, plurals and standalone pages."""

import gettext
import re
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.models import User
from django.template import engines
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils.translation import ngettext, override


class PolishCatalogTest(SimpleTestCase):
    def test_plural_forms_and_placeholders(self):
        with override("pl"):
            for count, expected in [(1, "1 lekcja"), (2, "2 lekcje"), (5, "5 lekcji"), (12, "12 lekcji"), (22, "22 lekcje")]:
                translated = ngettext("(%(counter)s lesson)", "(%(counter)s lessons)", count) % {"counter": count}
                self.assertEqual(translated, f"({expected})")
        with (settings.BASE_DIR / "locale/pl/LC_MESSAGES/django.mo").open("rb") as source:
            catalog = gettext.GNUTranslations(source)
        self.assertGreater(len(catalog._catalog), 2500)
        for key, value in catalog._catalog.items():
            if not key or isinstance(key, str) and not key.strip():
                continue
            msgid = key[0] if isinstance(key, tuple) else key
            # Some singular sources intentionally omit the counter in plural forms.
            placeholders = set(re.findall(r"\{[\w.]+\}", msgid))
            self.assertEqual(placeholders, set(re.findall(r"\{[\w.]+\}", value)), msgid)
            self.assertTrue(value.strip(), msgid)

    def test_all_templates_compile(self):
        engine = engines["django"]
        for path in Path(settings.BASE_DIR).rglob("*.html"):
            if "templates" in path.parts:
                with self.subTest(template=str(path)):
                    engine.from_string(path.read_text())


class PolishPagesTest(TestCase):
    def test_public_pages_and_language_cookie(self):
        for view in ["core:login", "portal:login", "portal:password_reset"]:
            with self.subTest(view=view):
                response = self.client.get(reverse(view), HTTP_ACCEPT_LANGUAGE="pl")
                self.assertContains(response, 'lang="pl"')
                self.assertNotContains(response, "Zum Tutor-Login")
        self.client.post(reverse("set_language"), {"language": "pl", "next": reverse("core:login")})
        response = self.client.get(reverse("core:login"), HTTP_ACCEPT_LANGUAGE="de")
        self.assertContains(response, "Nazwa użytkownika")

    def test_authenticated_navigation(self):
        user = User.objects.create_user(username="polish-navigation")
        self.client.force_login(user)
        response = self.client.get(reverse("core:dashboard"), HTTP_ACCEPT_LANGUAGE="pl")
        for label in ["Pulpit", "Uczniowie", "Kalendarz", "Faktury"]:
            self.assertContains(response, label)

    def test_polish_legal_pages_do_not_fetch_german_html(self):
        with patch("apps.core.erecht24_service.get_imprint") as imprint, patch("apps.core.erecht24_service.get_privacy_policy") as privacy:
            for view in ["legal_imprint", "legal_privacy", "legal_terms", "legal_withdrawal", "legal_avv"]:
                response = self.client.get(reverse("core:" + view), HTTP_ACCEPT_LANGUAGE="pl")
                self.assertEqual(response.status_code, 200)
            imprint.assert_not_called()
            privacy.assert_not_called()
