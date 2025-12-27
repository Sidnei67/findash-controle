# database.py
import sqlite3


def init_db():
    """Inicializa o banco de dados e cria a tabela se não existir."""
    conn = sqlite3.connect('financas.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            tipo TEXT NOT NULL,
            categoria TEXT NOT NULL,
            descricao TEXT,
            valor REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def adicionar_transacao(data, tipo, categoria, descricao, valor):
    """Insere uma nova transação no banco."""
    conn = sqlite3.connect('financas.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO transacoes (data, tipo, categoria, descricao, valor)
        VALUES (?, ?, ?, ?, ?)
    ''', (data, tipo, categoria, descricao, valor))
    conn.commit()
    conn.close()


def obter_todas_transacoes():
    """Retorna todas as transações para análise."""
    conn = sqlite3.connect('financas.db')
    c = conn.cursor()
    c.execute('SELECT id, data, tipo, categoria, descricao, valor FROM transacoes')
    data = c.fetchall()
    conn.close()
    return data
