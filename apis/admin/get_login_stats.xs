query "login_stats" verb=GET {
  description = "Returns login events from event_log. Requires admin."
  auth = "user"

  input {}

  stack {
    db.get "user" {
      field_name = "id"
      field_value = $auth.id
    } as $current_user

    precondition ($current_user.role == "admin") {
      error_type = "accessdenied"
      error = "Unauthorized: You do not have admin privileges."
    }

    // Busca todos os eventos de login do event_log
    db.query "event_log" {
      where = $db.event_log.action == "login"
      sort = {created_at: "desc"}
      return = {type: "list"}
    } as $login_events
  }

  response = $login_events
}
