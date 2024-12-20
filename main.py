import json
import sys
import pandas as pd
from antlr4 import *
from ExpressoesLexer import ExpressoesLexer
from ExpressoesParser import ExpressoesParser

database = {}

def executeStmt(stmt):
    if stmt.createStmt():
        executeCreate(stmt.createStmt())
    elif stmt.selectStmt():
        executeSelect(stmt.selectStmt())
    elif stmt.insertStmt():
        executeInsert(stmt.insertStmt())
    elif stmt.updateStmt():
        executeUpdate(stmt.updateStmt())
    elif stmt.deleteItemStmt():
        executeDeleteItem(stmt.deleteItemStmt())
    elif stmt.deleteTableStmt():
        executeDeleteTable(stmt.deleteTableStmt())
    elif stmt.clearStmt():
        executeClear(stmt.clearStmt())
    elif stmt.showStmt():
        executeShow(stmt.showStmt())
    elif stmt.exportStmt():
        executeExport(stmt.exportStmt())
    elif stmt.exportAllStmt():
        executeExportAll(stmt.exportAllStmt())
    else:
        raise Exception("Nao identificado")

def executeCreate(stmt):
    table = stmt.table().getText()
    if table not in database.keys():
        database[table] = []
        print(f"Tabela {table} criada")
    else:
        raise Exception(f"Tabela {table} ja existe")

def executeSelect(stmt):
    table = stmt.table().getText()
    columns = [col.getText() for col in stmt.columns().ID()]
    if table in database:
        print(f"Selecionando de {table}:")
        for row in database[table]:
            print({col: row[col] for col in columns})
    else:
        raise Exception(f"Tabela {table} nao encontrada")

def executeInsert(stmt):
    table = stmt.table().getText()
    columns = [col.getText() for col in stmt.columns().ID()]
    values = [val.getText() for val in stmt.values().value()]
    if table in database:
        row = dict(zip(columns, values))
        database[table].append(row)
        print(f"Adicionado em {table}: {row}")
    else:
        raise Exception(f"Tabela {table} nao encontrada")

def executeUpdate(stmt):
    table = stmt.table().getText()
    assignments = {assign.ID().getText(): assign.value().getText() for assign in stmt.assignments().assignment()}
    condition_column = stmt.condition().ID().getText()
    condition_value = stmt.condition().value().getText()
    if table in database:
        for row in database[table]:
            if row.get(condition_column) == condition_value:
                for col, val in assignments.items():
                    row[col] = val
        print(f"Atualizada a tabela {table} onde {condition_column} = {condition_value}: {assignments}")
    else:
        raise Exception(f"Tabela {table} nao encontrada")

def executeDeleteItem(stmt):
    table = stmt.table().getText()
    condition_column = stmt.condition().ID().getText()
    condition_value = stmt.condition().value().getText()
    if table in database:
        original_length = len(database[table])
        database[table] = [row for row in database[table] if row.get(condition_column) != condition_value]
        if len(database[table]) < original_length:
            print(f"Deletado item da tabela {table} onde {condition_column} = {condition_value}")
        else:
            print(f"Nenhum item encontrado na tabela {table} onde {condition_column} = {condition_value}")
    else:
        raise Exception(f"Tabela {table} nao encontrada")
    
def executeDeleteTable(stmt):
    table = stmt.table().getText()
    if table in database:
        database.pop(table)
        print(f"Tabela {table} deletada")
    else:
        raise Exception(f"Tabela {table} nao encontrada")

def executeClear(stmt):
    table = stmt.table().getText()
    if table in database:
        database[table].clear()
        print(f"Tabela {table} limpa")
    else:
        raise Exception(f"Tabela {table} nao encontrada")

def executeShow(stmt):
    table = stmt.table().getText()
    if table in database:
        # print(f"Tabela {table}: {database[table]}")
        df = pd.DataFrame(database[table])
        print(df)
    else:
        raise Exception(f"Tabela {table} nao encontrada")

def executeExport(stmt):
    table = stmt.table().getText()
    if table in database:
        if bool(database):
            json_dict = json.dumps(database[table], indent=4)
            with open(f'{table}.json', 'w') as f:
                f.write(json_dict)
            print(f"tabela {table} exportado como JSON com sucesso")
        else:
            raise Exception(f"Tabela vazia")
    else:
        raise Exception(f"Nao exitem dados para exportar")

def executeExportAll(stmt):
    if bool(database):
        json_dict = json.dumps(database, indent=4)
        with open('output.json', 'w') as f:
            f.write(json_dict)
        print(f"tabelas exportadas como JSON com sucesso")
    else:
        raise Exception(f"Nao exitem dados para exportar")


# COMMANDS EXAMPLES:
# CREATE users;
# SELECT id, name FROM users;
# INSERT INTO users (id, name) VALUES (1, 'Neymar');
# UPDATE users SET name = 'Ronaldinho' WHERE name = 'Messi';
# DELETE FROM users WHERE id = 3;
# DELETE users;
# CLEAR users;
# SHOW users;
# EXPORT users;

input_text = """
CREATE futebol;
INSERT INTO futebol (id, name) VALUES (1, 'Neymar');
INSERT INTO futebol (id, name) VALUES (2, 'Messi');
SELECT id, name FROM futebol;
SHOW futebol;

CREATE basquete;
INSERT INTO basquete (id, name) VALUES (1, 'Lebron');
INSERT INTO basquete (id, name) VALUES (2, 'Michael Jordan');
SELECT id, name FROM basquete;
SHOW basquete;

EXPORT futebol;
EXPORT basquete;
EXPORT ALL;
"""
# SELECT id, name FROM users;
# UPDATE users SET name = 'Ronaldinho' WHERE name = 'Messi';
# SHOW users;

input_stream = InputStream(input_text)
lexer = ExpressoesLexer(input_stream)
stream = CommonTokenStream(lexer)
parser = ExpressoesParser(stream)
tree = parser.prog()

# Verifica se houve erro sintático
if parser.getNumberOfSyntaxErrors() > 0:
    print("erro sintático")
    sys.exit(1)

print(tree.toStringTree(recog=parser))

for stmt in tree.stmt():
    executeStmt(stmt)