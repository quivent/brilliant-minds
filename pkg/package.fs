\ brilliant-minds/package.fs - Brilliant Minds Query Package
\ Package manifest and vocabulary
\
\ Usage:
\   use pkg:brilliant-minds
\   mind-count .               \ Print count
\   mind-list                  \ List all minds
\   mind-domains               \ List all domains
\   mind-zones                 \ Zone distribution
\   mind-random                \ Random mind
\   s" claude-shannon" mind-get            \ Get full record
\   s" Cryptography" mind-search-domain    \ Search by domain
\   s" synthesis" mind-search-zone         \ Search by zone
\   s" 1943" mind-search-era              \ Search by era

\ ============================================================
\ Package Metadata
\ ============================================================

\ Package: brilliant-minds
\ Version: 1.0.0
\ Author: Fifth Project
\ Description: Query 81 brilliant minds from agents.db
\ Depends: str, sql

\ ============================================================
\ Dependencies
\ ============================================================

use lib:str.fs
use lib:sql.fs

\ ============================================================
\ Database path (dedicated buffer — survives str-reset)
\ ============================================================

256 constant minds-db-max
create minds-db-buf minds-db-max allot
variable minds-db-len

\ Read root.txt (written by install.fs) to find the repo
: minds-root-from-file ( -- addr u flag )
  str2-reset
  fifth-home$ str2+ s" /packages/brilliant-minds/root.txt" str2+
  str2$ r/o open-file if drop 0 0 false exit then
  >r line-buf 255 r@ read-line if r> close-file drop 0 0 false exit then
  drop r> close-file drop
  line-buf swap true ;

: minds-db-init ( -- )
  s" BRILLIANT_MINDS_ROOT" getenv
  dup 0> if
    dup minds-db-len ! minds-db-buf swap move
  else
    2drop
    minds-root-from-file if
      dup minds-db-len ! minds-db-buf swap move
    else
      2drop
      1 minds-db-len ! minds-db-buf [char] . swap c!
    then
  then
  s" /db/agents.db"
  dup minds-db-len @ + minds-db-max < if
    minds-db-buf minds-db-len @ + swap dup minds-db-len +! move
  else 2drop then ;

minds-db-init

: minds-db ( -- addr u ) minds-db-buf minds-db-len @ ;

\ ============================================================
\ Static queries (string literals — no buffer collision)
\ ============================================================

: mind-count ( -- n )
  minds-db s" SELECT COUNT(*) FROM mind_metadata" sql-count ;

: mind-list ( -- )
  minds-db s" SELECT a.name, m.era, m.primary_zone FROM mind_metadata m JOIN agents a ON m.id = a.id ORDER BY a.name" sql-dump ;

: mind-domains ( -- )
  minds-db s" SELECT DISTINCT value FROM mind_metadata, json_each(mind_metadata.domains) ORDER BY value" sql-dump ;

: mind-zones ( -- )
  minds-db s" SELECT m.primary_zone, COUNT(*) FROM mind_metadata m GROUP BY m.primary_zone ORDER BY COUNT(*) DESC" sql-dump ;

: mind-random ( -- )
  minds-db s" SELECT a.name, m.era, m.primary_zone FROM mind_metadata m JOIN agents a ON m.id = a.id ORDER BY RANDOM() LIMIT 1" sql-dump ;

\ ============================================================
\ Dynamic queries (built in str2-buf, executed via sql-dump2)
\ ============================================================

: dq ( -- ) 34 str2-char ;

: mind-get ( addr u -- )
  2>r str2-reset
  s" SELECT a.id, a.name, a.role, m.era, m.domains, m.primary_zone, m.characteristics, m.teaching_style, m.file_identity, m.file_context, m.file_activation FROM mind_metadata m JOIN agents a ON m.id = a.id WHERE m.id = " str2+
  dq 2r> str2+ dq
  minds-db sql-dump2 ;

: mind-search-domain ( addr u -- )
  2>r str2-reset
  s" SELECT a.name, m.era, m.primary_zone FROM mind_metadata m JOIN agents a ON m.id = a.id WHERE m.domains LIKE " str2+
  dq s" %" str2+ 2r> str2+ s" %" str2+ dq
  s"  ORDER BY a.name" str2+
  minds-db sql-dump2 ;

: mind-search-zone ( addr u -- )
  2>r str2-reset
  s" SELECT a.name, m.era, m.primary_zone FROM mind_metadata m JOIN agents a ON m.id = a.id WHERE m.primary_zone = " str2+
  dq 2r> str2+ dq
  s"  ORDER BY a.name" str2+
  minds-db sql-dump2 ;

: mind-search-era ( addr u -- )
  2>r str2-reset
  s" SELECT a.name, m.era, m.primary_zone FROM mind_metadata m JOIN agents a ON m.id = a.id WHERE m.era LIKE " str2+
  dq s" %" str2+ 2r> str2+ s" %" str2+ dq
  s"  ORDER BY a.name" str2+
  minds-db sql-dump2 ;

\ ============================================================
\ Package Info
\ ============================================================

: .brilliant-minds ( -- )
  ." brilliant-minds 1.0.0" cr
  ." Query 81 brilliant minds from agents.db" cr
  ." " cr
  ." Words:" cr
  ."   mind-count            ( -- n )        Count of minds" cr
  ."   mind-list             ( -- )          List all minds" cr
  ."   mind-domains          ( -- )          All domains" cr
  ."   mind-zones            ( -- )          Zone distribution" cr
  ."   mind-random           ( -- )          Random mind" cr
  ."   mind-get              ( addr u -- )   Full record by ID" cr
  ."   mind-search-domain    ( addr u -- )   Search by domain" cr
  ."   mind-search-zone      ( addr u -- )   Search by zone" cr
  ."   mind-search-era       ( addr u -- )   Search by era" cr ;

.brilliant-minds
