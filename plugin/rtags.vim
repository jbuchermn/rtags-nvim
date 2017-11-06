"
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Guard
"

if exists('g:rtags_loaded') || &compatible
    finish
endif
let g:rtags_loaded = 1

"
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Reindex current file (including unsaved content)
" 
" Call by
"   :RTagsReindex
"

function! rtags#reindex()
    call _rtags_reindex_unsaved()
endfunction

command RTagsReindex :call rtags#reindex()

"
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Auto-Reindex functionality
" 
" Disable by adding
"   let g:rtags_enable_autoreindex = 0
" to your init.vim
"

if(!exists('g:rtags_enable_autoreindex'))
    let g:rtags_enable_autoreindex = 1
endif


function! rtags#enable_autoreindex()
    if(g:rtags_enable_autoreindex && (&ft==# 'cpp' || &ft==# 'c'))
        augroup rtags_nvim_autoreindex_group
            autocmd!
            autocmd InsertLeave * :call rtags#reindex()
            autocmd TextChanged * :call rtags#reindex()
        augroup end
    else
        augroup rtags_nvim_autoreindex_group
            autocmd!
        augroup end
    endif
endfunction

"
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Auto-Neomake functionality
"
" Useful, as RTags does not actually lint the file upon calling :Neomake
" but returns cached diagnostics which will be updated upon filesave or
" reindex
"
" Disable by adding
"   let g:rtags_enable_automake = 0
" to your init.vim
"

if(!exists('g:rtags_enable_automake'))
    let g:rtags_enable_automake = 1
endif

if(!exists('g:rtags_automake_interval'))
    let g:rtags_automake_interval = 1000
endif

function! rtags#call_automake(...)
    :Neomake
endfunction

function! rtags#start_automake_timer()
    let s:timer_id = timer_start(g:rtags_automake_interval, 'rtags#call_automake', {'repeat': -1})
endfunction

function! rtags#stop_automake_timer()
    if(exists('s:timer_id'))
        call timer_stop(s:timer_id)
    endif
endfunction

function! rtags#enable_automake()
    call rtags#stop_automake_timer()
    if(g:rtags_enable_automake && (&ft==# 'cpp'|| &ft==# 'c'))
        call neomake#configure#automake('rw', 0)
        call rtags#start_automake_timer()
    endif
endfunction

"
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Auto-Commands root
"

augroup rtags_nvim_root_group
    autocmd!
    autocmd Filetype * :call rtags#enable_autoreindex()
    autocmd Filetype * :call rtags#enable_automake()
augroup end
