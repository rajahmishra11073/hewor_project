
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
import io
import os
from reportlab.pdfgen import canvas

class ToolsVerificationTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create a dummy PDF file for testing
        self.pdf_buffer = io.BytesIO()
        c = canvas.Canvas(self.pdf_buffer)
        c.drawString(100, 750, "Test Page 1")
        c.showPage()
        c.drawString(100, 750, "Test Page 2")
        c.showPage()
        c.drawString(100, 750, "Test Page 3")
        c.save()
        self.pdf_buffer.seek(0)
        self.pdf_content = self.pdf_buffer.read()
        
        # Create dummy HTML file
        self.html_content = b"<html><body><h1>Test HTML</h1></body></html>"

    def get_pdf_file(self, name='test.pdf'):
        """Helper to get a fresh file object for each request"""
        return SimpleUploadedFile(name, self.pdf_content, content_type='application/pdf')

    def get_html_file(self, name='test.html'):
        return SimpleUploadedFile(name, self.html_content, content_type='text/html')

    def test_01_html_to_pdf_file(self):
        print("\nTesting HTML to PDF (File)...")
        html_file = self.get_html_file()
        response = self.client.post(reverse('html_to_pdf_tool'), {
            'conversion_type': 'file',
            'html_files': html_file
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        print("PASS: HTML File converted to PDF")

    def test_02_rotate_pdf(self):
        print("\nTesting Rotate PDF...")
        pdf_file = self.get_pdf_file()
        response = self.client.post(reverse('rotate_pdf_tool'), {
            'pdf_files': pdf_file,
            'rotation': '90'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('_rotated_90', response['Content-Disposition'])
        print("PASS: PDF Rotated")

    def test_03_add_watermark(self):
        print("\nTesting Add Watermark...")
        pdf_file = self.get_pdf_file()
        response = self.client.post(reverse('add_watermark_tool'), {
            'pdf_files': pdf_file,
            'watermark_text': 'TEST WATERMARK'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('_watermarked', response['Content-Disposition'])
        print("PASS: Watermark Added")

    def test_04_protect_pdf(self):
        print("\nTesting Protect PDF...")
        pdf_file = self.get_pdf_file()
        response = self.client.post(reverse('protect_pdf_tool'), {
            'pdf_files': pdf_file,
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('_protected', response['Content-Disposition'])
        print("PASS: PDF Protected")
        
        # Save for unlock test? 
        # Actually easier to let unlock test create its own or mock it.
        # But we need a valid encrypted PDF for unlock test to really be robust.
        # Let's trust pikepdf to work if protect worked.
        # For unlock test, we will create an encrypted PDF in the test.

    def test_05_unlock_pdf(self):
        print("\nTesting Unlock PDF...")
        # Create encrypted PDF using pikepdf
        import pikepdf
        
        input_stream = io.BytesIO(self.pdf_content)
        output_stream = io.BytesIO()
        
        with pikepdf.Pdf.open(input_stream) as pdf:
            pdf.save(output_stream, encryption=pikepdf.Encryption(owner='pass', user='pass', R=6))
        
        output_stream.seek(0)
        encrypted_pdf = SimpleUploadedFile('encrypted.pdf', output_stream.read(), content_type='application/pdf')
        
        response = self.client.post(reverse('unlock_pdf_tool'), {
            'pdf_files': encrypted_pdf,
            'password': 'pass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('_unlocked', response['Content-Disposition'])
        print("PASS: PDF Unlocked")

    def test_06_add_page_numbers(self):
        print("\nTesting Add Page Numbers...")
        pdf_file = self.get_pdf_file()
        response = self.client.post(reverse('add_page_numbers_tool'), {
            'pdf_files': pdf_file
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('_numbered', response['Content-Disposition'])
        print("PASS: Page Numbers Added")

    def test_07_remove_pages(self):
        print("\nTesting Remove Pages...")
        pdf_file = self.get_pdf_file()
        # PDF has 3 pages. Remove page 2.
        response = self.client.post(reverse('remove_pages_tool'), {
            'pdf_files': pdf_file,
            'pages_to_remove': '2'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('_removed', response['Content-Disposition'])
        print("PASS: Pages Removed")

    def test_08_extract_pages(self):
        print("\nTesting Extract Pages...")
        pdf_file = self.get_pdf_file()
        # PDF has 3 pages. Extract page 1 and 3.
        response = self.client.post(reverse('extract_pages_tool'), {
            'pdf_files': pdf_file,
            'pages_to_extract': '1, 3'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('_extracted', response['Content-Disposition'])
        print("PASS: Pages Extracted")
