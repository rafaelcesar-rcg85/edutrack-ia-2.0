query "tarefas" verb=DELETE {
  description = "Deleta uma tarefa existente"
  auth = "user"

  input {
    int id {
      description = "ID da tarefa a ser deletada"
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

    db.delete "tarefas" {
      where = $db.tarefas.id == $input.id
    }
  }

  response = {
    success: true
    message: "Tarefa deletada com sucesso"
  }
}
