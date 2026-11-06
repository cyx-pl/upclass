"""The owner admin is reachable, but its content requires authentication."""

from django.test import TestCase
from django.urls import reverse


class AdminRoutesTest(TestCase):
    def test_admin_index_requires_login(self):
        response = self.client.get("/admin/")
        self.assertRedirects(response, reverse("admin:login") + "?next=/admin/")

    def test_admin_login_renders_protected_form(self):
        response = self.client.get("/admin/login/")
        self.assertContains(response, "Administracja upclass")
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        self.assertContains(response, 'type="password"')
