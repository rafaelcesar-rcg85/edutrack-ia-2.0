// =============================================================
// tables/faltas.xs — Tabela de Registro de Faltas
// =============================================================
// Armazena cada falta registrada pelo aluno em uma disciplina.
//
// Relacionamentos:
//   faltas.disc_id   → disciplinas.id (disciplina da falta)
//   faltas.course_id → curso.id     (curso — para filtros)
//   faltas.user_id   → user.id        (aluno dono do registro)
// =============================================================

table "faltas" {
  // auth = false: segurança gerenciada pelas APIs (auth = "user")
  auth = false

  schema {
    // Identificador único da falta (chave primária, auto-incremental)
    int id {
      description = "Identificador único do registro de falta"
    }

    // Chave estrangeira: disciplina em que a falta ocorreu
    int disc_id {
      table = "disciplinas"
      description = "ID da disciplina onde a falta foi registrada"
    }

    // Chave estrangeira: curso (opcional) — facilita filtros por curso
    int course_id? {
      table = "curso"
      description = "ID do curso ao qual a disciplina pertence"
    }

    // Data da aula em que o aluno faltou
    timestamp data_falta {
      description = "Data da aula em que a falta ocorreu"
    }

    // Justificativa ou observação — campo opcional
    text justificativa? {
      description = "Justificativa ou observação sobre a falta (opcional)"
    }

    // Peso da falta: quantas aulas foram perdidas neste dia
    // Ex: disciplina com 2 aulas seguidas → peso = 2
    // Padrão = 1 (falta simples de 1 aula)
    int peso?=1 {
      description = "Número de aulas perdidas neste registro (padrão: 1)"
    }

    // Chave estrangeira: garante que cada falta pertence a um único aluno
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
      // Índice composto para o filtro mais comum:
      // "faltas do aluno X na disciplina Y"
      type: "btree"
      field: [{name: "user_id"}, {name: "disc_id"}]
    }
  ]
}
