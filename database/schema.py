from database.connection import get_db

def criar_tabelas():

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuario (
            id SERIAL PRIMARY KEY,
            telefone TEXT UNIQUE,
            nome TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS atendente (
            id SERIAL PRIMARY KEY,
            nome TEXT,
            email TEXT,
            telefone TEXT UNIQUE,
            ativo BOOLEAN DEFAULT TRUE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS conversa (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER REFERENCES usuario(id),
            atendente_id INTEGER REFERENCES atendente(id),
            status TEXT DEFAULT 'aberta',
            iniciada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            finalizada_em TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS mensagem (
            id SERIAL PRIMARY KEY,
            conversa_id INTEGER REFERENCES conversa(id),
            whatsapp_id TEXT,
            remetente TEXT,
            conteudo TEXT,
            tipo TEXT DEFAULT 'texto',
            criada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS arquivo (
            id SERIAL PRIMARY KEY,
            mensagem_id INTEGER REFERENCES mensagem(id),
            tipo TEXT,
            url TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id SERIAL PRIMARY KEY,
            conversa_id INTEGER REFERENCES conversa(id),
            atendente_id INTEGER REFERENCES atendente(id),
            nota INTEGER CHECK (nota BETWEEN 1 AND 5),
            comentario TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cur.close()
    conn.close()
