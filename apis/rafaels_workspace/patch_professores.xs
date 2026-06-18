// =============================================================
// apis/.../patch_professores.xs — PATCH /professores
// =============================================================
// Endpoint que atualiza um professor existente do aluno autenticado.
//
// Método HTTP: PATCH (atualização parcial)
// Autenticação: obrigatória (token JWT)
//
// Fluxo:
//   1. Busca o professor filtrando por id E user_id
//   2. Se não encontrado → erro de acesso
//   3. Atualiza campos usando ?? (mantém valores anteriores se não enviados)
//
// O operador ?? (null coalescing) é fundamental aqui:
//   nome: $input.nome ?? $existing_prof.nome
//   → Se o cliente não enviar "nome", o valor atual é preservado
// =============================================================

// Atualiza um professor existente
query "professores" verb=PATCH {
  description = "Atualiza um professor existente"
  auth = "user"

  input {
    // ID obrigatório para identificar qual professor atualizar
    int id {
      description = "ID do professor a ser atualizado"
    }
    // Campos opcionais — apenas os enviados serão alterados
    text nome? filters=trim {
      description = "Novo nome do professor"
    }
    email email? {
      description = "Novo email do professor"
    }
    int course_id? {
      description = "Novo ID do curso"
    }
  }

  stack {
    // Busca o professor garantindo que pertence ao usuário
    // A dupla condição (id + user_id) impede editar dados de outro usuário
    db.query "professores" {
      where = ($db.professores.id == $input.id) && ($db.professores.user_id == $auth.id)
      return = {type: "single"}
    } as $existing_prof
    
    // Validação: se o professor não foi encontrado, interrompe com erro
    precondition {
      if ($existing_prof == null) {
        throw "Professor não encontrado ou acesso negado"
      }
    }

    // Atualiza o registro preservando campos não enviados
    db.edit "professores" {
      field_name = "id"
      field_value = $input.id
      data = {
        // ?? mantém o valor atual quando o campo não é enviado pelo cliente
        nome      : $input.nome      ?? $existing_prof.nome
        email     : $input.email     ?? $existing_prof.email
        course_id : $input.course_id ?? $existing_prof.course_id
      }
    } as $updated_prof
  }

  // Retorna o professor com os dados atualizados
  response = $updated_prof
}
