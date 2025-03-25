fetch("/predict", {
    method: "POST",
    body: formData
})
.then(response => {
    if (!response.ok) {
        throw new Error("Server error: " + response.status);
    }
    return response.json();
})
.then(data => {
    document.getElementById("result").innerText = "Predicted Skin Tone: " + data.skin_tone;
})
.catch(error => {
    console.error("Error:", error);
    document.getElementById("result").innerText = "Prediction failed! " + error.message;
});
