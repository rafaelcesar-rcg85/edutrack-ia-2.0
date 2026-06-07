query "user_email/{id}" verb=PATCH {
  description = "Updates the email of a user. Requires admin authentication."
  auth = "user"

  input {
    int id {
      description = "User ID to update"
    }
    email email {
      description = "New email for the user"
    }
  }

  stack {
    db.get "user" {
      field_name = "id"
      field_value = $auth.id
    } as $current_user
    
    precondition ($current_user.role == "admin") {
      error_type = "accessdenied"
      error = "Unauthorized: You do not have admin privileges."
    }
    
    db.patch "user" {
      field_name = "id"
      field_value = $input.id
      data = {
        email: $input.email
      }
    } as $updated_user
  }
  
  response = $updated_user
}
