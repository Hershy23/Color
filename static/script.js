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

    if (!file) {
        alert("Please select an image first!");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    fetch("]https://color-2-5pxn.onrender.com/predict", {  // Update this URL
    method: "POST",
    body: formData
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error("Error:", error));

