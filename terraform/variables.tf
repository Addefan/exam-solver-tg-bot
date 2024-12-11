variable "cloud_id" {
  type        = string
  description = "Идентификатор облака по умолчанию"
}

variable "folder_id" {
  type        = string
  description = "Идентификатор каталога по умолчанию"
}

variable "sa_key_file_path" {
  type        = string
  default     = "~/.yc-keys/key.json"
  description = "Путь к ключу сервисного аккаунта с ролью admin"
}

variable "tg_bot_key" {
  type = string
  description = "Токен telegram-бота"
}
