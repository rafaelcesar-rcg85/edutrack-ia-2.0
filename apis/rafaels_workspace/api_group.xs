// =============================================================
// apis/rafaels_workspace/api_group.xs — Grupo de APIs
// =============================================================
// Este arquivo define o GRUPO ao qual todos os endpoints
// deste diretório pertencem.
//
// No Xano, um API Group é como uma "pasta" de endpoints —
// todos os arquivos .xs neste diretório fazem parte do grupo
// "Rafael's Workspace".
//
// O campo "canonical" é o identificador único interno do Xano
// para sincronização entre o código local e o backend na nuvem.
// =============================================================

// Define o grupo de APIs "Rafael's Workspace"
api_group "Rafael's Workspace" {
  // Identificador canônico gerado pelo Xano — não altere manualmente
  canonical = "tBID7vZq"
}