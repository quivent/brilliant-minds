UNAME_M := $(shell uname -m)
DEST    := $(HOME)/.fifth/packages/brilliant-minds

ifeq ($(UNAME_M),aarch64)

install: install.s
	@if [ -f "$(DEST)/package.fs" ] && diff -q pkg/package.fs "$(DEST)/package.fs" >/dev/null 2>&1; then \
		printf '\033[32m✓ brilliant-minds already installed at %s\033[0m\n' "$(DEST)"; \
	else \
		as -o install.o install.s && \
		ld -o install install.o && \
		rm -f install.o && \
		./install > /dev/null && \
		printf '\033[32m✓ brilliant-minds installed to %s\033[0m\n' "$(DEST)"; \
	fi

else

install:
	@if [ -f "$(DEST)/package.fs" ] && diff -q pkg/package.fs "$(DEST)/package.fs" >/dev/null 2>&1; then \
		printf '\033[32m✓ brilliant-minds already installed at %s\033[0m\n' "$(DEST)"; \
	else \
		fifth install.fs > /dev/null && \
		printf '\033[32m✓ brilliant-minds installed to %s\033[0m\n' "$(DEST)"; \
	fi

endif

clean:
	rm -f install install.o

.PHONY: install clean
