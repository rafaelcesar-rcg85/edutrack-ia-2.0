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

### Requirement: Implementar status e data de entrega na atividade
O sistema SHALL permitir registrar o status da atividade e opcionalmente uma data de entrega.

#### Scenario: Atividade Concluída
- **WHEN** a atividade é registrada com status "Concluída"
- **THEN** o sistema salva a nota sem exigir a data de entrega

#### Scenario: Atividade Para Entregar
- **WHEN** a atividade é registrada com status "Para Entregar"
- **THEN** o sistema salva o registro incluindo a data prevista para entrega (data_entrega)

### Requirement: Editar uma atividade existente
O sistema SHALL permitir que o usuário altere os dados de uma atividade previamente registrada.

#### Scenario: Edição de dados da atividade
- **WHEN** o usuário envia novos dados para uma atividade via requisição PATCH na rota respectiva
- **THEN** o sistema atualiza o registro no banco de dados com as novas informações, mantendo as associações intactas
