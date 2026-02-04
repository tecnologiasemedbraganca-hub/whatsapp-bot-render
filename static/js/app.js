document.querySelectorAll(".conversation").forEach(item => {
    item.addEventListener("click", () => {

        document
            .querySelectorAll(".conversation")
            .forEach(c => c.classList.remove("active"));

        item.classList.add("active");

        console.log("Conversa selecionada");
    });
});

