// ===============================
// AGRUPAMENTO DE MENSAGENS
// ===============================
function agruparMensagens() {
    const mensagens = document.querySelectorAll(".chat-messages .message");

    let remetenteAnterior = null;

    mensagens.forEach((msg) => {
        const remetenteAtual = msg.classList.contains("user")
            ? "user"
            : msg.classList.contains("agent")
            ? "agent"
            : "other";

        if (remetenteAtual === remetenteAnterior) {
            msg.classList.add("grouped");
        } else {
            msg.classList.remove("grouped");
        }

        remetenteAnterior = remetenteAtual;
    });
}

// Executa ao carregar
document.addEventListener("DOMContentLoaded", agruparMensagens);

// ===============================
// DIGITANDO...
// ===============================
function mostrarDigitando() {
    const status = document.getElementById("chatStatus");
    const typing = document.getElementById("typingIndicator");

    if (status) {
        status.textContent = "digitando…";
        status.classList.add("typing");
    }

    if (typing) {
        typing.style.display = "flex";
    }
}

function esconderDigitando() {
    const status = document.getElementById("chatStatus");
    const typing = document.getElementById("typingIndicator");

    if (status) {
        status.textContent = "online";
        status.classList.remove("typing");
    }

    if (typing) {
        typing.style.display = "none";
    }
}

// ===============================
// EXPOSIÇÃO GLOBAL (OBRIGATÓRIA)
// ===============================
window.agruparMensagens = agruparMensagens;
window.mostrarDigitando = mostrarDigitando;
window.esconderDigitando = esconderDigitando;
