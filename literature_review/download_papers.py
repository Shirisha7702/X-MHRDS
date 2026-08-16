import os
import sys
import time

# Ensure current folder is on sys.path to enable relative package imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from literature_review.metadata import PAPERS_METADATA
from literature_review import backend

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    papers_dir = os.path.join(base_dir, "papers")
    
    if not os.path.exists(papers_dir):
        os.makedirs(papers_dir)
        print(f"Created directory: {papers_dir}")
        
    print(f"Starting modular downloader for {len(PAPERS_METADATA)} papers...")
    
    for i, paper in enumerate(PAPERS_METADATA, 1):
        print(f"\n[{i}/{len(PAPERS_METADATA)}] Processing paper: {paper['title']}")
        filename = f"{paper['id']}.pdf"
        output_path = os.path.join(papers_dir, filename)
        
        pdf_url = paper.get("pdf_url")
        if not pdf_url:
            # Query arXiv preprint as a fallback
            pdf_url = backend.search_arxiv_by_title(paper["title"])
            
        success = False
        if pdf_url:
            success = backend.download_pdf(pdf_url, output_path)
            
        if not success:
            # Fall back to metadata placeholder
            backend.write_placeholder(paper, papers_dir)
            
        time.sleep(1.0)

    print("\nProcessing complete. All PDFs and placeholders generated.")

if __name__ == "__main__":
    main()
