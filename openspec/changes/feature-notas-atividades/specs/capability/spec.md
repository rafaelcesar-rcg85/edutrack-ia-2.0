# feature-notas-atividades Specification

## Purpose
Estabelecer os requisitos para o banco de dados e API a fim de permitir o lançamento de notas de alunos em atividades específicas por professores no EduTrack AI.

## ADDED Requirements

### Requirement: Criar tabela para notas de atividades
O sistema SHALL armazenar os lançamentos de nota das atividades.

#### Scenario: Professor lança a nota
- **WHEN** o professor envia a nota para a atividade do aluno
- **THEN** o sistema salva a nota na tabela `activity_grades` com a associação do `user_id` correspondente

### Requirement: Criar API para lançar nota
O sistema SHALL prover um endpoint do tipo POST para registrar as notas.

#### Scenario: Gravação de notas via API
- **WHEN** uma requisição válida é enviada para a rota POST `/activity_grades`
- **THEN** o sistema insere o registro vinculando a nota à atividade e ao aluno correspondente
