// =============================================================
// apis/.../delete_disciplinas.xs — DELETE /disciplinas
// =============================================================
// Endpoint que remove uma disciplina existente do aluno autenticado.
//
// Método HTTP: DELETE (remoção)
// Autenticação: obrigatória (token JWT)
//
// Fluxo com verificação de propriedade:
//   1. Busca a disciplina filtrando por id E user_id (dupla verificação)
//   2. Se não encontrada → erro (protege dados de outros usuários)
//   3. Se encontrada → remove permanentemente
// =============================================================

// Deleta uma disciplina existente
query "disciplinas" verb=DELETE {
  description = "Deleta uma disciplina existente"
  auth = "user"

  input {
    // ID da disciplina a ser removida — enviado no corpo da requisição
    int id {
      description = "ID da disciplina a ser deletada"
    }
  }

  stack {
    // Busca a disciplina garantindo que pertence ao usuário
    // Se o id existe mas pertence a outro usuário, o resultado será null
    // (a condição user_id == $auth.id falhará)
    db.get "disciplinas" {
      where = ($db.disciplinas.id == $input.id) && ($db.disciplinas.user_id == $auth.id)
    } as $existing_disc
    
    // Se a disciplina não foi encontrada (ou não pertence ao usuário), lança erro
    precondition {
      if ($existing_disc == null) {
        throw "Disciplina não encontrada ou acesso negado"
      }
    }

    // Remove o registro do banco de dados
    // Usa "where" para garantir que só o registro correto seja deletado
    db.delete "disciplinas" {
      where = $db.disciplinas.id == $input.id
    }
  }

  // Retorna confirmação de sucesso
  response = {
    success: true
    message: "Disciplina deletada com sucesso"
  }
}
