query "users" verb=GET {
  description = "Returns a list of all users, requires admin authentication"
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
    
    db.query "user" {
    } as $all_users
  }
  
  response = $all_users
}
