.PHONY: help quickstart init configure auth install-ui ui-status ui-logs start stop restart refresh status logs doctor uninstall

help:
	@echo "Targets:"
	@echo "  make quickstart   # guided setup"
	@echo "  make init         # init venv/config/service"
	@echo "  make configure    # write credentials config"
	@echo "  make auth         # run interactive 2FA bootstrap"
	@echo "  make install-ui   # build/install KDE Plasma integration"
	@echo "  make ui-status    # show Plasma backend status"
	@echo "  make ui-logs      # follow Plasma backend logs"
	@echo "  make start|stop|restart|refresh|status|logs|doctor|uninstall"
quickstart:
	./icloudctl quickstart

init:
	./icloudctl init

configure:
	./icloudctl configure

auth:
	./icloudctl auth

start:
	./icloudctl start

stop:
	./icloudctl stop

restart:
	./icloudctl restart

refresh:
	./icloudctl refresh

status:
	./icloudctl status

logs:
	./icloudctl logs

doctor:
	./icloudctl doctor

uninstall:
	./icloudctl uninstall

install-ui:
	./icloudctl install-ui

ui-status:
	./icloudctl ui-status

ui-logs:
	./icloudctl ui-logs
