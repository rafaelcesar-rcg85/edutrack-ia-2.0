// =============================================================
// apis/.../delete_tarefas.xs — DELETE /tarefas
// =============================================================
// Endpoint que remove uma tarefa/nota existente do aluno autenticado.
//
// Método HTTP: DELETE (remoção)
// Autenticação: obrigatória (token JWT)
//
// Fluxo com verificação de propriedade:
//   1. Busca a tarefa filtrando por id E user_id
//   2. Se não encontrada → erro (proteção contra acesso não autorizado)
//   3. Se encontrada → remove permanentemente do banco
// =============================================================

// Deleta uma tarefa existente
query "tarefas" verb=DELETE {
  description = "Deleta uma tarefa existente"
  auth = "user"

  input {
    // ID da tarefa a ser removida — enviado no corpo da requisição
    int id {
      description = "ID da tarefa a ser deletada"
    }
  }

  stack {
    // Busca a tarefa garantindo que pertence ao usuário
    // A condição dupla evita que qualquer usuário autenticado delete
    // tarefas de outros usuários — apenas o dono pode deletar
    db.get "tarefas" {
      where = ($db.tarefas.id == $input.id) && ($db.tarefas.user_id == $auth.id)
    } as $existing_tarefa
    
    // Se a tarefa não for encontrada (ou pertencer a outro usuário), lança erro
    precondition {
      if ($existing_tarefa == null) {
        throw "Tarefa não encontrada ou acesso negado"
      }
    }

    // Remove o registro do banco de dados permanentemente
    db.delete "tarefas" {
      where = $db.tarefas.id == $input.id
    }
  }

  // Retorna confirmação de sucesso para o cliente
  response = {
    success: true
    message: "Tarefa deletada com sucesso"
  }
}
