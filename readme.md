# PDF Text Extractor

This project is a simple text extractor that reads a PDF file and returns all the text content.

## Requirements

- Python 3.x
- `PyPDF2` library

## Installation

First, ensure you have Python 3 installed. Then, install the required library using pip:

```sh
pip install PyPDF2
```

## Usage

To use the text extractor, create a Python script with the following content:

```python
import PyPDF2

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfFileReader(file)
        text = ''
        for page_num in range(reader.numPages):
            page = reader.getPage(page_num)
            text += page.extract_text()
        return text

if __name__ == "__main__":
    pdf_path = 'path/to/your/pdf/file.pdf'
    text = extract_text_from_pdf(pdf_path)
    print(text)
```

Replace `'path/to/your/pdf/file.pdf'` with the path to your PDF file.

## License

This project is licensed under the MIT License.