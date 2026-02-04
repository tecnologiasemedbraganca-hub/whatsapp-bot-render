document.addEventListener("DOMContentLoaded", () => {

    console.log("app.js carregado");

    const input = document.getElementById("messageInput");
    const sendBtn = document.getElementById("sendBtn");
    const messages = document.getElementById("chatMessages");

    const assumeBtn = document.getElementById("assumeBtn");
    const endBtn = document.getElementById("endBtn");

    // ==========================
    // BOTÕES DE CONTROLE
    // ==========================
    assumeBtn.addEventListener("click", () => {
        console.log("Assumir clicado");
        ativarHumano();
    });

    endBtn.addEventListener("click", () => {
        console.log("Encerrar clicado");

        ativarBot();

        adicionarMensagem(
            "bot",
            "🔒 Atendimento encerrado. O bot assumiu novamente."
        );
    });
    
    ///detectar scroll do atendente
    messages.addEventListener("scroll", () => {
    const margem = 40;
    const noFim =
        messages.scrollTop + messages.clientHeight >=
        messages.scrollHeight - margem;

    estadoLeitura.noFimDoChat = noFim;

    if (noFim) {
        marcarMensagensComoLidas();
    }
    });

    // ==========================
    // FUNÇÃO ÚNICA DE MENSAGEM
    // ==========================
    function adicionarMensagem(remetente, texto) {

        const msg = document.createElement("div");
        msg.classList.add("message");

        if (remetente === "usuario") {
            msg.classList.add("other");

            if (!estadoLeitura.noFimDoChat) {
               msg.classList.add("unread");
             }
         }   

        if (remetente === "bot") {
            msg.classList.add("user");    // direita
        }

        if (remetente === "atendente") {
            msg.classList.add("agent");   // direita
        }

        msg.innerHTML = `
            <div class="bubble">
                <span class="text">${texto}</span>
                <span class="time">agora</span>
            </div>
        `;

        // 🔥 SEMPRE NO FINAL
        messages.appendChild(msg);

        agruparMensagens();
        messages.scrollTop = messages.scrollHeight;
    }
    
    ///marcar mensagens como lidas
    
    function marcarMensagensComoLidas() {
    const naoLidas = document.querySelectorAll(
        ".message.other.unread"
    );

    naoLidas.forEach(msg => {
        msg.classList.remove("unread");

        const time = msg.querySelector(".time");
        if (time) {
            time.classList.remove("unread");
            time.classList.add("read");
            time.textContent = time.textContent.replace("✓", "✓✓");
        }
     });

    // 🔮 FUTURO: avisar backend
    // fetch("/api/marcar-lidas", ...)
    }

    // ==========================
    // ENVIO ATENDENTE
    // ==========================
    function enviarMensagem() {

        if (estadoChat.modo !== "humano") {
            console.warn("Bot ativo — envio bloqueado");
            return;
        }

        const texto = input.value.trim();
        if (!texto) return;

        adicionarMensagem("atendente", texto);
        input.value = "";

        console.log("Mensagem do atendente:", texto);

        // 🔮 futuro: enviar para backend
    }

    sendBtn.addEventListener("click", enviarMensagem);

    input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            enviarMensagem();
        }
    });

    // ==========================
    // SIMULAÇÃO USUÁRIO (DEV)
    // ==========================
    window.simularMensagemUsuario = function (texto) {

        mostrarDigitando();

        setTimeout(() => {
            esconderDigitando();
            adicionarMensagem("usuario", texto);
        }, 1200);
    };

});
