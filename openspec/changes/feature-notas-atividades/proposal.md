# Change: feature-notas-atividades

## Why
É necessário permitir que os professores possam registrar as notas (avaliações) dos alunos referentes a atividades acadêmicas específicas, para o acompanhamento do desempenho dentro do EduTrack AI.

## What Changes
Criação da estrutura de dados e da interface de gravação (API POST) para suportar o lançamento de notas em atividades. A implementação segue o escopo estrito solicitado e não contempla rotas adicionais (ex: GET, PATCH, DELETE) ou interfaces de frontend no momento.

## Impact
Esta alteração expandirá o esquema de banco de dados do Xano com uma nova tabela (`activity_grades`) e introduzirá uma nova rota de endpoint para a persistência das notas.
