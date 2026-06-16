// =============================================================
// apis/.../delete_professores.xs — DELETE /professores/{id}
// =============================================================
// Endpoint que remove um professor existente do aluno autenticado.
// ATENÇÃO: Disciplinas com prof_id referenciando este professor
// podem ficar com referência quebrada após a exclusão.
// =============================================================
// Deleta um professor existente do aluno autenticado
query "professores/{id}" verb=DELETE {
  api_group = "Rafael's Workspace"
  auth = "user"

  input {
    // ID do professor capturado da URL — ex: DELETE /professores/4
    int id
  }

  stack {
    // Passo 1: Busca o registro pelo ID
    db.get professores {
      field_name = "id"
      field_value = $input.id
    } as $existing_prof

    // Passo 2: Verifica se pertence ao usuário logado
    precondition ($existing_prof != null && $existing_prof.user_id == $auth.id) {
      error_type = "accessdenied"
      error = "Professor não encontrado ou acesso negado"
    }

    // Passo 3: Remove o registro do banco de dados
    db.del professores {
      field_name = "id"
      field_value = $input.id
    }
  }

  response = {success: true, message: "Professor deletado com sucesso"}
}
