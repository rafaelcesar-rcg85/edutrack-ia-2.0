query "tarefas" verb=PATCH {
  description = "Atualiza uma tarefa existente"
  auth = "user"

  input {
    int id {
      description = "ID da tarefa a ser atualizada"
    }
    text nome? filters=trim {
      description = "Novo nome da tarefa"
    }
    int disc_id? {
      description = "Novo ID da disciplina"
    }
    int course_id? {
      description = "Novo ID do curso"
    }
    text status? {
      description = "Novo status da tarefa"
    }
    decimal nota? {
      description = "Nova nota obtida"
    }
    timestamp data_entrega? {
      description = "Nova data de entrega"
    }
  }

  stack {
    // Busca a tarefa garantindo que pertence ao usuário
    db.get "tarefas" {
      where = ($db.tarefas.id == $input.id) && ($db.tarefas.user_id == $auth.id)
    } as $existing_tarefa
    
    precondition {
      if ($existing_tarefa == null) {
        throw "Tarefa não encontrada ou acesso negado"
      }
    }

    db.edit "tarefas" {
      id = $input.id
      data = {
        nome         : $input.nome ?? $existing_tarefa.nome
        disc_id      : $input.disc_id ?? $existing_tarefa.disc_id
        course_id    : $input.course_id ?? $existing_tarefa.course_id
        status       : $input.status ?? $existing_tarefa.status
        nota         : $input.nota ?? $existing_tarefa.nota
        data_entrega : $input.data_entrega ?? $existing_tarefa.data_entrega
      }
    } as $updated_tarefa
  }

  response = $updated_tarefa
}
