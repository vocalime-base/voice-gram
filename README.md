<h1 align="center">Welcome to voice-gram 👋</h1>
<p>
  <img alt="Version" src="https://img.shields.io/badge/version-1.0.0-blue.svg?cacheSeconds=2592000" />
  <a href="https://github.com/vocalime-base/voice-gram" target="_blank">
    <img alt="Documentation" src="https://img.shields.io/badge/documentation-yes-brightgreen.svg" />
  </a>
  <a href="https://github.com/vocalime-base/voice-gram/blob/main/LICENSE" target="_blank">
    <img alt="License: GNU General Public License v3.0" src="https://img.shields.io/badge/License-GNU General Public License v3.0-yellow.svg" />
  </a>
</p>

> Unofficial Telegram client for Alexa

### 🏠 [Homepage](https://github.com/vocalime-base/voice-gram)

## Usage

### Telegram

- Create a Telegram app [here](https://my.telegram.org/) and copy `api_id` and `api_hash` to `scripts/config.ini` and `terraform/secret.auto.tfvars`
- Get Telegram Token running `scripts/getTelegramToken.py`. Follow the instructions, then copy the token to `terraform/secret.auto.tfvars`.

### Alexa

- Create Alexa Skill on the [developer console](https://developer.amazon.com/alexa/console/ask).
- Get Alexa client ID and secret from the bottom of the skill's permission page, then copy the values to `terraform/secret.auto.tfvars`.
- Get Alexa User ID, locale, endpoint and skill ID from the test page of your skill. Make a sample request and find those values and copy them to then copy the token to `terraform/secret.auto.tfvars`.

### AWS

- Import [FFMPEG layer](https://serverlessrepo.aws.amazon.com/applications/arn:aws:serverlessrepo:us-east-1:145266761615:applications~ffmpeg-lambda-layer) in your AWS account.
- Build the layer containing the libraries using [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-getting-started.html).
  So, run `sam build --use-container` and wait it finishes building the layer. You also need [Docker](https://www.docker.com/).
- Finally, install [Terraform CLI](https://www.terraform.io/downloads.html) and configure your AWS CLI account.
Then you can run `terraform apply` in order to deploy the infrastructure and copy the lambda function ARN.

Now, open `skill/skill-package/skill.json` and set `manifest.events.endpoint.uri` and `manifest.apis.custom.endpoint.uri` to the function ARN just copied.
Push skill's manifest and model using [ASK CLI](https://developer.amazon.com/en-US/docs/alexa/smapi/ask-cli-intro.html) and enable the notification from Alexa App (you can find your newly created skill in More -> Skill & Games -> Your skills -> Developer).

## Supported Languages

- Italian (IT-it)

To contribute, fork this repository and add `skill/lambda/skill/locales/LOCALE.json` (dialogues) and `skill/skill-package/interactionModels/custom/LOCALE.json` (model) where `LOCALE` is the language code (IT-it, EN-us, etc).

## Author

👤 **Vocalime**

* Website: www.vocalime.com
* Github: [@vocalime-base](https://github.com/vocalime-base)
* LinkedIn: [@vocalime](https://www.linkedin.com/company/vocalime/)

## 🤝 Contributing

Contributions, issues and feature requests are welcome!<br />Feel free to check [issues page](https://github.com/vocalime-base/voice-gram/issues). 

## Show your support

Give a ⭐️ if this project helped you!

## 📝 License

Copyright © 2021 [Vocalime](https://github.com/vocalime-base).

This project is [GNU General Public License v3.0](https://github.com/vocalime-base/voice-gram/blob/main/LICENSE) licensed.
