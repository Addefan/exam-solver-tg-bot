resource "yandex_function" "exam_solver_tg_bot" {
  name               = "exam-solver-tg-bot"
  description        = <<EOT
                       Функция, которая получает текстовые сообщения
                       и сообщения с фото, отправленные telegram-боту,
                       и отправляет ответы на вопросы с них от YandexGPT
                       EOT
  entrypoint         = "index.handler"
  memory             = "128"
  runtime            = "python312"
  service_account_id = yandex_iam_service_account.sa_exam_solver_tg_bot.id
  user_hash          = data.archive_file.content.output_sha512
  execution_timeout  = "30"
  environment        = {
    TELEGRAM_BOT_TOKEN = var.tg_bot_key
    FOLDER_ID          = var.folder_id
  }
  content {
    zip_filename = data.archive_file.content.output_path
  }
}

resource "yandex_function_iam_binding" "exam_solver_tg_bot_iam" {
  function_id = yandex_function.exam_solver_tg_bot.id
  role        = "functions.functionInvoker"
  members     = [
    "system:allUsers",
  ]
}

resource "telegram_bot_webhook" "exam_solver_tg_bot_webhook" {
  url = "https://functions.yandexcloud.net/${yandex_function.exam_solver_tg_bot.id}"
}

resource "yandex_storage_bucket" "exam_solver_tg_bot_bucket" {
  bucket = var.bucket_name
}

resource "yandex_storage_object" "yandexgpt_instruction" {
  bucket  = yandex_storage_bucket.exam_solver_tg_bot_bucket.id
  key     = var.bucket_object_key
  content = <<EOT
            Ты являешься преподавателем по дисциплине "Операционные системы".
            Ты проводишь экзамен по своей дисциплине и выдаёшь билеты,
            в каждом из которых написаны два вопроса, на которые нужно дать ответ
            (они пронумерованы соответственно 1 и 2). Предоставь такие ответы,
            которые ты ожидаешь получить от ученика, то есть ответы, за которые
            ты поставишь максимально возможный балл.
            EOT
}

resource "yandex_iam_service_account" "sa_exam_solver_tg_bot" {
  name = "sa-exam-solver-tg-bot"
}

resource "yandex_resourcemanager_folder_iam_member" "sa_exam_solver_tg_bot_ai_vision_iam" {
  folder_id = var.folder_id
  role      = "ai.vision.user"
  member    = "serviceAccount:${yandex_iam_service_account.sa_exam_solver_tg_bot.id}"
}

resource "yandex_resourcemanager_folder_iam_member" "sa_exam_solver_tg_bot_ai_language_models_iam" {
  folder_id = var.folder_id
  role      = "ai.languageModels.user"
  member    = "serviceAccount:${yandex_iam_service_account.sa_exam_solver_tg_bot.id}"
}

resource "yandex_resourcemanager_folder_iam_member" "sa_exam_solver_tg_bot_storage_viewer_iam" {
  folder_id = var.folder_id
  role      = "storage.viewer"
  member    = "serviceAccount:${yandex_iam_service_account.sa_exam_solver_tg_bot.id}"
}
