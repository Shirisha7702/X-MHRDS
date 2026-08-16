import os
import sys

# Ensure current folder is on sys.path to enable relative package imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from literature_review import backend

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_root = os.path.dirname(base_dir)
    
    docx_output = os.path.join(base_dir, "literature_review.docx")
    zip_output = os.path.join(workspace_root, "literature_review.zip")
    
    # Generate the formatted Word document using modular backend
    backend.create_docx(docx_output)
    
    # Compile the final ZIP package using modular backend
    backend.make_zip(workspace_root, zip_output)

if __name__ == "__main__":
    main()
