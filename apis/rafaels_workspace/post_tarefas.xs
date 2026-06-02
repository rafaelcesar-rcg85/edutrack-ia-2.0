query "tarefas" verb=POST {
  description = "Cria uma nova tarefa vinculada a uma disciplina e um curso"
  auth = "user"

  input {
    text nome filters=trim {
      description = "Nome da tarefa"
    }
    int disc_id {
      description = "ID da disciplina"
    }
    int course_id {
      description = "ID do curso"
    }
    text status {
      description = "Status da tarefa"
    }
    decimal nota? {
      description = "Nota obtida na atividade"
    }
    timestamp data_entrega? {
      description = "Data de entrega para atividades futuras"
    }
  }

  stack {
    db.add "tarefas" {
      data = {
        user_id      : $auth.id
        course_id    : $input.course_id
        disc_id      : $input.disc_id
        nome         : $input.nome
        status       : $input.status
        nota         : $input.nota
        data_entrega : $input.data_entrega
        created_at   : "now"
      }
    } as $new_tarefa
  }

  response = $new_tarefa
}
