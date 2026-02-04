document.addEventListener("DOMContentLoaded", () => {

    const botaoEnviar = document.querySelector(".resposta button");
    const input = document.querySelector(".resposta input");
    const mensagens = document.querySelector(".mensagens");

    botaoEnviar.addEventListener("click", () => {

        const texto = input.value.trim();
        if (!texto) return;

        const div = document.createElement("div");
        div.classList.add("mensagem", "atendente");
        div.innerText = texto;

        mensagens.appendChild(div);
        input.value = "";
        mensagens.scrollTop = mensagens.scrollHeight;

        // Aqui depois vamos integrar com o backend
        console.log("Mensagem enviada:", texto);
    });

});

