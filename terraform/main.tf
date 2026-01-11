terraform {
  required_version = ">= 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.57"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location

  tags = {
    Environment = "Production"
    Application = "Operations Dashboard"
  }
}

# PostgreSQL Flexible Server
resource "azurerm_postgresql_flexible_server" "main" {
  name                   = "psql-${replace(var.resource_group_name, "rg-", "")}-${random_string.suffix.result}"
  resource_group_name    = azurerm_resource_group.main.name
  location               = azurerm_resource_group.main.location
  version                = "15"
  delegated_subnet_id    = azurerm_subnet.postgres.id
  private_dns_zone_id    = azurerm_private_dns_zone.postgres.id
  administrator_login    = var.postgres_admin_username
  administrator_password = var.postgres_admin_password
  zone                   = "1"

  storage_mb = 32768
  sku_name   = "GP_Standard_D2s_v3"

  backup_retention_days        = 7
  geo_redundant_backup_enabled = false

  depends_on = [azurerm_private_dns_zone_virtual_network_link.postgres]

  tags = {
    Environment = "Production"
    Application = "Operations Dashboard"
  }
}

# PostgreSQL Database
resource "azurerm_postgresql_flexible_server_database" "main" {
  name      = "operationsdb"
  server_id = azurerm_postgresql_flexible_server.main.id
  collation = "en_US.utf8"
  charset   = "utf8"
}

# Network setup for PostgreSQL
resource "azurerm_virtual_network" "main" {
  name                = "vnet-${replace(var.resource_group_name, "rg-", "")}"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}

resource "azurerm_subnet" "postgres" {
  name                 = "subnet-postgres"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]
  service_endpoints    = ["Microsoft.Storage"]

  delegation {
    name = "fs"
    service_delegation {
      name = "Microsoft.DBforPostgreSQL/flexibleServers"
      actions = [
        "Microsoft.Network/virtualNetworks/subnets/join/action",
      ]
    }
  }
}

resource "azurerm_private_dns_zone" "postgres" {
  name                = "${replace(var.resource_group_name, "rg-", "")}.postgres.database.azure.com"
  resource_group_name = azurerm_resource_group.main.name
}

resource "azurerm_private_dns_zone_virtual_network_link" "postgres" {
  name                  = "vnet-link"
  resource_group_name   = azurerm_resource_group.main.name
  private_dns_zone_name = azurerm_private_dns_zone.postgres.name
  virtual_network_id    = azurerm_virtual_network.main.id
}

# App Service Plan
resource "azurerm_service_plan" "main" {
  name                = "asp-${replace(var.resource_group_name, "rg-", "")}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  os_type             = "Linux"
  sku_name            = var.app_service_plan_sku

  tags = {
    Environment = "Production"
    Application = "Operations Dashboard"
  }
}

# App Service for Backend
resource "azurerm_linux_web_app" "backend" {
  name                = "app-backend-${replace(var.resource_group_name, "rg-", "")}-${random_string.suffix.result}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_service_plan.main.location
  service_plan_id     = azurerm_service_plan.main.id

  site_config {
    application_stack {
      docker_image     = "your-registry.azurecr.io/backend:latest"
      docker_image_tag = "latest"
    }

    always_on = true
  }

  app_settings = {
    "DATABASE_URL" = "postgresql://${var.postgres_admin_username}:${var.postgres_admin_password}@${azurerm_postgresql_flexible_server.main.fqdn}:5432/${azurerm_postgresql_flexible_server_database.main.name}?sslmode=require"
    "AZURE_OPENAI_ENDPOINT" = azurerm_cognitive_account.openai.endpoint
    "AZURE_OPENAI_API_KEY"  = azurerm_cognitive_account.openai.primary_access_key
    "AZURE_OPENAI_DEPLOYMENT_NAME" = var.openai_deployment_name
    "WEBSITES_PORT" = "8000"
  }

  tags = {
    Environment = "Production"
    Application = "Operations Dashboard"
  }
}

# App Service for Frontend
resource "azurerm_linux_web_app" "frontend" {
  name                = "app-frontend-${replace(var.resource_group_name, "rg-", "")}-${random_string.suffix.result}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_service_plan.main.location
  service_plan_id     = azurerm_service_plan.main.id

  site_config {
    application_stack {
      docker_image     = "your-registry.azurecr.io/frontend:latest"
      docker_image_tag = "latest"
    }

    always_on = true
  }

  app_settings = {
    "NEXT_PUBLIC_API_URL" = "https://${azurerm_linux_web_app.backend.default_hostname}"
    "NEXT_PUBLIC_AZURE_CLIENT_ID" = azurerm_user_assigned_identity.main.client_id
    "NEXT_PUBLIC_AZURE_TENANT_ID" = data.azurerm_client_config.current.tenant_id
  }

  tags = {
    Environment = "Production"
    Application = "Operations Dashboard"
  }
}

# Azure OpenAI
resource "azurerm_cognitive_account" "openai" {
  name                = "openai-${replace(var.resource_group_name, "rg-", "")}-${random_string.suffix.result}"
  location            = "East US" # OpenAI requires specific regions
  resource_group_name = azurerm_resource_group.main.name
  kind                = "OpenAI"
  sku_name            = "S0"

  tags = {
    Environment = "Production"
    Application = "Operations Dashboard"
  }
}

resource "azurerm_cognitive_deployment" "gpt4o" {
  name                 = var.openai_deployment_name
  cognitive_account_id = azurerm_cognitive_account.openai.id

  model {
    format  = "OpenAI"
    name    = "gpt-4o"
    version = "2024-02-15-preview"
  }

  scale {
    type     = "Standard"
    capacity = 10
  }
}

# Application Insights
resource "azurerm_application_insights" "main" {
  name                = "appi-${replace(var.resource_group_name, "rg-", "")}-${random_string.suffix.result}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  application_type    = "web"

  tags = {
    Environment = "Production"
    Application = "Operations Dashboard"
  }
}

# User Assigned Identity for Entra ID
resource "azurerm_user_assigned_identity" "main" {
  name                = "identity-${replace(var.resource_group_name, "rg-", "")}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
}

# Random string for unique naming
resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

# Data source for current Azure client config
data "azurerm_client_config" "current" {}
