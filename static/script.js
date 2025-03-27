document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('imageUpload');
    const predictBtn = document.getElementById('predictBtn');
    const preview = document.getElementById('preview');
    const predictionText = document.getElementById('predictionText');
    const loader = document.querySelector('.loader');

    // Skin tone labels
    const skinTones = [
        "Very Light (Type I)",
        "Light (Type II)",
        "Medium (Type III)",
        "Olive (Type IV)",
        "Brown (Type V)",
        "Dark (Type VI)"
    ];

    fileInput.addEventListener('change', function(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.src = e.target.result;
                preview.style.display = "block";
                predictBtn.disabled = false;
            };
            reader.readAsDataURL(file);
        }
    });

    predictBtn.addEventListener('click', async function() {
        const file = fileInput.files[0];
        
        if (!file) {
            showError("Please select an image first!");
            return;
        }

        // Show loading state
        predictBtn.disabled = true;
        loader.style.display = "block";
        predictionText.innerHTML = '<span class="analyzing">Analyzing skin tone...</span>';
        
        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });

            // First check if we got any response at all
            if (!response) {
                throw new Error('No response from server');
            }

            // Then check if response is OK
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({
                    error: `Server error: ${response.status} ${response.statusText}`
                }));
                throw new Error(errorData.error || 'Request failed');
            }

            // Finally try to parse JSON
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Prediction failed');
            }

            // Display results
            const confidencePercent = (data.confidence * 100).toFixed(1);
            predictionText.innerHTML = `
                <strong>${skinTones[data.prediction] || "Unknown Type"}</strong>
                <div class="confidence">Confidence: ${confidencePercent}%</div>
                <div class="tips">${getSkinCareTips(data.prediction)}</div>
            `;

        } catch (error) {
            console.error('Prediction error:', error);
            showError(error.message || 'An unknown error occurred');
        } finally {
            predictBtn.disabled = false;
            loader.style.display = "none";
        }
    });

    function showError(message) {
        predictionText.innerHTML = `<span class="error">${message}</span>`;
    }

    function getSkinCareTips(skinType) {
        const tips = [
            "Use SPF 50+ daily, avoid peak sun hours",
            "Use SPF 30-50 daily, moisturize regularly",
            "Use SPF 15-30, consider vitamin C serums",
            "Use SPF 15-30, may tan easily",
            "Use SPF 15-30, focus on hydration",
            "Use SPF 15-30, may need extra moisture"
        ];
        return tips[skinType] || "Protect your skin from sun exposure";
    }
});
