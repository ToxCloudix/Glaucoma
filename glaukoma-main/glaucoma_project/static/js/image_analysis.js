// static/js/image_analysis.js

document.addEventListener("DOMContentLoaded", function() {
    // === 1. Инициализация всех нужных DOM-элементов ===
    const imageContainer      = document.getElementById('image-container');
    const imageURL            = imageContainer.getAttribute('data-image-url');
    const imageId             = imageContainer.getAttribute('data-image-id');
    const canvas              = document.getElementById('image-canvas');
    const ctx                 = canvas.getContext('2d');
    const brightnessSlider    = document.getElementById('brightness-slider');
    const contrastSlider      = document.getElementById('contrast-slider');
    const enableDotsButton    = document.getElementById('enable-dots-button');
    const cdrButton           = document.getElementById('enable-dots-button');
    const removeChannelButton = document.getElementById('remove-channel-button');
    const autoCdrButton       = document.getElementById('auto-cdr-button');
    const cdrCheckbox         = document.getElementById('cdr-checkbox');
    const autoCdrCheckbox     = document.getElementById('auto-cdr-checkbox');
    const uwagiTextarea       = document.getElementById('uwagi');
    const diagnozaTextarea    = document.getElementById('diagnoza');
    const saveButton          = document.querySelector('.footer button');
    const segModal            = document.getElementById('seg-modal');
    const segImg              = document.getElementById('auto-seg-img');
    const spanClose           = segModal.querySelector(".close");

    // === 2. Переменные для Canvas и CDR ===
    let image = new Image();
    let scale = 0.3;
    let offsetX = 0, offsetY = 0;
    let isDragging = false;
    let lastX = 0, lastY = 0;
    let selectedChannel;
    let dotsRelative = [];
    let placingDot = false;
    let currentLine = 1;

    // === 3. Функции работы с изображением (здесь вставьте свою логику) ===
    function reset() {
        scale = 0.3;
        offsetX = 0;
        offsetY = 0;
        selectedChannel = undefined;
        placingDot = false;
        brightnessSlider.value = 0;
        contrastSlider.value = 0;
        resetCanvas();
        drawLines();
    }

    function resetCanvas() {
        const maxWidth = imageContainer.clientWidth;
        const aspectRatio = image.width / image.height;
        if (image.width > maxWidth) {
            canvas.width = maxWidth;
            canvas.height = maxWidth / aspectRatio;
        } else {
            canvas.width = image.width;
            canvas.height = image.height;
        }
        drawImage();
    }

    function drawImage(doSplitChannel = true) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(image, offsetX, offsetY, image.width * scale, image.height * scale);
        if (doSplitChannel) splitChannel(selectedChannel);
        if (dotsRelative.length === 2) {
            const d1 = convertRelativeToCanvas(dotsRelative[0]);
            const d2 = convertRelativeToCanvas(dotsRelative[1]);
            drawLineAndDistance(d1, d2);
        }
    }

    function splitChannel(channel) {
        drawImage(false);
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const data = imageData.data;
        const channelIndex = { red: 0, green: 1 };
        selectedChannel = channel;
        const idx = channelIndex[channel];
        if (idx === undefined) return;
        for (let i = 0; i < data.length; i += 4) {
            const v = data[i + idx];
            data[i] = data[i + 1] = data[i + 2] = 0;
            data[i + idx] = v;
        }
        ctx.putImageData(imageData, 0, 0);
        drawLines();
    }

    function convertCanvasToRelative(dot) {
        return {
            x: (dot.x - offsetX) / (image.width * scale),
            y: (dot.y - offsetY) / (image.height * scale)
        };
    }

    function convertRelativeToCanvas(dot) {
        return {
            x: dot.x * image.width * scale + offsetX,
            y: dot.y * image.height * scale + offsetY
        };
    }

    function getMousePosition(event) {
        const rect = canvas.getBoundingClientRect();
        return { x: event.clientX - rect.left, y: event.clientY - rect.top };
    }

    function drawLines() {
        if (dotsRelative.length >= 2) {
            const d1 = convertRelativeToCanvas(dotsRelative[0]);
            const d2 = convertRelativeToCanvas(dotsRelative[1]);
            drawLineAndDistance(d1, d2);
        }
        if (dotsRelative.length === 4) {
            const d3 = convertRelativeToCanvas(dotsRelative[2]);
            const d4 = convertRelativeToCanvas(dotsRelative[3]);
            drawLineAndDistance(d3, d4);
        }
    }

    function drawLineAndDistance(dot1, dot2, isMouse = false) {
        ctx.beginPath();
        ctx.moveTo(dot1.x, dot1.y);
        ctx.lineTo(dot2.x, dot2.y);
        ctx.strokeStyle = isMouse ? 'blue' : 'red';
        ctx.lineWidth = 2;
        ctx.stroke();
        const dist = Math.hypot(dot2.x - dot1.x, dot2.y - dot1.y).toFixed(2);
        if (dist !== "0.00") {
            const midX = (dot1.x + dot2.x) / 2;
            const midY = (dot1.y + dot2.y) / 2;
            ctx.fillStyle = 'black';
            ctx.font = '14px Arial';
            ctx.fillText(`${dist}px`, midX, midY - 10);
        }
    }

    function constrainImage() {
        const maxW = imageContainer.clientWidth;
        const maxH = imageContainer.clientHeight;
        const sw = image.width * scale;
        const sh = image.height * scale;
        if (offsetX > 0) offsetX = 0;
        if (offsetY > 0) offsetY = 0;
        if (offsetX < maxW - sw) offsetX = maxW - sw;
        if (offsetY < maxH - sh) offsetY = maxH - sh;
        redrawImage(true);
    }

    function applyFilters() {
        const b = parseInt(brightnessSlider.value);
        const c = parseInt(contrastSlider.value);
        ctx.filter = `brightness(${100 + b}%) contrast(${100 + c}%)`;
        redrawImage(true);
    }

    function removeChannel(channel) {
        drawImage(false);
        if (channel === null) {
            drawImage();
        } else {
            const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            const data = imgData.data;
            if (channel === "red") {
                for (let i = 0; i < data.length; i += 4) data[i] = 0;
            } else if (channel === "green") {
                for (let i = 0; i < data.length; i += 4) data[i + 1] = 0;
            }
            ctx.putImageData(imgData, 0, 0);
        }
        drawLines();
    }

    function calculateCDR() {
        if (dotsRelative.length === 4) {
            const d1 = convertRelativeToCanvas(dotsRelative[0]);
            const d2 = convertRelativeToCanvas(dotsRelative[1]);
            const d3 = convertRelativeToCanvas(dotsRelative[2]);
            const d4 = convertRelativeToCanvas(dotsRelative[3]);
            const len1 = Math.hypot(d2.x - d1.x, d2.y - d1.y);
            const len2 = Math.hypot(d4.x - d3.x, d4.y - d3.y);
            const minLen = Math.min(len1, len2);
            const maxLen = Math.max(len1, len2);
            const cdr = (minLen / maxLen).toFixed(2);
            cdrButton.innerText = `CDR ≈ ${cdr}`;
            updateCdrCheckboxState();
        }
    }

    function removeLastLine() {
        if (dotsRelative.length >= 2) {
            dotsRelative.splice(-2, 2);
            placingDot = dotsRelative.length < 4;
            redrawImage(true);
        }
        if (dotsRelative.length < 4) {
            cdrButton.innerText = "CDR";
        }
    }

    function esc(text) {
        return text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    }

    function removeLine(text) {
        const pattern = new RegExp(`\\n*${esc(text)}\\n*`, "g");
        uwagiTextarea.value = uwagiTextarea.value.replace(pattern, "");
    }

    function redrawImage(clearCanvas = true) {
        if (clearCanvas) {
            drawImage();
        }
        if (selectedChannel) splitChannel(selectedChannel);
        drawLines();
    }

    // === 4. Автовызов при загрузке страницы ===
    image.src = imageURL;
    image.onload = reset;

    // === 5. Навесить остальные обработчики ===

    // 5.1 Фильтры яркости / контраста
    brightnessSlider.addEventListener('input', applyFilters);
    contrastSlider.addEventListener('input', applyFilters);

    // 5.2 Масштабирование и панорамирование
    canvas.addEventListener('wheel', (e) => {
        e.preventDefault();
        const zoomFactor = 1.05;
        const mx = e.offsetX, my = e.offsetY;
        const prevScale = scale;
        scale = e.deltaY < 0 ? scale * zoomFactor : scale / zoomFactor;
        scale = Math.max(0.1, Math.min(scale, 5));
        const deltaScale = scale / prevScale;
        offsetX = mx - (mx - offsetX) * deltaScale;
        offsetY = my - (my - offsetY) * deltaScale;
        constrainImage();
        redrawImage(true);
    });

    canvas.addEventListener('mousedown', (e) => {
        isDragging = true;
        lastX = e.clientX;
        lastY = e.clientY;
    });

    canvas.addEventListener('mousemove', (e) => {
        if (isDragging) {
            const dx = e.clientX - lastX;
            const dy = e.clientY - lastY;
            offsetX += dx;
            offsetY += dy;
            lastX = e.clientX;
            lastY = e.clientY;
            redrawImage(true);
        }
    });

    canvas.addEventListener('mouseup', () => { isDragging = false; });
    canvas.addEventListener('mouseleave', () => { isDragging = false; });

    // 5.3 Удаление каналов
    removeChannelButton.addEventListener('click', () => {
        selectedChannel = undefined;
        resetCanvas();
        drawLines();
    });

    // 5.4 CDR: постановка точек
    enableDotsButton.addEventListener('click', () => {
        dotsRelative = [];
        placingDot = true;
        currentLine = 1;
        redrawImage(true);
    });

    canvas.addEventListener('mousemove', (e) => {
        if (placingDot && (dotsRelative.length === 1 || dotsRelative.length === 3)) {
            redrawImage();
            const mp = convertCanvasToRelative(getMousePosition(e));
            const d1 = convertRelativeToCanvas(dotsRelative[dotsRelative.length - 1]);
            const d2 = convertRelativeToCanvas(mp);
            drawLineAndDistance(d1, d2, true);
        }
    });

    canvas.addEventListener('click', (e) => {
        if (placingDot) {
            const mp = getMousePosition(e);
            const rel = convertCanvasToRelative(mp);
            dotsRelative.push(rel);
            if (dotsRelative.length === 2) {
                currentLine = 2;
            } else if (dotsRelative.length === 4) {
                placingDot = false;
            }
            redrawImage();
        }
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            if (dotsRelative.length >= 2) removeLastLine();
            else placingDot = false;
        }
    });

    canvas.addEventListener('click', () => {
        if (dotsRelative.length === 4) calculateCDR();
    });

    // 5.5 AutoCDR
    autoCdrButton.addEventListener("click", () => {
        fetch(`/glaucoma/image/auto_cdr/${imageId}/`)
            .then(r => r.json())
            .then(data => {
                autoCdrButton.innerText = `AutoCDR ≈ ${Number(data.cdr).toFixed(2)}`;
                updateAutoCdrCheckboxState();
            })
            .catch(err => console.error("Ошибка AutoCDR:", err));
    });

    // 5.6 AutoSegmentation
    document.getElementById("auto-segmentation-button").addEventListener("click", () => {
        fetch(`/glaucoma/image/auto_segmentation/${imageId}/`)
            .then(r => r.json())
            .then(data => {
                segImg.src = "data:image/png;base64," + data.segmented_image;
                segModal.style.display = "block";
            })
            .catch(err => console.error("Ошибка AutoSegmentation:", err));
    });

    spanClose.addEventListener("click", () => { segModal.style.display = "none"; });
    window.addEventListener("click", (ev) => {
        if (ev.target === segModal) segModal.style.display = "none";
    });

    // 5.7 Чекбоксы
    function updateCdrCheckboxState() {
        cdrCheckbox.disabled = !cdrButton.innerText.includes("≈");
    }

    function updateAutoCdrCheckboxState() {
        autoCdrCheckbox.disabled = !autoCdrButton.innerText.includes("≈");
    }

    updateCdrCheckboxState();
    updateAutoCdrCheckboxState();

    cdrCheckbox.addEventListener("change", function() {
        const text = enableDotsButton.innerText;
        if (this.checked) uwagiTextarea.value += "\n" + text;
        else removeLine(text);
    });

    autoCdrCheckbox.addEventListener("change", function() {
        const line = autoCdrButton.innerText;
        if (this.checked) uwagiTextarea.value += "\n" + line;
        else removeLine(line);
    });

    // 5.8 Восстановление из savedAnalysis
    const savedAnalysisElement = document.getElementById("savedAnalysis");
    const savedAnalysis = savedAnalysisElement
        ? JSON.parse(savedAnalysisElement.textContent)
        : null;
    if (savedAnalysis) {
        uwagiTextarea.value    = savedAnalysis.notes || "";
        diagnozaTextarea.value = savedAnalysis.description || "";
        if (savedAnalysis.cdr) {
            cdrButton.innerText = `CDR ≈ ${Number(savedAnalysis.cdr).toFixed(2)}`;
        }
        if (Array.isArray(savedAnalysis.cdr_points) && savedAnalysis.cdr_points.length) {
            dotsRelative = savedAnalysis.cdr_points;
            redrawImage();
        }
    }

    // 5.9 Сохранение анализа
    saveButton.addEventListener('click', () => {
        const notes       = uwagiTextarea.value;
        const description = diagnozaTextarea.value;
        let cdr = 0;
        const cdrText = cdrButton.innerText;
        if (cdrText.includes('≈')) {
            cdr = parseFloat(cdrText.split('≈')[1]);
        }

        console.log("Сохраняем точки:", dotsRelative);
        const payload = {
            notes: notes,
            description: description,
            cdr: cdr,
            cdr_points: dotsRelative
        };

        fetch(`/glaucoma/image/save_analysis/${imageId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': (function() {
                    const key = 'csrftoken';
                    let cookieValue = null;
                    if (document.cookie && document.cookie !== '') {
                        const cookies = document.cookie.split(';');
                        for (let i = 0; i < cookies.length; i++) {
                            const c = cookies[i].trim();
                            if (c.substring(0, key.length + 1) === (key + '=')) {
                                cookieValue = decodeURIComponent(c.substring(key.length + 1));
                                break;
                            }
                        }
                    }
                    return cookieValue;
                })()
            },
            body: JSON.stringify(payload)
        })
        .then(response => response.json())
        .then(data => {
            console.log("Ответ сохранения:", data);
            alert(data.message || "Анализ успешно сохранён!");
        })
        .catch(error => {
            console.error("Ошибка сохранения анализа:", error);
            alert("Ошибка при сохранении анализа. Попробуйте ещё раз.");
        });
    });

    // 5.10 *** Блок «Аккордеон» ***
    const acc = document.getElementsByClassName("accordion");
    for (let i = 0; i < acc.length; i++) {
        acc[i].addEventListener("click", function() {
            this.classList.toggle("active");
            const panel = this.nextElementSibling;
            if (panel.style.maxHeight) {
                panel.style.maxHeight = null;
            } else {
                panel.style.maxHeight = panel.scrollHeight + "px";
            }
        });
    }

});
