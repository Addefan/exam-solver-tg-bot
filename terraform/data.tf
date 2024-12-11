data "archive_file" "content" {
  type        = "zip"
  source_dir  = "../src"
  output_path = "../build/content.zip"
}
