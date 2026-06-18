// =============================================================
// tables/836322_tarefas.xs — Tabela de Tarefas/Notas
// =============================================================
// Define a estrutura (schema) da tabela "tarefas" no banco
// de dados do Xano.
//
// Esta é a tabela mais completa do sistema — armazena todas
// as atividades e notas do aluno.
//
// Relacionamentos:
//   tarefas.disc_id   → disciplinas.id (disciplina da atividade)
//   tarefas.course_id → curso.id     (curso ao qual pertence)
//   tarefas.user_id   → user.id        (aluno dono do registro)
// =============================================================

table "tarefas" {
  // auth = false: segurança gerenciada pelas APIs (auth = "user")
  auth = false

  schema {
    // Identificador único da tarefa/nota (chave primária, auto-incremental)
    int id {
      description = "Identificador único da tarefa/nota"
    }

    // Título ou nome da atividade — campo obrigatório
    text nome {
      description = "Nome ou título da atividade"
    }

    // Chave estrangeira: vincula a tarefa a uma disciplina específica
    int disc_id {
      table = "disciplinas"
      description = "ID da disciplina à qual esta tarefa pertence"
    }

    // Chave estrangeira: vincula a tarefa a um curso (opcional)
    // Permite filtrar tarefas por curso no GET
    int course_id? {
      table = "curso"
      description = "ID do curso ao qual esta tarefa está vinculada"
    }

    // Status da tarefa — define se foi entregue ou ainda está pendente
    // Valores esperados: "Concluída" ou "Para Entregar"
    text status {
      description = "Status da tarefa (ex: 'Concluída', 'Para Entregar')"
    }

    // Nota obtida na atividade — campo opcional (só preenchido quando Concluída)
    // "decimal" permite valores com casas decimais como 8.5
    decimal nota? {
      description = "Nota obtida na atividade"
    }

    // Data de entrega — campo opcional, usado apenas para tarefas "Para Entregar"
    // "timestamp" armazena data e hora (ex: 2024-12-15T00:00:00)
    timestamp data_entrega? {
      description = "Data de entrega para atividades futuras"
    }

    // Tipo de avaliação (MAP, PROVA, SUB, PAI, OUTRO)
    text tipo? {
      description = "Tipo de avaliação para cálculo de médias"
    }

    // Chave estrangeira: garante que cada tarefa pertence a um único aluno
    int user_id {
      table = "user"
      description = "ID do usuário (aluno) dono deste registro"
    }

    // Data de criação automática do registro
    timestamp created_at?=now {
      description = "Data de criação do registro"
    }
  }

  // Índices para otimizar consultas frequentes
  index = [
    // Índice primário: unicidade do campo id
    {type: "primary", field: [{name: "id"}]}
    {
      // Índice composto para os filtros mais usados:
      // "tarefas do aluno X no curso Y na disciplina Z"
      type: "btree"
      field: [{name: "user_id"}, {name: "course_id"}, {name: "disc_id"}]
    }
  ]
}