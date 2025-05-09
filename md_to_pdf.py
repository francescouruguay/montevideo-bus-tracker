from fpdf import FPDF
import re

class MarkdownToPDF:
    def __init__(self, margin=10, font_size_normal=11, font_size_h1=24, font_size_h2=18, font_size_h3=15, font_size_h4=12):
        self.pdf = FPDF()
        self.pdf.set_margins(margin, margin, margin)
        self.pdf.set_auto_page_break(True, margin)
        self.pdf.add_page()
        
        # Configure fonts
        self.pdf.add_font('DejaVu', '', 'Helvetica', uni=True)
        self.pdf.add_font('DejaVu', 'B', 'Helvetica-Bold', uni=True)
        self.pdf.add_font('DejaVu', 'I', 'Helvetica-Oblique', uni=True)
        
        # Font sizes
        self.font_size_normal = font_size_normal
        self.font_size_h1 = font_size_h1
        self.font_size_h2 = font_size_h2
        self.font_size_h3 = font_size_h3
        self.font_size_h4 = font_size_h4
        
        # Set default font
        self.pdf.set_font('DejaVu', '', self.font_size_normal)

    def parse_and_convert(self, md_file, pdf_file):
        # Read markdown content
        with open(md_file, 'r', encoding='utf-8') as file:
            md_content = file.read()

        # Split content into lines for processing
        lines = md_content.split('\n')
        
        code_block = False
        list_level = 0
        
        for line in lines:
            # Handle code blocks
            if line.startswith('```'):
                code_block = not code_block
                continue
                
            if code_block:
                self.pdf.set_font('DejaVu', '', self.font_size_normal - 1)
                self.pdf.set_text_color(100, 100, 100)
                self.pdf.multi_cell(0, 5, line)
                self.pdf.set_font('DejaVu', '', self.font_size_normal)
                self.pdf.set_text_color(0, 0, 0)
                continue
            
            # Handle headers
            if line.startswith('# '):
                self.pdf.set_font('DejaVu', 'B', self.font_size_h1)
                self.pdf.multi_cell(0, 10, line[2:])
                self.pdf.ln(5)
                self.pdf.set_font('DejaVu', '', self.font_size_normal)
                continue
                
            if line.startswith('## '):
                self.pdf.set_font('DejaVu', 'B', self.font_size_h2)
                self.pdf.multi_cell(0, 8, line[3:])
                self.pdf.ln(4)
                self.pdf.set_font('DejaVu', '', self.font_size_normal)
                continue
                
            if line.startswith('### '):
                self.pdf.set_font('DejaVu', 'B', self.font_size_h3)
                self.pdf.multi_cell(0, 7, line[4:])
                self.pdf.ln(3)
                self.pdf.set_font('DejaVu', '', self.font_size_normal)
                continue
                
            if line.startswith('#### '):
                self.pdf.set_font('DejaVu', 'B', self.font_size_h4)
                self.pdf.multi_cell(0, 6, line[5:])
                self.pdf.ln(2)
                self.pdf.set_font('DejaVu', '', self.font_size_normal)
                continue
            
            # Handle lists
            if line.startswith('- ') or line.startswith('* '):
                self.pdf.set_x(self.pdf.get_x() + 5)
                self.pdf.multi_cell(0, 5, '• ' + line[2:])
                continue
                
            if re.match(r'^\d+\.\s', line):
                num, text = re.match(r'^(\d+\.\s)(.*)', line).groups()
                self.pdf.set_x(self.pdf.get_x() + 5)
                self.pdf.multi_cell(0, 5, num + text)
                continue
            
            # Handle normal text
            if line.strip() == '':
                self.pdf.ln(3)
            else:
                self.pdf.multi_cell(0, 5, line)

        # Save the PDF
        self.pdf.output(pdf_file)

if __name__ == '__main__':
    converter = MarkdownToPDF()
    converter.parse_and_convert('opensourcebusmaidan.md', 'opensourcebusmaidan.pdf')
    print("Convertido exitosamente a PDF.")