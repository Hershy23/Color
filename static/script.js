document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('imageUpload');
    const predictBtn = document.getElementById('predictBtn');
    const preview = document.getElementById('preview');
    const predictionText = document.getElementById('predictionText');
    const loader = document.querySelector('.loader');

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
        predictionText.innerHTML = '<span class="analyzing">Analyzing...</span>';
        
        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (!response.ok || !data.success) {
                throw new Error(data.message || 'Prediction failed');
            }

            // Display results
            const confidencePercent = (data.confidence * 100).toFixed(1);
            predictionText.innerHTML = `
                <strong>${data.label}</strong>
                <div class="confidence">${confidencePercent}% confidence</div>
                <div class="tips">${getSkinCareTips(data.prediction)}</div>
            `;

        } catch (error) {
            console.error('Error:', error);
            showError(error.message);
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
