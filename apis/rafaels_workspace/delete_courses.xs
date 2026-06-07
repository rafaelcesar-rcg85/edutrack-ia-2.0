// =============================================================
// apis/.../delete_courses.xs — DELETE /courses/{courses_id}
// =============================================================
// Endpoint que remove um curso do aluno autenticado.
//
// Método HTTP: DELETE (remoção de recurso)
// Autenticação: obrigatória (token JWT no cabeçalho)
//
// Fluxo com verificação de propriedade:
//   1. Recebe o ID do curso pela URL
//   2. Busca o curso no banco
//   3. Verifica se pertence ao usuário logado (precondition)
//   4. Se sim, deleta; se não, retorna 403 Forbidden
//
// ATENÇÃO: A exclusão é permanente. Dados filhos (disciplinas,
// tarefas) vinculados a este curso podem ficar órfãos.
// =============================================================

// DELETE /courses/{courses_id} — ex: DELETE /courses/42
query "courses/{courses_id}" verb=DELETE {
  description = "Remove um curso pertencente ao aluno autenticado"
  auth = "user"

  input {
    // ID do curso capturado do caminho da URL (path parameter)
    int courses_id {
      description = "ID do curso a ser removido"
    }
  }

  stack {
    // Verifica se o curso pertence ao aluno autenticado
    // Passo 1: Busca o registro pelo ID
    db.get "courses" {
      field_name  = "id"
      field_value = $input.courses_id
    } as $course

    // Passo 2: Valida a propriedade — o user_id do curso deve ser igual ao $auth.id
    // Se a condição for falsa, o endpoint retorna erro 403 e para a execução
    precondition ($course.user_id == $auth.id) {
      description = "Garante que o curso pertence ao aluno autenticado"
      error_type  = "accessdenied"
      error       = "Você não tem permissão para remover este curso."
    }

    // Passo 3: Remove o registro do banco de dados permanentemente
    db.del "courses" {
      field_name  = "id"
      field_value = $input.courses_id
    }
  }

  // DELETE bem-sucedido retorna objeto vazio {} com status HTTP 200
  response = {}
}
