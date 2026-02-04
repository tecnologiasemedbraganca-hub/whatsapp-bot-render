document.addEventListener("DOMContentLoaded", () => {

    const conversas = document.querySelectorAll(".conversation");

    conversas.forEach(conversa => {

        conversa.addEventListener("click", () => {

            // remove ativo de todas
            conversas.forEach(c => c.classList.remove("active"));

            // marca a clicada
            conversa.classList.add("active");

            // remove badge de não lidas
            const badge = conversa.querySelector(".badge");
            if (badge) {
                badge.style.display = "none";
                badge.textContent = "";
            }

            console.log("Conversa selecionada");

            // 🔮 futuro:
            // carregar mensagens via backend
            // fetch(`/api/conversa/${id}`)
        });

    });

});

