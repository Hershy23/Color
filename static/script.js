document.getElementById("imageUpload").addEventListener("change", function (event) {
    const file = event.target.files[0];

    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            document.getElementById("preview").src = e.target.result;
            document.getElementById("preview").style.display = "block";
            document.getElementById("predictBtn").disabled = false;
        };
        reader.readAsDataURL(file);
    }
});

document.getElementById("predictBtn").addEventListener("click", function () {
    const fileInput = document.getElementById("imageUpload");
    const file = fileInput.files[0];
    const predictionText = document.getElementById("predictionText");

    if (!file) {
        predictionText.innerText = "Please select an image first!";
        return;
    }

    predictionText.innerText = "Processing...";

    const formData = new FormData();
    formData.append("file", file);

    // ✅ Use relative path or ensure correct URL
    fetch("/predict", {
        method: "POST",
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Server error");
        }
        return response.json();
    })
    .then(data => {
        // Update with your actual prediction handling
        const skinTones = ["Light", "Medium-Light", "Medium-Dark", "Dark"];
        predictionText.innerText = skinTones[data.prediction] || "Unknown";
    })
    .catch(error => {
        console.error("Error:", error);
        predictionText.innerText = "Error: " + error.message;
    });
});
