function uploadImage() {
    let fileInput = document.getElementById("fileInput");
    let file = fileInput.files[0];

    if (!file) {
        alert("Please select an image!");
        return;
    }

    let formData = new FormData();
    formData.append("file", file);

    fetch("/predict", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById("result").innerText = "Error: " + data.error;
        } else {
            document.getElementById("result").innerText = "Predicted Skin Tone: " + data.skin_tone;
            
            let colors = {
                "light": "#FFDFC4",
                "mid-light": "#E1B899",
                "mid-dark": "#AE734A",
                "dark": "#5C3A21"
            };

            let colorBox = document.getElementById("colorBox");
            colorBox.style.backgroundColor = colors[data.skin_tone];
            colorBox.style.display = "block";

            let reader = new FileReader();
            reader.onload = function(e) {
                let img = document.getElementById("preview");
                img.src = e.target.result;
                img.style.display = "block";
            };
            reader.readAsDataURL(file);
        }
    })
    .catch(error => console.error("Error:", error));
}
