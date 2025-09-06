/**
 * PDF tools JavaScript
 * Handles PDF-specific functionality and tool interfaces
 */

/**
 * Load PDF tool content into modal
 * @param {string} tool - Tool identifier
 */
function loadPdfToolContent(tool) {
    const content = getPdfToolHTML(tool);
    DOM.modalBody.innerHTML = content;
    setupPdfToolEvents(tool);
}

/**
 * Get HTML content for PDF tools
 * @param {string} tool - Tool identifier
 * @returns {string} HTML content
 */
function getPdfToolHTML(tool) {
    const singlePdfUpload = `
        <div class="form-group">
            <label class="form-label">Select PDF</label>
            <div class="file-upload" id="pdf-file-upload">
                <i class="fas fa-cloud-upload-alt"></i>
                <p>Click to select a PDF or drag and drop</p>
                <input type="file" id="pdf-file" accept="application/pdf" style="display: none;">
            </div>
            <div id="pdf-file-info" class="file-info" style="display: none;"></div>
        </div>
    `;

    const multiPdfUpload = `
        <div class="form-group">
            <label class="form-label">Select PDFs (in desired order)</label>
            <div class="file-upload" id="pdf-files-upload">
                <i class="fas fa-cloud-upload-alt"></i>
                <p>Click to select PDFs or drag and drop</p>
                <input type="file" id="pdf-files" accept="application/pdf" multiple style="display: none;">
            </div>
            <div id="pdf-files-info" class="file-info" style="display: none;"></div>
        </div>
    `;

    switch (tool) {
        case 'split':
            return `
                ${singlePdfUpload}
                <div class="form-group">
                    <label class="form-label">Pages (optional)</label>
                    <input type="text" id="split-pages" class="form-input" placeholder="e.g., 1-3,5,7-">
                    <small>Leave empty to split into individual pages. Use ranges like 1-3,5,7- for custom selection.</small>
                </div>
                <div id="split-results" class="form-group" style="display:none;"></div>
                <div class="form-group">
                    <button type="button" id="pdf-process-btn" class="btn btn-primary" disabled>
                        <i class="fas fa-scissors"></i> Split PDF
                    </button>
                </div>
            `;

        case 'merge':
            return `
                ${multiPdfUpload}
                <div class="form-group">
                    <small>Files will be merged in the order selected. To change order, reselect files in the desired sequence.</small>
                </div>
                <div id="merge-result" class="form-group" style="display:none;"></div>
                <div class="form-group">
                    <button type="button" id="pdf-process-btn" class="btn btn-primary" disabled>
                        <i class="fas fa-layer-group"></i> Merge PDFs
                    </button>
                </div>
            `;

        case 'rearrange':
            return `
                ${singlePdfUpload}
                <div class="form-group">
                    <label class="form-label">New Page Order</label>
                    <input type="text" id="page-order" class="form-input" placeholder="e.g., 2,1,3 (1-based indices)">
                    <small>Provide a full permutation of pages using 1-based indices.</small>
                </div>
                <div id="rearrange-result" class="form-group" style="display:none;"></div>
                <div class="form-group">
                    <button type="button" id="pdf-process-btn" class="btn btn-primary" disabled>
                        <i class="fas fa-sort"></i> Rearrange Pages
                    </button>
                </div>
            `;

        case 'extract-text':
            return `
                ${singlePdfUpload}
                <div class="form-group">
                    <label class="form-label">Pages (optional)</label>
                    <input type="text" id="text-pages" class="form-input" placeholder="e.g., 1-2,5">
                </div>
                <div class="form-group" id="text-output" style="display:none;">
                    <label class="form-label">Extracted Text</label>
                    <textarea id="extracted-text" class="form-input" rows="10" readonly></textarea>
                    <div style="margin-top: .5rem; display:flex; gap:.5rem;">
                        <button type="button" id="copy-text-btn" class="btn btn-secondary"><i class="fas fa-copy"></i> Copy</button>
                        <button type="button" id="download-text-btn" class="btn btn-success"><i class="fas fa-download"></i> Download .txt</button>
                    </div>
                </div>
                <div class="form-group">
                    <button type="button" id="pdf-process-btn" class="btn btn-primary" disabled>
                        <i class="fas fa-file-export"></i> Extract Text
                    </button>
                </div>
            `;

        case 'convert-to-pdf':
            return `
                <div class="form-group">
                    <label class="form-label">Select File (image or PDF)</label>
                    <div class="file-upload" id="convert-file-upload">
                        <i class="fas fa-cloud-upload-alt"></i>
                        <p>Click to select a file or drag and drop</p>
                        <input type="file" id="convert-file" accept="application/pdf,image/*" style="display: none;">
                    </div>
                    <div id="convert-file-info" class="file-info" style="display: none;"></div>
                </div>
                <div id="convert-result" class="form-group" style="display:none;"></div>
                <div class="form-group">
                    <button type="button" id="pdf-process-btn" class="btn btn-primary" disabled>
                        <i class="fas fa-file-arrow-down"></i> Convert to PDF
                    </button>
                </div>
            `;

        default:
            return '<p>PDF tool not implemented yet.</p>';
    }
}

/**
 * Setup event listeners for PDF tools
 * @param {string} tool - Tool identifier
 */
function setupPdfToolEvents(tool) {
    switch (tool) {
        case 'split':
            setupSinglePdfUpload('pdf-file-upload', 'pdf-file', 'pdf-file-info');
            document.getElementById('pdf-process-btn').addEventListener('click', processSplitPdf);
            break;
        case 'merge':
            setupMultiPdfUpload('pdf-files-upload', 'pdf-files', 'pdf-files-info');
            document.getElementById('pdf-process-btn').addEventListener('click', processMergePdfs);
            break;
        case 'rearrange':
            setupSinglePdfUpload('pdf-file-upload', 'pdf-file', 'pdf-file-info');
            document.getElementById('pdf-process-btn').addEventListener('click', processRearrangePdf);
            break;
        case 'extract-text':
            setupSinglePdfUpload('pdf-file-upload', 'pdf-file', 'pdf-file-info');
            document.getElementById('pdf-process-btn').addEventListener('click', processExtractText);
            break;
        case 'convert-to-pdf':
            setupGenericUpload('convert-file-upload', 'convert-file', 'convert-file-info', ['application/pdf', 'image/']);
            document.getElementById('pdf-process-btn').addEventListener('click', processConvertToPdf);
            break;
    }
}

function setupSinglePdfUpload(wrapperId, inputId, infoId) {
    setupGenericUpload(wrapperId, inputId, infoId, ['application/pdf']);
}

function setupMultiPdfUpload(wrapperId, inputId, infoId) {
    const upload = document.getElementById(wrapperId);
    const input = document.getElementById(inputId);
    const info = document.getElementById(infoId);
    const processBtn = document.getElementById('pdf-process-btn');

    upload.addEventListener('click', () => input.click());
    upload.addEventListener('dragover', (e) => { e.preventDefault(); upload.classList.add('dragover'); });
    upload.addEventListener('dragleave', () => upload.classList.remove('dragover'));
    upload.addEventListener('drop', (e) => {
        e.preventDefault();
        upload.classList.remove('dragover');
        const files = Array.from(e.dataTransfer.files).filter(f => f.type.includes('pdf') || f.name.toLowerCase().endsWith('.pdf'));
        input.files = createFileList(files);
        handleFiles(files);
    });
    input.addEventListener('change', () => handleFiles(Array.from(input.files)));

    function handleFiles(files) {
        if (!files || files.length < 2) {
            showAlert('Select at least two PDF files.', 'warning', 3000);
            info.style.display = 'none';
            if (processBtn) processBtn.disabled = true;
            return;
        }
        const list = files.map(f => `${f.name} (${formatFileSize(f.size)})`).join('<br>');
        info.innerHTML = list;
        info.style.display = 'block';
        if (processBtn) processBtn.disabled = false;
    }
}

function setupGenericUpload(wrapperId, inputId, infoId, allowedTypes) {
    const upload = document.getElementById(wrapperId);
    const input = document.getElementById(inputId);
    const info = document.getElementById(infoId);
    const processBtn = document.getElementById('pdf-process-btn');

    upload.addEventListener('click', () => input.click());
    upload.addEventListener('dragover', (e) => { e.preventDefault(); upload.classList.add('dragover'); });
    upload.addEventListener('dragleave', () => upload.classList.remove('dragover'));
    upload.addEventListener('drop', (e) => {
        e.preventDefault();
        upload.classList.remove('dragover');
        const file = e.dataTransfer.files[0];
        if (file) handleFile(file);
    });
    input.addEventListener('change', () => {
        if (input.files.length > 0) handleFile(input.files[0]);
    });

    function handleFile(file) {
        const ok = validateFileType(file, allowedTypes);
        if (!ok) {
            showAlert('Please select a valid file.', 'error');
            info.style.display = 'none';
            if (processBtn) processBtn.disabled = true;
            return;
        }
        info.innerHTML = `<strong>${file.name}</strong><br>Size: ${formatFileSize(file.size)}<br>Type: ${file.type || 'n/a'}`;
        info.style.display = 'block';
        if (processBtn) processBtn.disabled = false;
    }
}

// Helpers
function createFileList(files) {
    const dataTransfer = new DataTransfer();
    files.forEach(f => dataTransfer.items.add(f));
    return dataTransfer.files;
}

// Processors
async function processSplitPdf() {
    const input = document.getElementById('pdf-file');
    const file = input.files[0];
    const pages = document.getElementById('split-pages').value.trim();
    if (!file) return showAlert('Select a PDF.', 'error');

    try {
        showLoading('Splitting PDF...');
        const formData = new FormData();
        formData.append('file', file);
        if (pages) formData.append('pages', pages);

        const res = await fetch('/api/pdf/split', { method: 'POST', body: formData });
        const result = await res.json();
        if (!res.ok || !result.success) throw new Error(result.message || 'Split failed');

        const container = document.getElementById('split-results');
        container.style.display = 'block';
        const outputs = (result.metadata && result.metadata.outputs) || [];
        if (outputs.length === 0) {
            container.innerHTML = '<p>No output generated.</p>';
        } else {
            const links = outputs.map(o => `<li><a href="${o.output_url}" target="_blank">Download ${o.page ? 'Page ' + o.page : ('Pages ' + (o.pages || []).join(','))}</a></li>`).join('');
            container.innerHTML = `<ul>${links}</ul>`;
        }
        showAlert('PDF split successfully!', 'success');
    } catch (e) {
        console.error(e);
        showAlert(String(e.message || e), 'error');
    } finally {
        hideLoading();
    }
}

async function processMergePdfs() {
    const input = document.getElementById('pdf-files');
    const files = Array.from(input.files || []);
    if (files.length < 2) return showAlert('Select at least two PDFs.', 'error');

    try {
        showLoading('Merging PDFs...');
        const formData = new FormData();
        files.forEach(f => formData.append('files', f));
        // order defaults to selection order

        const res = await fetch('/api/pdf/merge', { method: 'POST', body: formData });
        const result = await res.json();
        if (!res.ok || !result.success) throw new Error(result.message || 'Merge failed');

        const container = document.getElementById('merge-result');
        container.style.display = 'block';
        const url = result.output_url || '';
        container.innerHTML = url ? `<a class="btn btn-success" href="${url}" target="_blank"><i class="fas fa-download"></i> Download Merged PDF</a>` : '<p>Merged, but no file URL.</p>';
        showAlert('PDFs merged successfully!', 'success');
    } catch (e) {
        console.error(e);
        showAlert(String(e.message || e), 'error');
    } finally {
        hideLoading();
    }
}

async function processRearrangePdf() {
    const input = document.getElementById('pdf-file');
    const file = input.files[0];
    const orderStr = document.getElementById('page-order').value.trim();
    if (!file) return showAlert('Select a PDF.', 'error');
    if (!orderStr) return showAlert('Enter new page order.', 'error');

    // Validate quick format like 1,3,2
    const order = orderStr.split(',').map(s => parseInt(s.trim(), 10)).filter(n => !isNaN(n));
    if (order.length === 0) return showAlert('Invalid page order.', 'error');

    try {
        showLoading('Rearranging pages...');
        const formData = new FormData();
        formData.append('file', file);
        formData.append('page_order', JSON.stringify(order));

        const res = await fetch('/api/pdf/rearrange', { method: 'POST', body: formData });
        const result = await res.json();
        if (!res.ok || !result.success) throw new Error(result.message || 'Rearrange failed');

        const container = document.getElementById('rearrange-result');
        container.style.display = 'block';
        const url = result.output_url || '';
        container.innerHTML = url ? `<a class="btn btn-success" href="${url}" target="_blank"><i class="fas fa-download"></i> Download Rearranged PDF</a>` : '<p>Rearranged, but no file URL.</p>';
        showAlert('PDF pages rearranged!', 'success');
    } catch (e) {
        console.error(e);
        showAlert(String(e.message || e), 'error');
    } finally {
        hideLoading();
    }
}

async function processExtractText() {
    const input = document.getElementById('pdf-file');
    const file = input.files[0];
    const pages = document.getElementById('text-pages').value.trim();
    if (!file) return showAlert('Select a PDF.', 'error');

    try {
        showLoading('Extracting text...');
        const formData = new FormData();
        formData.append('file', file);
        if (pages) formData.append('pages', pages);

        const res = await fetch('/api/pdf/extract-text', { method: 'POST', body: formData });
        const result = await res.json();
        if (!res.ok || !result.success) throw new Error(result.message || 'Extract failed');

        const text = (result.metadata && result.metadata.text) || '';
        const textArea = document.getElementById('extracted-text');
        const wrapper = document.getElementById('text-output');
        textArea.value = text;
        wrapper.style.display = 'block';

        // Buttons
        document.getElementById('copy-text-btn').onclick = () => {
            navigator.clipboard.writeText(textArea.value).then(() => showAlert('Copied to clipboard', 'success', 2000));
        };
        document.getElementById('download-text-btn').onclick = () => {
            const blob = new Blob([textArea.value], { type: 'text/plain;charset=utf-8' });
            const url = URL.createObjectURL(blob);
            downloadFile(url, 'extracted.txt');
            URL.revokeObjectURL(url);
        };

        showAlert('Text extracted!', 'success');
    } catch (e) {
        console.error(e);
        showAlert(String(e.message || e), 'error');
    } finally {
        hideLoading();
    }
}

async function processConvertToPdf() {
    const input = document.getElementById('convert-file');
    const file = input.files[0];
    if (!file) return showAlert('Select a file.', 'error');

    try {
        showLoading('Converting to PDF...');
        const formData = new FormData();
        formData.append('file', file);
        const res = await fetch('/api/pdf/convert-to-pdf', { method: 'POST', body: formData });
        const result = await res.json();
        if (!res.ok || !result.success) throw new Error(result.message || 'Convert failed');

        const container = document.getElementById('convert-result');
        container.style.display = 'block';
        const url = result.output_url || '';
        container.innerHTML = url ? `<a class=\"btn btn-success\" href=\"${url}\" target=\"_blank\"><i class=\"fas fa-download\"></i> Download PDF</a>` : '<p>Converted, but no file URL.</p>';
        showAlert('Converted to PDF!', 'success');
    } catch (e) {
        console.error(e);
        showAlert(String(e.message || e), 'error');
    } finally {
        hideLoading();
    }
}

// Expose loader
window.loadPdfToolContent = loadPdfToolContent;
