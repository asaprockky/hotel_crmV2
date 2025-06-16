document.querySelectorAll(".nav-btn").forEach(btn => {
    btn.addEventListener("click", function() {
        document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("selected"));
        this.classList.add("selected");
    });
});
