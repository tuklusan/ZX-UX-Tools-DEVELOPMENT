# rfc Forth-83 coverage

Target: the Forth-83 Required Word Set, as a one-pass cross-compiler for ZX-UX
(true flag = -1; `/ mod /mod` are floored; `um*`/`um/mod` unsigned, `*/ */mod`
built on them). Programs compile to a native indirect-threaded `.ssx`.

## Implemented and tested
- Stack: `dup drop swap over rot nip ?dup 2dup 2drop 2swap 2over pick roll depth`
- Return stack: `>r r> r@`
- Arithmetic: `+ - * / mod /mod negate abs min max 1+ 1- 2+ 2- 2* 2/ um* um/mod */ */mod d+ d- d0= d= du<`
- Compare: `= <> < > 0= 0< 0> u<`   Logic: `and or xor invert`
- Memory: `@ ! c@ c! +! 2@ 2! fill cmove cmove> move-via-cmove`
- Numbers / I/O: `. u. .r u.r <# # #s #> hold sign  base hex decimal  emit cr space spaces type key count -trailing  ." `
- Control: `if else then  begin until again  begin while repeat  do loop +loop leave i j exit recurse`
- Defining: `: ;  variable 2variable constant create ... ( , c, allot cells )  cells cell+`
- Reflection: `' ['] execute  char [char]`
- Misc: `bye`

Verified end to end on `rvm` (see ../../tests/test_rfc.py and the recursive
`assets/forth-src/**/*.fth` corpus).

## Not applicable to a batch cross-compiler (no resident interpreter)
These Forth-83 words assume an interactive text interpreter, which this
compiler does not host: `does> literal [ ] immediate [compile] compile
interpret quit expect query forget`.

The batch target does provide a runtime dictionary and input-buffer primitives
(`find`, `word`, `number?`, `tib`, `#tib`, `>in`, `span`, `state`, `here`, `,`,
`c,`, and `allot`) for compiled programs and adapters.  `'`, `[']`, `char`,
`[char]`, and `create` initialisers are compile-time facilities; `array` and
`2array` are static-table compatibility helpers.

## Known limitations
- Division by zero is not guarded (undefined).
- `i`/`j` read the return stack directly: do not place an unbalanced `>r` before
  them inside a loop.
- `do` with limit == start iterates 65536 times; use `?do` when the empty-loop
  case must be skipped.
- `(` and `\` comments require a trailing space after the comment word.

## Cross-compiler compatibility helpers
- `n array name` and `n 2array name` reserve static tables; `index name`
  leaves the element address. They cover the common F83 `CREATE ... DOES>`
  table idiom without a resident compiler on the target.
