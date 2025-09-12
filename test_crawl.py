import unittest
from crawl import *


class TestCrawl(unittest.TestCase):
    def test_normalize_url(self):
        input_url = "https://blog.boot.dev/path"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev/path"
        self.assertEqual(actual, expected)

    def test_normalize_url2(self):
        # Test URL with no path
        input_url = "https://blog.boot.dev"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev"
        self.assertEqual(actual, expected)

    def test_normalize_url3(self):
        # Test URL with query parameters
        input_url = "https://blog.boot.dev/path?key=value"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev/path"
        self.assertEqual(actual, expected)

    def test_normalize_url4(self):
        # Test URL with fragment
        input_url = "https://blog.boot.dev/path#section"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev/path"
        self.assertEqual(actual, expected)

    def test_normalize_url5(self):
        # Test URL with port number
        input_url = "https://blog.boot.dev:8000/path"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev/path"
        self.assertEqual(actual, expected)

    def test_get_h1_from_html_basic(self):
        input_body = '<html><body><h1>Test Title</h1></body></html>'
        actual = get_h1_from_html(input_body)
        expected = "Test Title"
        self.assertEqual(actual, expected)

    def test_get_h1_from_html_multiple(self):
        input_body = '<html><body><h1>First Title</h1><h1>Second Title</h1></body></html>'
        actual = get_h1_from_html(input_body)
        expected = "First Title"
        self.assertEqual(actual, expected)

    def test_get_h1_from_html_nested(self):
        input_body = '<html><body><h1>Title <span>with nested</span> elements</h1></body></html>'
        actual = get_h1_from_html(input_body)
        expected = "Title with nested elements"
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_main_priority(self):
        input_body = '''<html><body>
            <p>Outside paragraph.</p>
            <main>
                <p>Main paragraph.</p>
            </main>
        </body></html>'''
        actual = get_first_paragraph_from_html(input_body)
        expected = "Main paragraph."
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_no_main(self):
        input_body = '<html><body><p>Only paragraph</p></body></html>'
        actual = get_first_paragraph_from_html(input_body)
        expected = "Only paragraph"
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_nested_main(self):
        input_body = '''<html><body>
            <main>
                <div><p>Nested paragraph</p></div>
                <p>Second paragraph</p>
            </main>
        </body></html>'''
        actual = get_first_paragraph_from_html(input_body)
        expected = "Nested paragraph"
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_absolute(self):
        input_url = "https://blog.boot.dev"
        input_body = '<html><body><a href="https://blog.boot.dev"><span>Boot.dev</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://blog.boot.dev"]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_relative(self):
        input_url = "https://blog.boot.dev"
        input_body = '<html><body><a href="/path"><span>Path</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://blog.boot.dev/path"]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_mixed(self):
        input_url = "https://blog.boot.dev"
        input_body = '''<html><body>
            <a href="/path1">Path1</a>
            <a href="https://example.com">External</a>
            <a href="/path2">Path2</a>
        </body></html>'''
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://blog.boot.dev/path1", "https://example.com", "https://blog.boot.dev/path2"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_relative(self):
        input_url = "https://blog.boot.dev"
        input_body = '<html><body><img src="/logo.png" alt="Logo"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://blog.boot.dev/logo.png"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_absolute(self):
        input_url = "https://blog.boot.dev"
        input_body = '<html><body><img src="https://example.com/image.jpg" alt="External"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = []
        self.assertEqual(actual, expected)

    def test_get_images_from_html_mixed(self):
        input_url = "https://blog.boot.dev"
        input_body = '''<html><body>
            <img src="/local1.jpg" alt="Local1">
            <img src="https://example.com/external.jpg" alt="External">
            <img src="/local2.jpg" alt="Local2">
        </body></html>'''
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://blog.boot.dev/local1.jpg", "https://blog.boot.dev/local2.jpg"]
        self.assertEqual(actual, expected)

    def test_extract_page_data_basic(self):
        input_url = "https://blog.boot.dev"
        input_body = '''<html><body>
            <h1>Test Title</h1>
            <p>This is the first paragraph.</p>
            <a href="/link1">Link 1</a>
            <img src="/image1.jpg" alt="Image 1">
        </body></html>'''
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url"            : "https://blog.boot.dev",
            "h1"             : "Test Title",
            "first_paragraph": "This is the first paragraph.",
            "outgoing_links" : ["https://blog.boot.dev/link1"],
            "image_urls"     : ["https://blog.boot.dev/image1.jpg"]
        }
        self.assertEqual(actual, expected)

if __name__ == "__main__":
    unittest.main()
