"""
Converts .docx files to .pdf using a real, locally-installed Microsoft Word via COM
automation (Windows only) -- this gives the highest-fidelity conversion, since Word's own
rendering/print engine produces the PDF, correctly resolving the Table-of-Contents field,
internal bookmark hyperlinks, and table styling exactly as Word itself displays them.

Usage: python scripts/docx_to_pdf.py <input1.docx> [<input2.docx> ...]
Writes each <name>.pdf next to its source .docx.
"""
import os
import sys

import win32com.client as win32

WD_FORMAT_PDF = 17


def convert(docx_path):
    docx_path = os.path.abspath(docx_path)
    pdf_path = os.path.splitext(docx_path)[0] + ".pdf"

    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        doc = word.Documents.Open(docx_path)
        try:
            # Resolve the TOC field to real page numbers/entries before export, and
            # refresh any other fields (e.g. PAGE numbers in the footer) too.
            doc.Fields.Update()
            doc.SaveAs2(pdf_path, FileFormat=WD_FORMAT_PDF)
            print(f"Wrote {pdf_path}")
        finally:
            doc.Close(SaveChanges=False)
    finally:
        word.Quit()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python docx_to_pdf.py <input1.docx> [<input2.docx> ...]")
        sys.exit(1)
    for path in sys.argv[1:]:
        convert(path)
