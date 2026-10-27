UNAME_M    := $(shell uname -m)
FIFTH_HOME ?= $(HOME)/.fifth
DEST       := $(FIFTH_HOME)/packages/brilliant-minds

# Default: POSIX shell installer. No Fifth interpreter, no assembler.
install:
	@./install.sh

# Same result via the Fifth installer (requires the `fifth` interpreter).
install-fifth:
	@if [ -f "$(DEST)/package.fs" ] && diff -q pkg/package.fs "$(DEST)/package.fs" >/dev/null 2>&1; then \
		printf '\033[32m✓ brilliant-minds already installed at %s\033[0m\n' "$(DEST)"; \
	else \
		fifth install.fs > /dev/null && \
		printf '\033[32m✓ brilliant-minds installed to %s\033[0m\n' "$(DEST)"; \
	fi

# Same result via the AArch64 assembly installer (aarch64 only, needs as/ld).
install-asm: install.s
ifeq ($(UNAME_M),aarch64)
	@as -o install.o install.s && \
		ld -o install install.o && \
		rm -f install.o && \
		./install > /dev/null && \
		printf '\033[32m✓ brilliant-minds installed to %s\033[0m\n' "$(DEST)"
else
	@echo "install-asm requires aarch64 (this is $(UNAME_M)); use 'make install'" >&2; exit 1
endif

clean:
	rm -f install.o

.PHONY: install install-fifth install-asm clean
