const estadoChat = {
    modo: "bot", // bot | humano
};

function ativarBot() {
    estadoChat.modo = "bot";

    const input = document.getElementById("messageInput");
    const status = document.getElementById("chatStatus");

    input.disabled = true;
    input.placeholder = "Atendimento automático em andamento";

    status.textContent = "bot ativo";
    status.classList.remove("typing");
}

function ativarHumano() {
    estadoChat.modo = "humano";

    const input = document.getElementById("messageInput");
    const status = document.getElementById("chatStatus");

    input.disabled = false;
    input.placeholder = "Digite uma mensagem";

    status.textContent = "atendimento humano";
}

window.ativarBot = ativarBot;
window.ativarHumano = ativarHumano;
window.estadoChat = estadoChat;

