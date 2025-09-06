/**
 * Image tools JavaScript
 * Handles image-specific functionality and tool interfaces
 */

/**
 * Load image tool content into modal
 * @param {string} tool - Tool identifier
 */
function loadImageToolContent(tool) {
    const content = getImageToolHTML(tool);
    DOM.modalBody.innerHTML = content;
    
    // Setup tool-specific event listeners
    setupImageToolEvents(tool);
}

/**
 * Get HTML content for image tools
 * @param {string} tool - Tool identifier
 * @returns {string} HTML content
 */
function getImageToolHTML(tool) {
    const commonFileUpload = `
        <div class="form-group">
            <label class="form-label">Select Image</label>
            <div class="file-upload" id="file-upload">
                <i class="fas fa-cloud-upload-alt"></i>
                <p>Click to select an image or drag and drop</p>
                <input type="file" id="image-file" accept="image/*" style="display: none;">
            </div>
            <div id="file-info" class="file-info" style="display: none;"></div>
        </div>
    `;

    const previewSection = `
        <div class="preview-container" id="preview-container" style="display: none;">
            <div class="preview-section">
                <h4>Original</h4>
                <img id="original-preview" class="image-preview" alt="Original">
            </div>
            <div class="preview-section">
                <h4>Preview</h4>
                <img id="processed-preview" class="image-preview" alt="Processed">
            </div>
        </div>
    `;

    switch (tool) {
        case 'resize':
            return `
                ${commonFileUpload}
                <div class="form-group">
                    <label class="form-label">Width (pixels)</label>
                    <input type="number" id="width" class="form-input" min="1" max="5000" value="800">
                </div>
                <div class="form-group">
                    <label class="form-label">Height (pixels)</label>
                    <input type="number" id="height" class="form-input" min="1" max="5000" value="600">
                </div>
                <div class="form-group">
                    <label class="form-label">
                        <input type="checkbox" id="maintain-aspect" class="form-checkbox" checked>
                        Maintain aspect ratio
                    </label>
                </div>
                ${previewSection}
                <div class="form-group">
                    <button type="button" id="process-btn" class="btn btn-primary" disabled>
                        <i class="fas fa-expand-arrows-alt"></i>
                        Resize Image
                    </button>
                    <button type="button" id="download-btn" class="btn btn-success" style="display: none;">
                        <i class="fas fa-download"></i>
                        Download
                    </button>
                </div>
            `;

        case 'crop':
            return `
                ${commonFileUpload}
                <div id="crop-controls" style="display: none;">
                    <div class="form-group">
                        <p>Click and drag on the image to select the crop area.</p>
                        <canvas id="crop-canvas" style="max-width: 100%; border: 1px solid #ddd; cursor: crosshair;"></canvas>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                        <div class="form-group">
                            <label class="form-label">X (Left)</label>
                            <input type="number" id="crop-x" class="form-input" min="0" value="0">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Y (Top)</label>
                            <input type="number" id="crop-y" class="form-input" min="0" value="0">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Width</label>
                            <input type="number" id="crop-width" class="form-input" min="1" value="100">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Height</label>
                            <input type="number" id="crop-height" class="form-input" min="1" value="100">
                        </div>
                    </div>
                </div>
                ${previewSection}
                <div class="form-group">
                    <button type="button" id="process-btn" class="btn btn-primary" disabled>
                        <i class="fas fa-crop"></i>
                        Crop Image
                    </button>
                    <button type="button" id="download-btn" class="btn btn-success" style="display: none;">
                        <i class="fas fa-download"></i>
                        Download
                    </button>
                </div>
            `;

        case 'rotate':
            return `
                ${commonFileUpload}
                <div class="form-group">
                    <label class="form-label">Rotation Angle (degrees)</label>
                    <input type="range" id="angle" class="form-input" min="-180" max="180" value="0" step="1">
                    <div style="text-align: center; margin-top: 0.5rem;">
                        <span id="angle-value">0°</span>
                    </div>
                </div>
                <div class="form-group">
                    <label class="form-label">
                        <input type="checkbox" id="expand" class="form-checkbox" checked>
                        Expand image to fit rotated content
                    </label>
                </div>
                ${previewSection}
                <div class="form-group">
                    <button type="button" id="process-btn" class="btn btn-primary" disabled>
                        <i class="fas fa-redo"></i>
                        Rotate Image
                    </button>
                    <button type="button" id="download-btn" class="btn btn-success" style="display: none;">
                        <i class="fas fa-download"></i>
                        Download
                    </button>
                </div>
            `;

        case 'enhance':
            return `
                ${commonFileUpload}
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <div class="form-group">
                        <label class="form-label">Brightness</label>
                        <input type="range" id="brightness" class="form-input" min="0.1" max="3" value="1" step="0.1">
                        <div style="text-align: center; margin-top: 0.5rem;">
                            <span id="brightness-value">1.0</span>
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Contrast</label>
                        <input type="range" id="contrast" class="form-input" min="0.1" max="3" value="1" step="0.1">
                        <div style="text-align: center; margin-top: 0.5rem;">
                            <span id="contrast-value">1.0</span>
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Saturation</label>
                        <input type="range" id="saturation" class="form-input" min="0.1" max="3" value="1" step="0.1">
                        <div style="text-align: center; margin-top: 0.5rem;">
                            <span id="saturation-value">1.0</span>
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Sharpness</label>
                        <input type="range" id="sharpness" class="form-input" min="0.1" max="3" value="1" step="0.1">
                        <div style="text-align: center; margin-top: 0.5rem;">
                            <span id="sharpness-value">1.0</span>
                        </div>
                    </div>
                </div>
                ${previewSection}
                <div class="form-group">
                    <button type="button" id="process-btn" class="btn btn-primary" disabled>
                        <i class="fas fa-magic"></i>
                        Enhance Image
                    </button>
                    <button type="button" id="download-btn" class="btn btn-success" style="display: none;">
                        <i class="fas fa-download"></i>
                        Download
                    </button>
                </div>
            `;

        case 'remove-bg':
            return `
                ${commonFileUpload}
                <div id="bg-controls" style="display: none;">
                    <div class="form-group">
                        <p>Click on the image to mark foreground objects. The AI will automatically detect and remove the background.</p>
                        <canvas id="bg-canvas" style="max-width: 100%; border: 1px solid #ddd; cursor: crosshair;"></canvas>
                    </div>
                    <div class="form-group">
                        <button type="button" id="clear-points" class="btn btn-secondary">
                            <i class="fas fa-eraser"></i>
                            Clear Points
                        </button>
                    </div>
                </div>
                ${previewSection}
                <div class="form-group">
                    <button type="button" id="process-btn" class="btn btn-primary" disabled>
                        <i class="fas fa-cut"></i>
                        Remove Background
                    </button>
                    <button type="button" id="download-btn" class="btn btn-success" style="display: none;">
                        <i class="fas fa-download"></i>
                        Download
                    </button>
                </div>
            `;

        case 'convert':
            return `
                ${commonFileUpload}
                <div class="form-group">
                    <label class="form-label">Target Format</label>
                    <select id="target-format" class="form-input">
                        <option value="JPEG">JPEG</option>
                        <option value="PNG">PNG</option>
                        <option value="WEBP">WebP</option>
                        <option value="BMP">BMP</option>
                        <option value="TIFF">TIFF</option>
                    </select>
                </div>
                <div class="form-group" id="quality-group">
                    <label class="form-label">Quality (for JPEG/WebP)</label>
                    <input type="range" id="quality" class="form-input" min="1" max="100" value="95">
                    <div style="text-align: center; margin-top: 0.5rem;">
                        <span id="quality-value">95</span>
                    </div>
                </div>
                ${previewSection}
                <div class="form-group">
                    <button type="button" id="process-btn" class="btn btn-primary" disabled>
                        <i class="fas fa-exchange-alt"></i>
                        Convert Format
                    </button>
                    <button type="button" id="download-btn" class="btn btn-success" style="display: none;">
                        <i class="fas fa-download"></i>
                        Download
                    </button>
                </div>
            `;

        default:
            return '<p>Tool not implemented yet.</p>';
    }
}

/**
 * Setup event listeners for image tools
 * @param {string} tool - Tool identifier
 */
function setupImageToolEvents(tool) {
    // File upload handling
    setupFileUpload();
    
    // Tool-specific events
    switch (tool) {
        case 'resize':
            setupResizeEvents();
            break;
        case 'crop':
            setupCropEvents();
            break;
        case 'rotate':
            setupRotateEvents();
            break;
        case 'enhance':
            setupEnhanceEvents();
            break;
        case 'remove-bg':
            setupBackgroundRemovalEvents();
            break;
        case 'convert':
            setupConvertEvents();
            break;
    }
    
    // Process button
    const processBtn = document.getElementById('process-btn');
    if (processBtn) {
        processBtn.addEventListener('click', () => processImage(tool));
    }
}

/**
 * Setup file upload functionality
 */
function setupFileUpload() {
    const fileUpload = document.getElementById('file-upload');
    const fileInput = document.getElementById('image-file');
    const fileInfo = document.getElementById('file-info');
    const processBtn = document.getElementById('process-btn');

    // Click to select file
    fileUpload.addEventListener('click', () => {
        fileInput.click();
    });

    // Drag and drop
    fileUpload.addEventListener('dragover', (e) => {
        e.preventDefault();
        fileUpload.classList.add('dragover');
    });

    fileUpload.addEventListener('dragleave', () => {
        fileUpload.classList.remove('dragover');
    });

    fileUpload.addEventListener('drop', (e) => {
        e.preventDefault();
        fileUpload.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelection(files[0]);
        }
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelection(e.target.files[0]);
        }
    });

    function handleFileSelection(file) {
        // Validate file type
        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp', 'image/tiff'];
        if (!validateFileType(file, allowedTypes)) {
            showAlert('Please select a valid image file.', 'error');
            return;
        }

        // Show file info
        fileInfo.innerHTML = `
            <strong>${file.name}</strong><br>
            Size: ${formatFileSize(file.size)}<br>
            Type: ${file.type}
        `;
        fileInfo.style.display = 'block';

        // Enable process button
        if (processBtn) {
            processBtn.disabled = false;
        }

        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            const originalPreview = document.getElementById('original-preview');
            if (originalPreview) {
                originalPreview.src = e.target.result;
                document.getElementById('preview-container').style.display = 'grid';
                // If crop tool is active, reveal controls once image is loaded
                const cropControls = document.getElementById('crop-controls');
                if (cropControls) {
                    cropControls.style.display = 'block';
                    // Defer to ensure image has layout
                    setTimeout(() => initializeCropCanvas(), 0);
                }

                // If background removal tool is active, reveal its controls
                const bgControls = document.getElementById('bg-controls');
                if (bgControls) {
                    bgControls.style.display = 'block';
                }
            }
        };
        reader.readAsDataURL(file);
    }
}

/**
 * Setup resize tool events
 */
function setupResizeEvents() {
    const widthInput = document.getElementById('width');
    const heightInput = document.getElementById('height');
    const maintainAspect = document.getElementById('maintain-aspect');

    let originalAspectRatio = 1;

    // Update aspect ratio when image loads
    const originalPreview = document.getElementById('original-preview');
    originalPreview.addEventListener('load', () => {
        originalAspectRatio = originalPreview.naturalWidth / originalPreview.naturalHeight;
        widthInput.value = originalPreview.naturalWidth;
        heightInput.value = originalPreview.naturalHeight;
    });

    // Maintain aspect ratio
    widthInput.addEventListener('input', () => {
        if (maintainAspect.checked) {
            heightInput.value = Math.round(widthInput.value / originalAspectRatio);
        }
    });

    heightInput.addEventListener('input', () => {
        if (maintainAspect.checked) {
            widthInput.value = Math.round(heightInput.value * originalAspectRatio);
        }
    });
}

/**
 * Setup rotate tool events
 */
function setupRotateEvents() {
    const angleSlider = document.getElementById('angle');
    const angleValue = document.getElementById('angle-value');

    angleSlider.addEventListener('input', () => {
        angleValue.textContent = angleSlider.value + '°';
    });
}

/**
 * Setup enhance tool events
 */
function setupEnhanceEvents() {
    const controls = ['brightness', 'contrast', 'saturation', 'sharpness'];
    
    controls.forEach(control => {
        const slider = document.getElementById(control);
        const value = document.getElementById(`${control}-value`);
        
        if (slider && value) {
            slider.addEventListener('input', () => {
                value.textContent = parseFloat(slider.value).toFixed(1);
            });
        }
    });
}

/**
 * Setup convert tool events
 */
function setupConvertEvents() {
    const formatSelect = document.getElementById('target-format');
    const qualityGroup = document.getElementById('quality-group');
    const qualitySlider = document.getElementById('quality');
    const qualityValue = document.getElementById('quality-value');

    formatSelect.addEventListener('change', () => {
        const format = formatSelect.value;
        const showQuality = format === 'JPEG' || format === 'WEBP';
        qualityGroup.style.display = showQuality ? 'block' : 'none';
    });

    if (qualitySlider && qualityValue) {
        qualitySlider.addEventListener('input', () => {
            qualityValue.textContent = qualitySlider.value;
        });
    }
}

/**
 * Setup crop tool events
 */
function setupCropEvents() {
    // Inputs
    const xInput = document.getElementById('crop-x');
    const yInput = document.getElementById('crop-y');
    const wInput = document.getElementById('crop-width');
    const hInput = document.getElementById('crop-height');

    // Sync when user types
    ;[xInput, yInput, wInput, hInput].forEach(inp => {
        if (!inp) return;
        inp.addEventListener('input', () => {
            if (typeof window.drawCropRect === 'function') {
                window.drawCropRect();
            }
        });
    });

    // Initialize when original image loads
    const originalPreview = document.getElementById('original-preview');
    if (originalPreview) {
        originalPreview.addEventListener('load', () => {
            initializeCropCanvas();
        });
    }
}

/**
 * Initialize crop canvas and mouse handlers
 */
function initializeCropCanvas() {
    const img = document.getElementById('original-preview');
    const canvas = document.getElementById('crop-canvas');
    if (!img || !canvas || !img.complete) return;

    // Match canvas to displayed image size
    const rect = img.getBoundingClientRect();
    canvas.width = Math.round(rect.width);
    canvas.height = Math.round(rect.height);

    const ctx = canvas.getContext('2d');
    const xInput = document.getElementById('crop-x');
    const yInput = document.getElementById('crop-y');
    const wInput = document.getElementById('crop-width');
    const hInput = document.getElementById('crop-height');

    // Start with centered square selection
    const initW = Math.min(canvas.width, canvas.height) * 0.5;
    const initH = initW;
    const initX = Math.max(0, (canvas.width - initW) / 2);
    const initY = Math.max(0, (canvas.height - initH) / 2);
    xInput.value = Math.round(initX);
    yInput.value = Math.round(initY);
    wInput.value = Math.round(initW);
    hInput.value = Math.round(initH);
    drawCropRect();

    let dragging = false;
    let startX = 0, startY = 0;

    canvas.onmousedown = (e) => {
        dragging = true;
        const p = getCanvasMousePos(canvas, e);
        startX = p.x; startY = p.y;
        xInput.value = p.x;
        yInput.value = p.y;
        wInput.value = 0;
        hInput.value = 0;
        drawCropRect();
    };

    canvas.onmousemove = (e) => {
        if (!dragging) return;
        const p = getCanvasMousePos(canvas, e);
        const x = Math.max(0, Math.min(startX, p.x));
        const y = Math.max(0, Math.min(startY, p.y));
        const w = Math.min(canvas.width - x, Math.abs(p.x - startX));
        const h = Math.min(canvas.height - y, Math.abs(p.y - startY));
        xInput.value = Math.round(x);
        yInput.value = Math.round(y);
        wInput.value = Math.round(w);
        hInput.value = Math.round(h);
        drawCropRect();
    };

    window.onmouseup = () => { dragging = false; };

    function drawImageUnderlay() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        // Draw the displayed image into canvas for context (no scaling issues)
        // Create a temporary image to draw with current display size
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        // Darken overlay
        ctx.fillStyle = 'rgba(0,0,0,0.35)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

    function drawCropRect() {
        drawImageUnderlay();
        const x = parseInt(xInput.value || '0', 10);
        const y = parseInt(yInput.value || '0', 10);
        const w = parseInt(wInput.value || '0', 10);
        const h = parseInt(hInput.value || '0', 10);
        // Clear overlay where the crop is
        ctx.save();
        ctx.globalCompositeOperation = 'destination-out';
        ctx.fillStyle = 'rgba(0,0,0,1)';
        ctx.fillRect(x, y, w, h);
        ctx.restore();
        // Draw border
        ctx.strokeStyle = '#00b3ff';
        ctx.lineWidth = 2;
        ctx.setLineDash([6, 4]);
        ctx.strokeRect(x + 1, y + 1, Math.max(0, w - 2), Math.max(0, h - 2));
    }

    // Expose to other functions
    window.drawCropRect = drawCropRect;
}

/** Get mouse position relative to canvas */
function getCanvasMousePos(canvas, evt) {
    const rect = canvas.getBoundingClientRect();
    return {
        x: Math.round((evt.clientX - rect.left)),
        y: Math.round((evt.clientY - rect.top))
    };
}

/**
 * Setup background removal events
 */
function setupBackgroundRemovalEvents() {
    // TODO: Implement interactive point selection
    console.log('Background removal events setup - point selection to be implemented');
}

/**
 * Process image with selected tool
 * @param {string} tool - Tool identifier
 */
async function processImage(tool) {
    const fileInput = document.getElementById('image-file');
    const file = fileInput.files[0];
    
    if (!file) {
        showAlert('Please select an image first.', 'error');
        return;
    }

    try {
        showLoading('Processing image...');

        const formData = new FormData();
        formData.append('file', file);

        // Add tool-specific parameters
        switch (tool) {
            case 'resize':
                formData.append('width', document.getElementById('width').value);
                formData.append('height', document.getElementById('height').value);
                formData.append('maintain_aspect', document.getElementById('maintain-aspect').checked);
                break;
            case 'crop':
                // Scale crop rect from displayed pixels to natural image pixels
                const imgEl = document.getElementById('original-preview');
                const scaleX = imgEl ? (imgEl.naturalWidth / imgEl.clientWidth) : 1;
                const scaleY = imgEl ? (imgEl.naturalHeight / imgEl.clientHeight) : 1;
                const dx = parseInt(document.getElementById('crop-x').value || '0', 10);
                const dy = parseInt(document.getElementById('crop-y').value || '0', 10);
                const dw = parseInt(document.getElementById('crop-width').value || '0', 10);
                const dh = parseInt(document.getElementById('crop-height').value || '0', 10);
                const sx = Math.max(0, Math.round(dx * scaleX));
                const sy = Math.max(0, Math.round(dy * scaleY));
                const sw = Math.max(1, Math.round(dw * scaleX));
                const sh = Math.max(1, Math.round(dh * scaleY));
                formData.append('x', String(sx));
                formData.append('y', String(sy));
                formData.append('width', String(sw));
                formData.append('height', String(sh));
                break;
            case 'rotate':
                formData.append('angle', document.getElementById('angle').value);
                formData.append('expand', document.getElementById('expand').checked);
                break;
            case 'enhance':
                formData.append('brightness', document.getElementById('brightness').value);
                formData.append('contrast', document.getElementById('contrast').value);
                formData.append('saturation', document.getElementById('saturation').value);
                formData.append('sharpness', document.getElementById('sharpness').value);
                break;
            case 'convert':
                formData.append('target_format', document.getElementById('target-format').value);
                formData.append('quality', document.getElementById('quality').value);
                break;
        }

        const response = await fetch(`/api/image/${tool}`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            showAlert('Image processed successfully!', 'success');
            
            // Show processed image if available
            if (result.output_path || result.output_url) {
                const fileUrl = result.output_url || `/output/${String(result.output_path || '').split(/[\\\\/]/).pop()}`;
                const processedPreview = document.getElementById('processed-preview');
                if (processedPreview) {
                    processedPreview.src = fileUrl;
                }
                
                // Show download button
                const downloadBtn = document.getElementById('download-btn');
                if (downloadBtn) {
                    downloadBtn.style.display = 'inline-flex';
                    downloadBtn.onclick = () => {
                        downloadFile(fileUrl, `processed_${file.name}`);
                    };
                }
            }
        } else {
            showAlert(result.message || 'Processing failed', 'error');
        }

    } catch (error) {
        console.error('Processing error:', error);
        showAlert('An error occurred while processing the image.', 'error');
    } finally {
        hideLoading();
    }
}

// Expose image tool functions globally
window.loadImageToolContent = loadImageToolContent;
