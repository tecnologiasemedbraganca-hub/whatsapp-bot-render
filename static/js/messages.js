// ===============================
// AGRUPAMENTO DE MENSAGENS
// ===============================
function agruparMensagens() {

    const mensagens = document.querySelectorAll(
        ".chat-messages .message:not(.typing)"
    );

    let remetenteAnterior = null;

    mensagens.forEach((msg) => {

        let remetenteAtual = "other";

        if (msg.classList.contains("user")) {
            remetenteAtual = "user";
        } else if (msg.classList.contains("agent")) {
            remetenteAtual = "agent";
        }

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
// DIGITANDO... (overlay)
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
        status.classList.remove("typing");
        // ⚠️ quem define online/bot/humano é o state.js
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
