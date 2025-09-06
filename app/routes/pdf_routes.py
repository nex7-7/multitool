"""
PDF processing API routes.
Handles all PDF-related HTTP requests.
"""

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from typing import Dict, Any, Tuple, Optional, List, Union
from pathlib import Path
import os
import uuid
import json

from ..tools.pdf.processors import (
    PDFSplitter, PDFMerger, PDFRearranger, ConvertToPDF, PDFTextExtractor
)
from ..utils.base import FileValidator
from ..config import Config

pdf_bp = Blueprint('pdf', __name__)


def _validate_pdf_file(file) -> Optional[str]:
    if not file or not file.filename:
        return "No file provided"
    if not FileValidator.is_allowed_extension(file.filename, Config.ALLOWED_PDF_EXTENSIONS):
        return f"Invalid file type. Allowed: {', '.join(Config.ALLOWED_PDF_EXTENSIONS)}"
    return None


def _save_uploaded_file(file, prefix: str) -> str:
    filename = secure_filename(file.filename)
    safe_filename = FileValidator.get_safe_filename(f"{prefix}_{uuid.uuid4()}_{filename}")
    filepath = current_app.config['UPLOAD_FOLDER'] / safe_filename
    file.save(filepath)
    return str(filepath)


def _generate_output_path(input_path: str, suffix: str = "processed", ext: Optional[str] = None) -> str:
    input_file = Path(input_path)
    ext_out = ext if ext else input_file.suffix
    output_filename = f"{input_file.stem}_{suffix}_{uuid.uuid4()}{ext_out}"
    return str(current_app.config['OUTPUT_FOLDER'] / output_filename)


@pdf_bp.route('/split', methods=['POST'])
def split_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        error = _validate_pdf_file(file)
        if error:
            return jsonify({'error': error}), 400

        pages = request.form.get('pages')  # optional ranges string

        input_path = _save_uploaded_file(file, 'pdf_split_input')
        output_path = _generate_output_path(input_path, 'split', ext='.pdf')

        splitter = PDFSplitter(input_path, output_path)
        result = splitter.process(pages=pages)

        os.remove(input_path)

        return (jsonify(result), 200) if result.get('success') else (jsonify(result), 500)
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@pdf_bp.route('/merge', methods=['POST'])
def merge_pdfs():
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400

        files = request.files.getlist('files')
        if not files or len(files) < 2:
            return jsonify({'error': 'At least two PDF files are required'}), 400

        # Optional order as JSON array of indices (0-based mapping to provided files)
        order_str = request.form.get('order')
        if order_str:
            try:
                order = json.loads(order_str)
                if not isinstance(order, list) or any(not isinstance(i, int) for i in order):
                    return jsonify({'error': 'order must be an array of integers'}), 400
            except json.JSONDecodeError:
                return jsonify({'error': 'Invalid order JSON'}), 400
        else:
            order = list(range(len(files)))

        input_paths: List[str] = []
        for idx in order:
            if idx < 0 or idx >= len(files):
                return jsonify({'error': f'order index out of range: {idx}'}), 400
            f = files[idx]
            err = _validate_pdf_file(f)
            if err:
                return jsonify({'error': err}), 400
            input_paths.append(_save_uploaded_file(f, 'pdf_merge_input'))

        output_path = _generate_output_path(input_paths[0], 'merged', ext='.pdf')
        merger = PDFMerger(input_paths, output_path)
        result = merger.process()

        for p in input_paths:
            os.remove(p)

        return (jsonify(result), 200) if result.get('success') else (jsonify(result), 500)
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@pdf_bp.route('/rearrange', methods=['POST'])
def rearrange_pages():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        file = request.files['file']
        err = _validate_pdf_file(file)
        if err:
            return jsonify({'error': err}), 400

        order_str = request.form.get('page_order')
        if not order_str:
            return jsonify({'error': 'page_order is required'}), 400
        try:
            page_order = json.loads(order_str)
            if not isinstance(page_order, list) or any(not isinstance(i, int) for i in page_order):
                return jsonify({'error': 'page_order must be an array of 1-based integers'}), 400
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid page_order JSON'}), 400

        input_path = _save_uploaded_file(file, 'pdf_rearrange_input')
        output_path = _generate_output_path(input_path, 'rearranged', ext='.pdf')

        rearranger = PDFRearranger(input_path, output_path)
        result = rearranger.process(page_order=page_order)

        os.remove(input_path)
        return (jsonify(result), 200) if result.get('success') else (jsonify(result), 500)
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@pdf_bp.route('/convert-to-pdf', methods=['POST'])
def convert_to_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        file = request.files['file']
        # Accept images and PDFs; ConvertToPDF will validate
        if not file.filename:
            return jsonify({'error': 'No file provided'}), 400

        input_path = _save_uploaded_file(file, 'convert_to_pdf_input')
        # Force .pdf extension regardless of source
        output_path = _generate_output_path(input_path, 'converted', ext='.pdf')

        converter = ConvertToPDF(input_path, output_path)
        result = converter.process()

        os.remove(input_path)
        return (jsonify(result), 200) if result.get('success') else (jsonify(result), 500)
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@pdf_bp.route('/extract-text', methods=['POST'])
def extract_text():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        file = request.files['file']
        err = _validate_pdf_file(file)
        if err:
            return jsonify({'error': err}), 400

        pages = request.form.get('pages')
        input_path = _save_uploaded_file(file, 'pdf_text_input')

        extractor = PDFTextExtractor(input_path)
        result = extractor.process(pages=pages)

        os.remove(input_path)
        return (jsonify(result), 200) if result.get('success') else (jsonify(result), 500)
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500
