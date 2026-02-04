// ===============================
// ESTADO GLOBAL DO CHAT
// ===============================
const estadoChat = {
    modo: "bot", // bot | humano
};

// ===============================
// ATUALIZAR STATUS VISUAL
// ===============================
function atualizarStatus(texto) {
    const status = document.getElementById("chatStatus");
    if (!status) return;

    status.textContent = texto;
    status.classList.remove("typing");
}

// ===============================
// ATIVAR BOT
// ===============================
function ativarBot() {

    estadoChat.modo = "bot";

    const input = document.getElementById("messageInput");

    if (input) {
        input.disabled = true;
        input.placeholder = "Atendimento automático em andamento";
    }

    atualizarStatus("bot ativo");
}

// ===============================
// ATIVAR HUMANO
// ===============================
function ativarHumano() {

    estadoChat.modo = "humano";

    const input = document.getElementById("messageInput");

    if (input) {
        input.disabled = false;
        input.placeholder = "Digite uma mensagem";
        input.focus();
    }

    atualizarStatus("atendimento humano");
}

// ===============================
// ESTADO DE LEITURA
// ===============================
window.estadoLeitura = {
    noFimDoChat: true
};

// ===============================
// EXPOSIÇÃO GLOBAL
// ===============================
window.estadoChat = estadoChat;
window.ativarBot = ativarBot;
window.ativarHumano = ativarHumano;
