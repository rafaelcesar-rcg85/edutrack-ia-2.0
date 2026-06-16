// =============================================================
// tables/836313_disciplinas.xs — Tabela de Disciplinas
// =============================================================
// Atualização: adicionados campos total_aulas e limite_faltas
// para controle de frequência por disciplina.
// Define a estrutura (schema) da tabela "disciplinas" no banco
// de dados do Xano.
//
// Esta tabela armazena as disciplinas cadastradas pelo aluno.
// Relacionamentos:
//   disciplinas.prof_id   → professores.id (professor responsável)
//   disciplinas.course_id → curso.id     (curso ao qual pertence)
//   disciplinas.user_id   → user.id        (aluno dono do registro)
// =============================================================
table "disciplinas" {
  // auth = false: segurança gerenciada pelas APIs (auth = "user")
  auth = false

  schema {
    // Identificador único da disciplina (chave primária, auto-incremental)
    int id {
      description = "Identificador único da disciplina"
    }

    // Nome da disciplina — campo obrigatório
    text nome {
      description = "Nome da disciplina"
    }

    // Chave estrangeira: ID do professor responsável por esta disciplina
    // O "table" cria um relacionamento formal entre as tabelas
    int prof_id {
      table = "professores"
      description = "ID do professor responsável por esta disciplina"
    }

    // Chave estrangeira: ID do curso ao qual a disciplina pertence
    // É opcional (?) pois uma disciplina pode existir sem curso definido
    int course_id? {
      table = "curso"
      description = "ID do curso ao qual esta disciplina pertence"
    }

    // Chave estrangeira: ID do usuário (aluno) — isolamento dos dados por usuário
    int user_id {
      table = "user"
      description = "ID do usuário (aluno) dono deste registro"
    }

    // Total de aulas previstas na disciplina — campo opcional
    int total_aulas? {
      description = "Total de aulas previstas na disciplina"
    }

    // Limite máximo de faltas permitidas — campo opcional
    // Normalmente equivale a 25% do total_aulas (ex: 5 de 20)
    int limite_faltas? {
      description = "Número máximo de faltas permitidas na disciplina"
    }

    // Data de criação automática — preenchida pelo Xano no momento do INSERT
    timestamp created_at?=now {
      description = "Data de criação do registro"
    }
  }

  // Índices para otimizar o desempenho das consultas
  index = [
    // Índice primário: garante unicidade do campo id
    {type: "primary", field: [{name: "id"}]}
    {
      // Índice composto para filtros por usuário e curso simultaneamente
      // Ex: "disciplinas do aluno X no curso Y"
      type: "btree"
      field: [{name: "user_id"}, {name: "course_id"}]
    }
  ]
}