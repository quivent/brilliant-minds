\ install.fs - Brilliant Minds installs itself
\
\ After installing Fifth:
\   git clone git@github.com:quivent/brilliant-minds.git
\   cd brilliant-minds
\   fifth install.fs
\
\ Copies the package into ~/.fifth/packages/brilliant-minds/
\ so any Fifth program can: use pkg:brilliant-minds

require ~/.fifth/lib/str.fs

\ ============================================================
\ Package destination (dedicated buffer — survives str-reset)
\ ============================================================

512 constant dest-max
create dest-buf dest-max allot
variable dest-len

: dest-init ( -- )
  s" FIFTH_HOME" getenv dup 0> if
    dup dest-len ! dest-buf swap move
  else
    2drop
    s" HOME" getenv dup 0= if 2drop s" /tmp" then
    dup dest-len ! dest-buf swap move
    s" /.fifth"
    dest-buf dest-len @ + swap dup dest-len +! move
  then
  s" /packages/brilliant-minds"
  dest-buf dest-len @ + swap dup dest-len +! move ;

dest-init

: dest$ ( -- addr u ) dest-buf dest-len @ ;

\ Capture PWD into its own buffer before system calls clobber it
256 constant cwd-max
create cwd-buf cwd-max allot
variable cwd-len

: cwd-init ( -- )
  s" PWD" getenv dup 0= if 2drop s" ." then
  dup cwd-len ! cwd-buf swap move ;

cwd-init

: cwd$ ( -- addr u ) cwd-buf cwd-len @ ;

\ ============================================================
\ Install
\ ============================================================

cr
." Brilliant Minds — installing package" cr
cr

\ 1. Create package directory
str-reset s" mkdir -p " str+ dest$ str+ str$ system

\ 2. Copy package.fs
str-reset s" cp pkg/package.fs " str+ dest$ str+ s" /package.fs" str+ str$ system

\ 3. Write root.txt so package can find agents.db
str-reset s" printf '%s' '" str+ cwd$ str+ s" ' > " str+ dest$ str+ s" /root.txt" str+ str$ system

." Installed to: " dest$ type cr
." Root stored:  " cwd$ type cr
cr
." Any Fifth program can now:" cr
."   use pkg:brilliant-minds" cr
."   mind-count . cr" cr
cr
." CLI:" cr
."   MINDS_CMD=count fifth minds/loader.fs" cr
cr

bye
