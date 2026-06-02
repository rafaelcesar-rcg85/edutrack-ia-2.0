table "disciplinas" {
  auth = false
  schema {
    int id {
      description = "Identificador único da disciplina"
    }

    text nome {
      description = "Nome da disciplina"
    }

    int prof_id {
      table = "professores"
      description = "ID do professor responsável por esta disciplina"
    }

    int course_id? {
      table = "courses"
      description = "ID do curso ao qual esta disciplina pertence"
    }

    int user_id {
      table = "user"
      description = "ID do usuário (aluno) dono deste registro"
    }

    timestamp created_at?=now {
      description = "Data de criação do registro"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {
      type: "btree"
      field: [{name: "user_id"}, {name: "course_id"}]
    }
  ]
}