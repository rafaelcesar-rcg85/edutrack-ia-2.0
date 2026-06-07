// =============================================================
// apis/.../post_professores.xs — POST /professores
// =============================================================
// Endpoint que cria um novo professor para o aluno autenticado.
//
// Método HTTP: POST (criação)
// Autenticação: obrigatória (token JWT)
//
// Um professor exige:
//   - nome: nome completo do professor (obrigatório)
//   - email: e-mail de contato (opcional)
//   - course_id: curso ao qual está vinculado (obrigatório)
//
// O campo user_id é preenchido automaticamente pelo Xano
// usando $auth.id do token JWT — garantindo isolamento entre usuários.
// =============================================================

// Cria um novo professor vinculado a um curso e usuário
query "professores" verb=POST {
  description = "Cria um novo professor vinculado a um curso e usuário"
  auth = "user"

  input {
    // Nome do professor — obrigatório
    // filters=trim: remove espaços extras automáticamente
    text nome filters=trim {
      description = "Nome do professor"
    }
    // E-mail do professor — opcional (marcado com ?)
    // O tipo "email" faz validação básica de formato de e-mail
    email email? {
      description = "Email do professor"
    }
    // ID do curso ao qual o professor está vinculado
    int course_id {
      description = "ID do curso"
    }
  }

  stack {
    // db.add: insere um novo registro na tabela "professores"
    db.add "professores" {
      data = {
        // Vincula automaticamente ao usuário logado via token JWT
        user_id   : $auth.id
        course_id : $input.course_id
        nome      : $input.nome
        email     : $input.email
        // Registra o momento da criação
        created_at: "now"
      }
    } as $new_prof  // Variável com o objeto do professor recém-criado
  }

  // Retorna o professor criado (incluindo o ID gerado automaticamente pelo banco)
  response = $new_prof
}
