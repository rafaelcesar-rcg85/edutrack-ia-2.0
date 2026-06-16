// =============================================================
// apis/authentication/delete_faltas.xs — DELETE /faltas/{id}
// =============================================================
// Endpoint que remove um registro de falta do aluno autenticado.
// Grupo: Authentication (canonical: iiiYAbKm)
// =============================================================
// Deleta um registro de falta existente do aluno autenticado
// Retorna confirmação de sucesso
// Deleta um registro de falta existente do aluno autenticado
query "faltas/{id}" verb=DELETE {
  api_group = "Authentication"
  auth = "user"

  input {
    // ID da falta capturado da URL — ex: DELETE /faltas/7
    // ID da falta a ser deletada
    int id
  }

  stack {
    // Passo 1: Busca o registro pelo ID
    db.get faltas {
      field_name = "id"
      field_value = $input.id
    } as $existing_falta

    // Passo 2: Verifica se a falta pertence ao usuário logado
    // Garante que a falta pertence ao aluno autenticado
    precondition ($existing_falta != null && $existing_falta.user_id == $auth.id) {
      error_type = "accessdenied"
      error = "Falta não encontrada ou acesso negado"
    }

    // Passo 3: Remove o registro do banco de dados
    db.del faltas {
      field_name = "id"
      field_value = $input.id
    }
  }

  response = {success: true, message: "Falta removida com sucesso"}
}
