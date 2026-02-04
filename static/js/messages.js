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
document.addEventListener("DOMContentLoaded", () => {
    agruparMensagens();
});

// Executa sempre que uma nova mensagem for adicionada
window.agruparMensagens = agruparMensagens;

