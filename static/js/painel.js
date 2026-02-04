document.addEventListener("DOMContentLoaded", () => {

    const mensagens = document.querySelector(".mensagens");
    const input = document.querySelector(".resposta input");
    const botao = document.querySelector(".enviar");

    botao.onclick = () => {
        const texto = input.value.trim();
        if (!texto) return;

        const msg = document.createElement("div");
        msg.classList.add("msg", "atendente");
        msg.innerHTML = `${texto}<span class="hora">agora</span>`;

        mensagens.appendChild(msg);
        input.value = "";
        mensagens.scrollTop = mensagens.scrollHeight;

        console.log("Mensagem enviada:", texto);
    };

});
