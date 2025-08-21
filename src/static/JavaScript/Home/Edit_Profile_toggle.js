document.addEventListener("DOMContentLoaded", () => {
    const editBtn = document.getElementById("edit-profile-btn");
    const modal = document.getElementById("edit-profile-modal");
    const closeModal = document.getElementById("close-modal");

    editBtn.onclick = () => modal.style.display = "block";
    closeModal.onclick = () => modal.style.display = "none";
    window.onclick = (event) => {
        if (event.target === modal) modal.style.display = "none";
    };

    // Dark/Light toggle
    const themeToggle = document.getElementById("theme-toggle");
    themeToggle.addEventListener("change", () => {
        document.body.classList.toggle("dark-mode");
        document.body.classList.toggle("light-mode");
    });
});