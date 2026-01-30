\ minds/loader.fs - Brilliant Minds CLI
\
\ Command-line interface for querying minds.
\ Vocabulary provided by pkg:brilliant-minds.
\
\ Usage:
\   MINDS_CMD=count fifth minds/loader.fs
\   MINDS_CMD=list fifth minds/loader.fs
\   MINDS_CMD=domains fifth minds/loader.fs
\   MINDS_CMD=zones fifth minds/loader.fs
\   MINDS_CMD=random fifth minds/loader.fs
\   MINDS_CMD=get MINDS_ARG=claude-shannon fifth minds/loader.fs
\   MINDS_CMD=search-domain MINDS_ARG=Cryptography fifth minds/loader.fs
\   MINDS_CMD=search-zone MINDS_ARG=synthesis fifth minds/loader.fs
\   MINDS_CMD=search-era MINDS_ARG=1943 fifth minds/loader.fs

require ~/.fifth/lib/pkg.fs
use pkg:brilliant-minds

\ ============================================================
\ CLI dispatch
\ ============================================================

: minds-arg ( -- addr u )
  s" MINDS_ARG" getenv dup 0= if 2drop s" " then ;

: minds-usage ( -- )
  ." Brilliant Minds Loader (Fifth)" cr
  ." MINDS_CMD: count list domains zones random get search-domain search-zone search-era" cr ;

: minds-cli ( -- )
  s" MINDS_CMD" getenv
  dup 0= if 2drop minds-usage bye then
  2dup s" count" str= if 2drop mind-count . cr bye then
  2dup s" list" str= if 2drop mind-list bye then
  2dup s" domains" str= if 2drop mind-domains bye then
  2dup s" zones" str= if 2drop mind-zones bye then
  2dup s" random" str= if 2drop mind-random bye then
  2dup s" get" str= if 2drop minds-arg mind-get bye then
  2dup s" search-domain" str= if 2drop minds-arg mind-search-domain bye then
  2dup s" search-zone" str= if 2drop minds-arg mind-search-zone bye then
  2dup s" search-era" str= if 2drop minds-arg mind-search-era bye then
  ." Unknown: " type cr minds-usage bye ;

minds-cli
