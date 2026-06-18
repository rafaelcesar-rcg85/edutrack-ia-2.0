// =============================================================
// apis/.../post_courses.xs — POST /curso
// =============================================================
// Endpoint que cria um novo curso para o aluno autenticado.
//
// Método HTTP: POST (criação de recurso)
// Autenticação: obrigatória (token JWT no cabeçalho)
//
// Fluxo:
//   1. O cliente envia o nome do curso no corpo da requisição (JSON)
//   2. O Xano valida o token e extrai $auth.id (ID do usuário)
//   3. O banco insere o novo registro vinculando ao usuário logado
//   4. Retorna o registro recém-criado com seu ID gerado
// =============================================================
// Declara o endpoint POST na rota "/curso"
query "curso" verb=POST {
  description = "Cria um novo curso vinculado ao aluno autenticado"
  // auth = "user": exige token JWT válido para identificar o dono do novo curso
  auth = "user"

  // Bloco de inputs: campos obrigatórios e opcionais enviados pelo cliente
  input {
    // Campo "name" do tipo texto
    // filters=trim: remove espaços em branco no início e no final automaticamente
    text name filters=trim {
      description = "Nome do curso ou instituição"
    }
  }

  // Bloco stack: operações executadas no servidor
  stack {
    // db.add: insere um novo registro na tabela "curso"
    db.add "curso" {
      // data: objeto com os campos a serem inseridos no banco
      data = {
        // Vincula o curso ao usuário autenticado via $auth.id (token JWT)
        user_id   : $auth.id
        // Pega o nome enviado pelo cliente via $input.name
        name      : $input.name
        // "now" é uma expressão do Xano que gera o timestamp atual automaticamente
        created_at: "now"
      }
    } as $new_curso  // Salva o registro criado na variável $new_course
  }

  // Retorna o objeto completo do curso recém-criado (incluindo o ID gerado)
  response = $new_curso
}
