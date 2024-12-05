terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
  }
  required_version = ">= 0.13"
}

provider "yandex" {
  cloud_id                 = "b1g71e95h51okii30p25"
  folder_id                = "b1g8jbmpoi5g1ppb4dvt"
  zone                     = "ru-central1-a"
  service_account_key_file = "~/.yc-keys/key.json"
}
