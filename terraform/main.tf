terraform {
    backend "s3" {
        bucket = "voice-gram"
        key = "terraform.tfstate"
        region = "eu-west-1"
        profile = "default"
        workspace_key_prefix = "terraform"
    }

    required_providers {
        aws = {
            source = "hashicorp/aws",
            version = "3.26.0"
        }
        archive = {
            source = "hashicorp/archive"
            version = "2.0.0"
        }
    }
}

provider "aws" {
    profile = "default"
    region = var.REGION
}

module "aws" {
    source = "./modules/aws"

    PROJECT_NAME = var.PROJECT_NAME
    ALEXA_ID = var.ALEXA_ID
    ALEXA_SECRET = var.ALEXA_SECRET
    TG_ID = var.TG_ID
    TG_SECRET = var.TG_SECRET
    TG_TOKEN = var.TG_TOKEN
    SKILL_ID = var.SKILL_ID
    REGION = var.REGION
    ALEXA_USER_ID = var.ALEXA_USER_ID
    ENDPOINT = var.ENDPOINT
    LOCALE = var.LOCALE
}
