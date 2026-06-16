// =============================================================
// apis/.../patch_courses.xs — PATCH /curso/{curso_id}
// =============================================================
// Endpoint que atualiza um curso existente do aluno autenticado.
//
// Método HTTP: PATCH (atualização parcial de recurso)
// Autenticação: obrigatória (token JWT no cabeçalho)
//
// Fluxo com segurança (Authorization Check):
//   1. Recebe o ID do curso e os novos dados
//   2. Busca o curso no banco de dados
//   3. VERIFICA se o curso pertence ao usuário logado (precondition)
//   4. Se sim, atualiza; se não, retorna erro de permissão
//
// O passo 3 é essencial para evitar que um usuário edite
// cursos de outro usuário (Broken Object Level Authorization - BOLA)
// =============================================================
// A rota usa {curso_id} como parâmetro de caminho (path parameter)
// Exemplo: PATCH /curso/42 → atualiza o curso com ID 42
query "curso/{curso_id}" verb=PATCH {
  description = "Atualiza o nome de um curso pertencente ao aluno autenticado"
  auth = "user"

  // Bloco de inputs
  input {
    // ID do curso a ser atualizado — capturado automaticamente da URL
    int curso_id {
      description = "ID do curso a ser atualizado"
    }

    // Nome atualizado — campo opcional (marcado com ?)
    // Se não enviado, o campo não será alterado
    text name? filters=trim {
      description = "Novo nome do curso ou instituição"
    }
  }

  // Bloco stack: operações executadas em sequência
  stack {
    // Verifica se o curso pertence ao aluno autenticado
    // Passo 1: Busca o curso pelo ID fornecido
    db.get "curso" {
      field_name  = "id"
      field_value = $input.curso_id
    } as $course  // Armazena o registro encontrado em $course

    // Passo 2: Verifica se o dono do curso é o usuário logado
    // precondition: se a condição for FALSA, o Xano lança o erro definido
    precondition ($course.user_id == $auth.id) {
      description = "Garante que o curso pertence ao aluno autenticado"
      // error_type "accessdenied" → HTTP 403 Forbidden
      error_type = "accessdenied"
      error = "Você não tem permissão para editar este curso."
    }

    // Passo 3: Atualiza apenas os campos enviados pelo cliente
    db.patch "curso" {
      field_name  = "id"
      field_value = $input.curso_id
      data = {
        name: $input.name
      }
    } as $updated_course  // Armazena o registro atualizado
  }

  // Retorna o curso com os dados atualizados
  response = $updated_course
}
