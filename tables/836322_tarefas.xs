table "tarefas" {
  auth = false
  schema {
    int id {
      description = "Identificador único da tarefa/nota"
    }

    text nome {
      description = "Nome ou título da atividade"
    }

    int disc_id {
      table = "disciplinas"
      description = "ID da disciplina à qual esta tarefa pertence"
    }

    int course_id? {
      table = "courses"
      description = "ID do curso ao qual esta tarefa está vinculada"
    }

    text status {
      description = "Status da tarefa (ex: 'Concluída', 'Para Entregar')"
    }

    decimal nota? {
      description = "Nota obtida na atividade"
    }

    timestamp data_entrega? {
      description = "Data de entrega para atividades futuras"
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
      field: [{name: "user_id"}, {name: "course_id"}, {name: "disc_id"}]
    }
  ]
}