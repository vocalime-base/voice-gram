locals {
    tags = {
        skill = "voice-gram"
    }

    functions = [
        "skill",
        "notification",
        "layer"
    ]
}

variable "REGION" {
  default = "eu-west-1"
}

variable "PROJECT_NAME" {
    type = string
    default = "voice-gram"
}

variable "TG_ID" {
    type = number
}

variable "TG_SECRET" {
    type = string
}

variable "TG_TOKEN" {
    type = string
}

variable "ALEXA_ID" {
    type = string
}

variable "ALEXA_SECRET" {
    type = string
}

variable "ALEXA_USER_ID" {
    type = string
}

variable "ENDPOINT" {
    type = string
}

variable "LOCALE" {
    type = string
}

variable "SKILL_ID" {
    type = string
}