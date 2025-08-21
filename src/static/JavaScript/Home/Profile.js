document.addEventListener("DOMContentLoaded", function() {
    const upload = document.getElementById("upload");
    const profileImg = document.getElementById("profile-img");

    upload.addEventListener("change", (event) => {
       const file = event.target.files[0];
       if (file && file.type.startsWith("image/")) {
           const reader = new FileReader();
           reader.onload = (e) => {
               profileImg.src = e.target.result;
           };
           reader.readAsDataURL(file);
       } else {
           alert("Please upload a valid image file.");
       }
    });
});