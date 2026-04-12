// install.s — Brilliant Minds installer in AArch64 Linux assembly
// Equivalent to install.fs: creates ~/.fifth/packages/brilliant-minds/
// copies pkg/package.fs there, writes root.txt with cwd.
//
// Build:
//   as -o install.o install.s && ld -o install install.o
//
// Syscall ABI: x8 = syscall number, x0-x5 = args, svc #0

.equ SYS_GETCWD,   17
.equ SYS_OPENAT,   56
.equ SYS_CLOSE,    57
.equ SYS_READ,     63
.equ SYS_WRITE,    64
.equ SYS_MKDIRAT,  34
.equ SYS_EXIT,     93

.equ AT_FDCWD,     -100
.equ O_RDONLY,      0
.equ O_WRONLY,      1
.equ O_CREAT,       64
.equ O_TRUNC,       512
.equ O_WRONLY_CREAT_TRUNC, 577   // O_WRONLY | O_CREAT | O_TRUNC

.equ MODE_DIR,     0755
.equ MODE_FILE,    0644

.data

msg_banner:     .asciz "Brilliant Minds — installing package\n"
msg_installed:  .asciz "Installed to: "
msg_root:       .asciz "Root stored:  "
msg_done:       .asciz "\nAny Fifth program can now:\n  use pkg:brilliant-minds\n  mind-count . cr\n"
msg_newline:    .asciz "\n"
msg_err_home:   .asciz "error: HOME not set\n"
msg_err_read:   .asciz "error: cannot read pkg/package.fs\n"
msg_err_write:  .asciz "error: cannot write to destination\n"
src_file:       .asciz "pkg/package.fs"

seg_fifth:      .asciz "/.fifth"
seg_packages:   .asciz "/packages"
seg_bm:         .asciz "/brilliant-minds"
file_pkg:       .asciz "/package.fs"
file_root:      .asciz "/root.txt"

.bss
.align 4
home_buf:       .skip 512          // $HOME
dest_buf:       .skip 1024         // full destination path
cwd_buf:        .skip 512          // getcwd result
copy_buf:       .skip 8192         // file copy buffer
dest_len:       .skip 8
home_len:       .skip 8
cwd_len:        .skip 8

.text
.global _start

// ---- Utility: strlen ----
// x0 = pointer to null-terminated string
// returns length in x0
strlen:
    mov     x1, x0
1:  ldrb    w2, [x1], #1
    cbnz    w2, 1b
    sub     x0, x1, x0
    sub     x0, x0, #1
    ret

// ---- Utility: write string to stdout ----
// x0 = pointer, x1 = length
puts:
    mov     x2, x1              // length
    mov     x1, x0              // buffer
    mov     x0, #1              // stdout
    mov     x8, #SYS_WRITE
    svc     #0
    ret

// ---- Utility: print null-terminated string ----
// x0 = pointer
print:
    stp     x29, x30, [sp, #-16]!
    mov     x29, sp
    mov     x19, x0
    bl      strlen
    mov     x1, x0
    mov     x0, x19
    bl      puts
    ldp     x29, x30, [sp], #16
    ret

// ---- Utility: append string to dest_buf ----
// x0 = src pointer, x1 = src length
// uses dest_len
dest_append:
    adrp    x2, dest_len
    add     x2, x2, :lo12:dest_len
    ldr     x3, [x2]               // current length
    adrp    x4, dest_buf
    add     x4, x4, :lo12:dest_buf
    add     x4, x4, x3             // dest_buf + offset
    mov     x5, x1                 // count
1:  cbz     x5, 2f
    ldrb    w6, [x0], #1
    strb    w6, [x4], #1
    sub     x5, x5, #1
    b       1b
2:  add     x3, x3, x1
    str     x3, [x2]
    // null-terminate
    strb    wzr, [x4]
    ret

// ---- Utility: get env var ----
// Walks the environment block on the stack.
// x0 = var name (null-terminated), returns x0 = pointer to value or 0
// We saved the envp in x20 at _start.
getenv:
    stp     x29, x30, [sp, #-16]!
    mov     x29, sp
    mov     x9, x0                 // var name
    bl      strlen
    mov     x10, x0                // var name length
    mov     x11, x20               // envp
1:  ldr     x12, [x11], #8
    cbz     x12, 3f                // end of envp
    // compare first x10 bytes
    mov     x13, x12
    mov     x14, x9
    mov     x15, x10
2:  cbz     x15, 4f
    ldrb    w16, [x13], #1
    ldrb    w17, [x14], #1
    cmp     w16, w17
    b.ne    1b
    sub     x15, x15, #1
    b       2b
4:  // check that next char is '='
    ldrb    w16, [x13]
    cmp     w16, #'='
    b.ne    1b
    add     x0, x13, #1            // past the '='
    ldp     x29, x30, [sp], #16
    ret
3:  mov     x0, #0
    ldp     x29, x30, [sp], #16
    ret

// ---- mkdir_p: create path and all parents ----
// x0 = path (null-terminated)
mkdir_p:
    stp     x29, x30, [sp, #-16]!
    mov     x29, sp
    mov     x19, x0                // path
    // walk the string, mkdir at each '/'
    mov     x21, x19
    ldrb    w22, [x21]
    cmp     w22, #'/'
    b.ne    1f
    add     x21, x21, #1           // skip leading /
1:  ldrb    w22, [x21]
    cbz     w22, 2f                // end of string
    cmp     w22, #'/'
    b.ne    3f
    // temporarily null-terminate at this slash
    strb    wzr, [x21]
    mov     x0, #AT_FDCWD
    mov     x1, x19
    mov     x2, #MODE_DIR
    mov     x8, #SYS_MKDIRAT
    svc     #0
    // restore slash
    mov     w22, #'/'
    strb    w22, [x21]
3:  add     x21, x21, #1
    b       1b
2:  // mkdir the full path
    mov     x0, #AT_FDCWD
    mov     x1, x19
    mov     x2, #MODE_DIR
    mov     x8, #SYS_MKDIRAT
    svc     #0
    ldp     x29, x30, [sp], #16
    ret

// ---- copy_file: src path in x0, dst path in x1 ----
copy_file:
    stp     x29, x30, [sp, #-48]!
    mov     x29, sp

    // open source
    mov     x19, x1                // save dst
    mov     x1, x0
    mov     x0, #AT_FDCWD
    mov     x2, #O_RDONLY
    mov     x3, #0
    mov     x8, #SYS_OPENAT
    svc     #0
    cmp     x0, #0
    b.lt    .copy_err
    mov     x21, x0                // src fd

    // open dest
    mov     x1, x19
    mov     x0, #AT_FDCWD
    mov     x2, #O_WRONLY_CREAT_TRUNC
    mov     x3, #MODE_FILE
    mov     x8, #SYS_OPENAT
    svc     #0
    cmp     x0, #0
    b.lt    .copy_err_close_src
    mov     x22, x0                // dst fd

    // copy loop
.copy_loop:
    mov     x0, x21                // src fd
    adrp    x1, copy_buf
    add     x1, x1, :lo12:copy_buf
    mov     x2, #8192
    mov     x8, #SYS_READ
    svc     #0
    cmp     x0, #0
    b.le    .copy_done
    mov     x23, x0                // bytes read

    mov     x2, x23
    adrp    x1, copy_buf
    add     x1, x1, :lo12:copy_buf
    mov     x0, x22                // dst fd
    mov     x8, #SYS_WRITE
    svc     #0
    b       .copy_loop

.copy_done:
    mov     x0, x22
    mov     x8, #SYS_CLOSE
    svc     #0
    mov     x0, x21
    mov     x8, #SYS_CLOSE
    svc     #0
    mov     x0, #0
    ldp     x29, x30, [sp], #48
    ret

.copy_err_close_src:
    mov     x0, x21
    mov     x8, #SYS_CLOSE
    svc     #0
.copy_err:
    mov     x0, #-1
    ldp     x29, x30, [sp], #48
    ret

// ---- write_file: create file with given contents ----
// x0 = path, x1 = data, x2 = data length
write_file:
    stp     x29, x30, [sp, #-32]!
    mov     x29, sp
    mov     x19, x1                // data
    mov     x23, x2                // data len

    mov     x1, x0
    mov     x0, #AT_FDCWD
    mov     x2, #O_WRONLY_CREAT_TRUNC
    mov     x3, #MODE_FILE
    mov     x8, #SYS_OPENAT
    svc     #0
    cmp     x0, #0
    b.lt    .wf_err
    mov     x21, x0                // fd

    mov     x0, x21
    mov     x1, x19
    mov     x2, x23
    mov     x8, #SYS_WRITE
    svc     #0

    mov     x0, x21
    mov     x8, #SYS_CLOSE
    svc     #0
    mov     x0, #0
    ldp     x29, x30, [sp], #32
    ret
.wf_err:
    mov     x0, #-1
    ldp     x29, x30, [sp], #32
    ret

// ---- _start ----
_start:
    // Save envp: on AArch64 Linux, stack has [argc, argv..., NULL, envp..., NULL]
    ldr     x0, [sp]              // argc
    add     x1, sp, #8            // argv
    add     x0, x0, #1            // argc + 1 (skip argv + NULL)
    add     x20, x1, x0, lsl #3  // envp = argv + (argc+1)*8

    // Print banner
    adrp    x0, msg_banner
    add     x0, x0, :lo12:msg_banner
    bl      print

    // Get $HOME
    adrp    x0, .Lhome_str
    add     x0, x0, :lo12:.Lhome_str
    bl      getenv
    cbz     x0, .err_home
    mov     x19, x0               // HOME value

    // Store HOME length
    mov     x0, x19
    bl      strlen
    adrp    x1, home_len
    add     x1, x1, :lo12:home_len
    str     x0, [x1]

    // Build destination path: $HOME/.fifth/packages/brilliant-minds
    // Reset dest_len
    adrp    x1, dest_len
    add     x1, x1, :lo12:dest_len
    str     xzr, [x1]

    // append HOME
    mov     x0, x19
    adrp    x1, home_len
    add     x1, x1, :lo12:home_len
    ldr     x1, [x1]
    bl      dest_append

    // append /.fifth
    adrp    x0, seg_fifth
    add     x0, x0, :lo12:seg_fifth
    mov     x1, #7
    bl      dest_append

    // append /packages
    adrp    x0, seg_packages
    add     x0, x0, :lo12:seg_packages
    mov     x1, #9
    bl      dest_append

    // append /brilliant-minds
    adrp    x0, seg_bm
    add     x0, x0, :lo12:seg_bm
    mov     x1, #16
    bl      dest_append

    // mkdir -p dest
    adrp    x0, dest_buf
    add     x0, x0, :lo12:dest_buf
    bl      mkdir_p

    // Get cwd
    adrp    x0, cwd_buf
    add     x0, x0, :lo12:cwd_buf
    mov     x1, #512
    mov     x8, #SYS_GETCWD
    svc     #0
    // store cwd length
    adrp    x0, cwd_buf
    add     x0, x0, :lo12:cwd_buf
    bl      strlen
    adrp    x1, cwd_len
    add     x1, x1, :lo12:cwd_len
    str     x0, [x1]

    // Save current dest_len (we'll restore it after appending filenames)
    adrp    x24, dest_len
    add     x24, x24, :lo12:dest_len
    ldr     x25, [x24]            // base dest_len

    // Copy pkg/package.fs -> dest/package.fs
    // Append /package.fs to dest
    adrp    x0, file_pkg
    add     x0, x0, :lo12:file_pkg
    mov     x1, #11
    bl      dest_append

    adrp    x0, src_file
    add     x0, x0, :lo12:src_file
    adrp    x1, dest_buf
    add     x1, x1, :lo12:dest_buf
    bl      copy_file
    cmp     x0, #0
    b.lt    .err_read

    // Restore dest_len to base, then append /root.txt
    str     x25, [x24]
    adrp    x0, dest_buf
    add     x0, x0, :lo12:dest_buf
    strb    wzr, [x0, x25]        // null-terminate at base

    adrp    x0, file_root
    add     x0, x0, :lo12:file_root
    mov     x1, #9
    bl      dest_append

    // Write cwd to root.txt
    adrp    x0, dest_buf
    add     x0, x0, :lo12:dest_buf
    adrp    x1, cwd_buf
    add     x1, x1, :lo12:cwd_buf
    adrp    x2, cwd_len
    add     x2, x2, :lo12:cwd_len
    ldr     x2, [x2]
    bl      write_file
    cmp     x0, #0
    b.lt    .err_write

    // Print results
    adrp    x0, msg_installed
    add     x0, x0, :lo12:msg_installed
    bl      print

    // Print dest (without /root.txt suffix)
    adrp    x0, dest_buf
    add     x0, x0, :lo12:dest_buf
    strb    wzr, [x0, x25]        // cut back to base path
    bl      print

    adrp    x0, msg_newline
    add     x0, x0, :lo12:msg_newline
    bl      print

    adrp    x0, msg_root
    add     x0, x0, :lo12:msg_root
    bl      print

    adrp    x0, cwd_buf
    add     x0, x0, :lo12:cwd_buf
    bl      print

    adrp    x0, msg_done
    add     x0, x0, :lo12:msg_done
    bl      print

    // exit(0)
    mov     x0, #0
    mov     x8, #SYS_EXIT
    svc     #0

.err_home:
    adrp    x0, msg_err_home
    add     x0, x0, :lo12:msg_err_home
    bl      print
    mov     x0, #1
    mov     x8, #SYS_EXIT
    svc     #0

.err_read:
    adrp    x0, msg_err_read
    add     x0, x0, :lo12:msg_err_read
    bl      print
    mov     x0, #1
    mov     x8, #SYS_EXIT
    svc     #0

.err_write:
    adrp    x0, msg_err_write
    add     x0, x0, :lo12:msg_err_write
    bl      print
    mov     x0, #1
    mov     x8, #SYS_EXIT
    svc     #0

.Lhome_str:
    .asciz "HOME"
