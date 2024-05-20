export GOOGLE_IDP_ID=00000#DNX IDP
export GOOGLE_SP_ID=0000#DNX ID

ASSUME_REQUIRED?=.env.assume

export PATH_DEPLOY=.deploy
export PATH_TEST=test
export AWS_DEFAULT_REGION?=us-east-1

env-%:
	@ if [ "${${*}}" = "" ]; then \
		echo "Environment variable $* not set"; \
		exit 1; \
	fi

.env:
	@echo "make .env"
	cp $(PATH_DEPLOY)/.env.template $(PATH_DEPLOY)/.env
	cat $(PATH_DEPLOY)/.env.ci.template >> $(PATH_DEPLOY)/.env
	echo >> $(PATH_DEPLOY)/.env
	touch $(PATH_DEPLOY)/.env.assume
	touch $(PATH_DEPLOY)/.env.auth

.env.auth: .env env-GOOGLE_IDP_ID env-GOOGLE_SP_ID
	@echo "make .env.auth"
	echo > $(PATH_DEPLOY)/.env.auth
	echo > $(PATH_DEPLOY)/.env.assume
	docker-compose -f $(PATH_DEPLOY)/docker-compose.yml run --rm google-auth

.env.assume: .env env-AWS_ACCOUNT_ID env-AWS_ROLE
	@echo "make .env.assume"
	echo > $(PATH_DEPLOY)/.env.assume
	docker-compose -f $(PATH_DEPLOY)/docker-compose.yml pull aws
	docker-compose -f $(PATH_DEPLOY)/docker-compose.yml run --rm aws \
		assume-role.sh > $(PATH_DEPLOY)/.env.assume
.PHONY: assumeRole

create-env: .env
	@echo "make create-env"
	docker-compose -f $(PATH_DEPLOY)/docker-compose.yml run --rm serverless \
		"python3 -m venv .venv"
.PHONY: create-env

install-local: .env create-env
	@echo "make install-local"
	docker-compose -f $(PATH_DEPLOY)/docker-compose.yml run --rm serverless \
		"source .venv/bin/activate && pip3 install -r requirements.txt"
.PHONY: install

install-layer: .env
	@echo "make install-layer"
	docker-compose -f $(PATH_DEPLOY)/docker-compose.yml run --rm serverless \
		"pip3 install -t src/layer/pip/python/ -r src/layer/requirements.txt"
.PHONY: install-layer

install-sls-plugins: .env
    #Plugin is hard-coded as SLS does not provide a fetaure to install all plugins based on serverless.yml configuraton - https://github.com/serverless/serverless/issues/3930
	@echo "install-sls-plugins"
	docker-compose -f $(PATH_DEPLOY)/docker-compose.yml run --rm serverless \
		"serverless plugin install --name serverless-add-api-key"
.PHONY: install-sls-plugins


deploy: $(ASSUME_REQUIRED) env-AWS_ACCOUNT_ID env-AWS_ROLE env-AWS_ENV
	@echo "make deploy"
	docker-compose -f $(PATH_DEPLOY)/docker-compose.yml run --rm serverless \
		"sls deploy --conceal"
.PHONY: deploy

shell-aws: $(ASSUME_REQUIRED)
	docker run \
		--env-file $(PATH_DEPLOY)/.env \
		--env-file $(PATH_DEPLOY)/.env.auth \
		--env-file $(PATH_DEPLOY)/.env.assume \
		-it --entrypoint "sh" dnxsolutions/aws:1.4.1

shell-sls: $(ASSUME_REQUIRED) create-env install-local
	@echo "make shell-sls"
	docker-compose -f $(PATH_DEPLOY)/docker-compose.yml run --rm serverless \
	"source .venv/bin/activate && /bin/bash"
.PHONY: shell-sls

unit-testing: create-env install-local
	@echo "make unit-testing"
	docker-compose -f $(PATH_DEPLOY)/docker-compose.yml run --rm serverless \
		"source .venv/bin/activate && \
		pip3 install -r requirements.txt && \
		python3 -m pytest $(PATH_TEST)/unit/test_*_unit.py --ignore=src"
.PHONY: unit-testing

service-testing: $(ASSUME_REQUIRED) create-env install-local
	@echo "make service-testing"
	docker-compose -f $(PATH_DEPLOY)/docker-compose.yml run --rm serverless \
		"source .venv/bin/activate && \
		pip3 install -r requirements.txt && \
		cp test/service/test_*_service.py . && \
		python3 -m pytest $(PATH_TEST)/service/test_*_service.py --ignore=src && \
		rm test_*_service.py"
.PHONY: service-testing

ui-testing: create-env install-local
	@echo "make ui-testing"
	docker-compose -f $(PATH_DEPLOY)/docker-compose.yml run --rm serverless \
		"source .venv/bin/activate && \
		pip3 install -r requirements.txt && \
		python3 -m pytest $(PATH_TEST)/ui/test_*_ui.py --ignore=src"
.PHONY: ui-testing