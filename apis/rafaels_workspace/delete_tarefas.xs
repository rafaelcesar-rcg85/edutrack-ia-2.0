// =============================================================
// apis/.../delete_tarefas.xs — DELETE /tarefas/{id}
// =============================================================
// Endpoint que remove uma tarefa/nota existente do aluno autenticado.
// =============================================================
// Deleta uma tarefa existente do aluno autenticado
query "tarefas/{id}" verb=DELETE {
  api_group = "Rafael's Workspace"
  auth = "user"

  input {
    // ID da tarefa capturado da URL — ex: DELETE /tarefas/7
    int id
  }

  stack {
    // Passo 1: Busca o registro pelo ID
    db.get tarefas {
      field_name = "id"
      field_value = $input.id
    } as $existing_tarefa

    // Passo 2: Verifica se pertence ao usuário logado
    precondition ($existing_tarefa != null && $existing_tarefa.user_id == $auth.id) {
      error_type = "accessdenied"
      error = "Tarefa não encontrada ou acesso negado"
    }

    // Passo 3: Remove o registro do banco de dados
    db.del tarefas {
      field_name = "id"
      field_value = $input.id
    }
  }

  response = {success: true, message: "Tarefa deletada com sucesso"}
}
