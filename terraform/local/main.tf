variable "app_image" {
  type        = string
  description = "Local image name for the FastAPI service."
  default     = "infra-lab:local"
}

resource "docker_network" "backend" {
  name = "infra-lab-backend"
}

resource "docker_volume" "postgres_data" {
  name = "infra-lab-postgres-data"
}

resource "docker_image" "app" {
  name = var.app_image
  build {
    context    = "../.."
    dockerfile = "docker/Dockerfile"
  }
}

resource "docker_container" "db" {
  name  = "infra-lab-db"
  image = "postgres:16.6-alpine"
  env = [
    "POSTGRES_DB=infra_lab",
    "POSTGRES_USER=infra",
    "POSTGRES_PASSWORD=infra_password",
  ]
  networks_advanced {
    name = docker_network.backend.name
  }
  volumes {
    volume_name    = docker_volume.postgres_data.name
    container_path = "/var/lib/postgresql/data"
  }
  healthcheck {
    test     = ["CMD-SHELL", "pg_isready -U infra -d infra_lab"]
    interval = "5s"
    timeout  = "5s"
    retries  = 10
  }
}

resource "docker_container" "app" {
  name  = "infra-lab-app"
  image = docker_image.app.image_id
  env = [
    "APP_ENV=development",
    "DATABASE_URL=postgresql+psycopg://infra:infra_password@${docker_container.db.name}:5432/infra_lab",
  ]
  command = ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
  ports {
    internal = 8000
    external = 8000
  }
  networks_advanced {
    name = docker_network.backend.name
  }
  depends_on = [docker_container.db]
  restart    = "unless-stopped"
}

output "app_url" {
  value = "http://localhost:8000"
}
