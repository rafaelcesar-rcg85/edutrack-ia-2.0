# Proposal: Feature Cursos

## Why
Atualmente, as disciplinas e tarefas estão atreladas diretamente ao usuário. Isso impede que o aluno consiga organizar seus estudos de forma segmentada caso estude em mais de uma instituição simultaneamente (ex: Faculdade e Curso de Inglês). A introdução da entidade `courses` resolve este problema criando uma hierarquia organizacional lógica.

## What Changes
- Será criada uma nova tabela `courses`.
- A tabela `disciplinas` passará a possuir uma chave estrangeira para `courses` (`course_id`), deixando de ficar "solta" no escopo do usuário.
- O Frontend passará a exibir um "Curso Ativo" e filtrará todo o escopo de visualização (Dashboard, Disciplinas e Tarefas) com base nesta seleção.

## Impact
Esta é uma mudança estrutural (breaking change parcial). As disciplinas existentes no banco de dados ficarão órfãs de curso temporariamente até que o usuário crie um curso e o sistema migre esses dados, ou o banco de dados seja limpo para um recomeço. APIs relacionadas a disciplinas exigirão o envio obrigatório do parâmetro `course_id`.
