// app/static/script.js
document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const uploadArea = document.getElementById('uploadArea');
    const audioFile = document.getElementById('audioFile');
    const browseBtn = document.getElementById('browseBtn');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const removeFile = document.getElementById('removeFile');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultsSection = document.getElementById('resultsSection');
    const sampleBtns = document.querySelectorAll('.sample-btn');

    // Upload area click
    uploadArea.addEventListener('click', () => {
        audioFile.click();
    });

    // Browse button click
    browseBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        audioFile.click();
    });

    // File selection
    audioFile.addEventListener('change', handleFileSelect);

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#2ecc71';
        uploadArea.style.transform = 'scale(1.02)';
    });

    uploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#3498db';
        uploadArea.style.transform = 'scale(1)';
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#3498db';
        uploadArea.style.transform = 'scale(1)';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            audioFile.files = files;
            handleFileSelect();
        }
    });

    // Remove file
    removeFile.addEventListener('click', () => {
        audioFile.value = '';
        fileInfo.style.display = 'none';
        uploadArea.style.display = 'block';
        resultsSection.style.display = 'none';
    });

    // Sample buttons
    sampleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const emotion = btn.dataset.emotion;
            // Simulate sample test (in production, would load actual sample file)
            simulateSampleTest(emotion);
        });
    });

    function handleFileSelect() {
        const file = audioFile.files[0];
        if (file) {
            fileName.textContent = file.name;
            fileInfo.style.display = 'block';
            uploadArea.style.display = 'none';
            
            // Upload and analyze
            uploadAudio(file);
        }
    }

    function uploadAudio(file) {
        const formData = new FormData();
        formData.append('audio', file);

        // Show loading
        loadingIndicator.style.display = 'flex';
        resultsSection.style.display = 'none';

        // Record start time
        const startTime = Date.now();

        fetch('/predict', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Calculate processing time
            const processingTime = ((Date.now() - startTime) / 1000).toFixed(2);
            
            // Hide loading
            loadingIndicator.style.display = 'none';
            
            if (data.success) {
                displayResults(data, processingTime);
            } else {
                showError(data.error);
            }
        })
        .catch(error => {
            loadingIndicator.style.display = 'none';
            showError('Network error: ' + error.message);
        });
    }

    function displayResults(data, processingTime) {
        // Update emotion
        document.getElementById('emotionText').textContent = data.emotion.toUpperCase();
        document.getElementById('confidenceBar').style.width = (data.confidence * 100) + '%';
        document.getElementById('confidenceText').textContent = (data.confidence * 100).toFixed(1) + '%';
        
        // Update emotion icon
        const emotionIcon = document.getElementById('emotionIcon');
        emotionIcon.innerHTML = getEmotionIcon(data.emotion);
        
        // Update result card color
        const resultCard = document.getElementById('emotionResultCard');
        resultCard.style.background = `linear-gradient(135deg, ${data.color} 0%, #764ba2 100%)`;
        
        // Update processing time
        document.getElementById('processingTime').textContent = processingTime + 's';

        // Display top 3 predictions
        displayTop3(data.top_3);

        // Create emotion chart
        createEmotionChart(data.all_predictions);

        // Create waveform plot
        if (data.waveform) {
            createWaveformPlot(data.waveform);
        }

        // Show results
        resultsSection.style.display = 'block';
        
        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    function displayTop3(top3) {
        const container = document.getElementById('top3List');
        container.innerHTML = '';
        
        top3.forEach((item, index) => {
            const colors = ['#FFD700', '#C0C0C0', '#CD7F32']; // Gold, Silver, Bronze
            const element = document.createElement('div');
            element.className = 'top-3-item';
            element.innerHTML = `
                <span class="emotion">
                    <span class="badge me-2" style="background-color: ${colors[index]}">
                        #${index + 1}
                    </span>
                    ${item.emotion.charAt(0).toUpperCase() + item.emotion.slice(1)}
                </span>
                <span class="confidence">${(item.confidence * 100).toFixed(1)}%</span>
            `;
            container.appendChild(element);
        });
    }

    function createEmotionChart(predictions) {
        const emotions = Object.keys(predictions);
        const values = Object.values(predictions).map(v => v * 100);
        
        const trace = {
            x: emotions.map(e => e.charAt(0).toUpperCase() + e.slice(1)),
            y: values,
            type: 'bar',
            marker: {
                color: values.map(v => {
                    if (v >= 70) return '#2ecc71';
                    if (v >= 40) return '#f1c40f';
                    return '#e74c3c';
                })
            },
            text: values.map(v => v.toFixed(1) + '%'),
            textposition: 'outside',
            hovertemplate: '<b>%{x}</b><br>Confidence: %{y:.1f}%<extra></extra>'
        };

        const layout = {
            title: 'Emotion Probabilities',
            xaxis: { 
                title: 'Emotion',
                tickangle: -45
            },
            yaxis: { 
                title: 'Confidence (%)',
                range: [0, 100]
            },
            height: 400,
            margin: { t: 50, b: 100, l: 60, r: 30 },
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)',
            font: { family: 'Segoe UI', size: 12 }
        };

        Plotly.newPlot('emotionChart', [trace], layout, {responsive: true});
    }

    function createWaveformPlot(waveform) {
        const trace = {
            y: waveform,
            type: 'scatter',
            mode: 'lines',
            line: {
                color: '#3498db',
                width: 1.5
            },
            fill: 'tozeroy',
            fillcolor: 'rgba(52,152,219,0.2)'
        };

        const layout = {
            title: 'Audio Waveform',
            xaxis: { 
                title: 'Sample',
                showgrid: true,
                gridcolor: 'rgba(0,0,0,0.1)'
            },
            yaxis: { 
                title: 'Amplitude',
                showgrid: true,
                gridcolor: 'rgba(0,0,0,0.1)'
            },
            height: 300,
            margin: { t: 40, b: 40, l: 50, r: 20 },
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)'
        };

        Plotly.newPlot('waveformPlot', [trace], layout, {responsive: true});
    }

    function simulateSampleTest(emotion) {
        // Simulate processing
        loadingIndicator.style.display = 'flex';
        resultsSection.style.display = 'none';
        
        setTimeout(() => {
            const mockData = {
                success: true,
                emotion: emotion,
                confidence: Math.random() * 0.3 + 0.7, // 70-100%
                top_3: [
                    {emotion: emotion, confidence: 0.85},
                    {emotion: emotion === 'happy' ? 'surprised' : 'neutral', confidence: 0.10},
                    {emotion: emotion === 'sad' ? 'calm' : 'happy', confidence: 0.05}
                ],
                all_predictions: {
                    neutral: 0.02,
                    calm: 0.03,
                    happy: emotion === 'happy' ? 0.85 : 0.05,
                    sad: emotion === 'sad' ? 0.82 : 0.04,
                    angry: emotion === 'angry' ? 0.88 : 0.03,
                    fearful: 0.02,
                    disgust: 0.01,
                    surprised: 0.02
                },
                waveform: Array.from({length: 5000}, () => Math.random() * 2 - 1),
                color: '#3498db'
            };
            
            loadingIndicator.style.display = 'none';
            displayResults(mockData, '1.2');
        }, 1500);
    }

    function getEmotionIcon(emotion) {
        const icons = {
            neutral: '<i class="fas fa-meh fa-5x"></i>',
            calm: '<i class="fas fa-peace fa-5x"></i>',
            happy: '<i class="fas fa-smile-beam fa-5x"></i>',
            sad: '<i class="fas fa-frown fa-5x"></i>',
            angry: '<i class="fas fa-angry fa-5x"></i>',
            fearful: '<i class="fas fa-dizzy fa-5x"></i>',
            disgust: '<i class="fas fa-tired fa-5x"></i>',
            surprised: '<i class="fas fa-surprise fa-5x"></i>'
        };
        return icons[emotion] || icons.neutral;
    }

    function showError(message) {
        alert('Error: ' + message);
        fileInfo.style.display = 'none';
        uploadArea.style.display = 'block';
    }
});