// =============================================================
// apis/.../delete_disciplinas.xs — DELETE /disciplinas/{id}
// =============================================================
// Endpoint que remove uma disciplina existente do aluno autenticado.
// =============================================================
// Deleta uma disciplina existente do aluno autenticado
query "disciplinas/{id}" verb=DELETE {
  api_group = "Rafael's Workspace"
  auth = "user"

  input {
    // ID da disciplina capturado da URL — ex: DELETE /disciplinas/7
    int id
  }

  stack {
    // Passo 1: Busca o registro pelo ID
    db.get disciplinas {
      field_name = "id"
      field_value = $input.id
    } as $existing_disc

    // Passo 2: Verifica se pertence ao usuário logado
    precondition ($existing_disc != null && $existing_disc.user_id == $auth.id) {
      error_type = "accessdenied"
      error = "Disciplina não encontrada ou acesso negado"
    }

    // Passo 3: Remove o registro do banco de dados
    db.del disciplinas {
      field_name = "id"
      field_value = $input.id
    }
  }

  response = {success: true, message: "Disciplina deletada com sucesso"}
}
