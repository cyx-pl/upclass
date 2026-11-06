"""
Tests for CanonicalDomainMiddleware: 301 redirect for www and Railway hosts.
"""

from django.test import RequestFactory, TestCase, override_settings

from apps.core.middleware import CanonicalDomainMiddleware


def _make_middleware(status=200):
    def get_response(request):
        from django.http import HttpResponse

        return HttpResponse(status=status)

    return CanonicalDomainMiddleware(get_response)


@override_settings(SITE_URL="https://preceptly.de")
class CanonicalDomainMiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(DEBUG=False)
    def test_www_redirects_to_canonical(self):
        request = self.factory.get("/", HTTP_HOST="www.preceptly.de")
        response = _make_middleware()(request)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "https://preceptly.de/")

    @override_settings(DEBUG=False)
    def test_railway_subdomain_redirects_with_path_and_query(self):
        request = self.factory.get("/dashboard/?foo=bar", HTTP_HOST="preceptly.up.railway.app")
        response = _make_middleware()(request)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "https://preceptly.de/dashboard/?foo=bar")

    @override_settings(DEBUG=False)
    def test_canonical_host_no_redirect(self):
        request = self.factory.get("/dashboard/", HTTP_HOST="preceptly.de")
        response = _make_middleware()(request)
        self.assertEqual(response.status_code, 200)

    @override_settings(DEBUG=False)
    def test_localhost_no_redirect(self):
        request = self.factory.get("/", HTTP_HOST="localhost:8000")
        response = _make_middleware()(request)
        self.assertEqual(response.status_code, 200)

    @override_settings(DEBUG=False)
    def test_testserver_no_redirect(self):
        request = self.factory.get("/", HTTP_HOST="testserver")
        response = _make_middleware()(request)
        self.assertEqual(response.status_code, 200)

    @override_settings(DEBUG=True)
    def test_debug_mode_skips_redirect(self):
        request = self.factory.get("/", HTTP_HOST="www.preceptly.de")
        response = _make_middleware()(request)
        self.assertEqual(response.status_code, 200)

    @override_settings(DEBUG=False, SITE_URL="https://upclass-production.up.railway.app")
    def test_configured_railway_host_does_not_redirect(self):
        request = self.factory.get("/login/", HTTP_HOST="upclass-production.up.railway.app")
        response = _make_middleware()(request)
        self.assertEqual(response.status_code, 200)

    @override_settings(DEBUG=False, SITE_URL="https://app.upclass.pl/")
    def test_railway_alias_redirects_to_configured_site(self):
        request = self.factory.get("/login/?next=/dashboard/", HTTP_HOST="upclass.up.railway.app")
        response = _make_middleware()(request)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "https://app.upclass.pl/login/?next=/dashboard/")
