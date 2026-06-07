// =============================================================
// apis/.../delete_professores.xs — DELETE /professores
// =============================================================
// Endpoint que remove um professor existente do aluno autenticado.
//
// Método HTTP: DELETE (remoção)
// Autenticação: obrigatória (token JWT)
//
// Fluxo com verificação de propriedade:
//   1. Busca o professor filtrando por id E user_id simultaneamente
//   2. Se não encontrado → erro (acesso negado ou não existe)
//   3. Remove o registro permanentemente do banco
//
// ATENÇÃO: Disciplinas que referenciam este professor via prof_id
// podem ficar com referência quebrada após a exclusão.
// =============================================================

// Deleta um professor existente
query "professores" verb=DELETE {
  description = "Deleta um professor existente"
  auth = "user"

  input {
    // ID do professor a ser removido
    int id {
      description = "ID do professor a ser deletado"
    }
  }

  stack {
    // Busca o professor garantindo que pertence ao usuário
    // Se o professor existir mas pertencer a outro usuário, o where
    // não encontrará o registro e $existing_prof será null
    db.get "professores" {
      where = ($db.professores.id == $input.id) && ($db.professores.user_id == $auth.id)
    } as $existing_prof
    
    // Se não foi encontrado, lança erro e interrompe a execução
    precondition {
      if ($existing_prof == null) {
        throw "Professor não encontrado ou acesso negado"
      }
    }

    // Remove o registro do banco usando filtro where para segurança
    db.delete "professores" {
      where = $db.professores.id == $input.id
    }
  }

  // Retorna confirmação de sucesso ao cliente
  response = {
    success: true
    message: "Professor deletado com sucesso"
  }
}
