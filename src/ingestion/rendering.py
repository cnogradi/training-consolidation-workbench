import os
import platform
from typing import List
from PIL import Image
from pdf2image import convert_from_path
from pdf2image.exceptions import PDFInfoNotInstalledError

def render_pdf_pages(file_path: str) -> List[Image.Image]:
    """
    Render each page of a PDF to a PIL Image.
    Requires poppler to be installed on the system.
    """
    try:
        images = convert_from_path(file_path)
        return images
    except PDFInfoNotInstalledError:
        system = platform.system()
        msg = (
            "Unable to find 'pdftoppm' or 'pdftocairo'. Is poppler installed?\n"
        )
        if system == "Windows":
            msg += (
                "On Windows: Download the latest binary from https://github.com/oschwartz10612/poppler-windows/releases/,\n"
                "extract it, and add the 'bin' folder to your PATH environment variable."
            )
        elif system == "Linux":
            msg += "On Linux: Run `sudo apt-get install poppler-utils` (Debian/Ubuntu) or equivalent."
        elif system == "Darwin":
            msg += "On macOS: Run `brew install poppler`."
        
        raise RuntimeError(msg)
    except Exception as e:
        print(f"Error rendering PDF {file_path}: {e}")
        # Fallback or re-raise depending on strictness
        raise

def render_pptx_slides(file_path: str) -> List[Image.Image]:
    """
    Render each slide of a PPTX to a PIL Image.
    Currently a placeholder as pure Python PPTX rendering is complex.
    Future implementation could use LibreOffice or COM automation on Windows.
    """
    print(f"Warning: PPTX rendering to images is not yet implemented for {file_path}")
    return []
