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
    if(g:rtags_enable_autoreindex && (&ft==# 'cpp' || &ft==# 'c' || &ft==# 'objc' || &ft==# 'objcpp'))
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
" Auto-Commands root
"

augroup rtags_nvim_root_group
    autocmd!
    autocmd Filetype * :call rtags#enable_autoreindex()
augroup end

"
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Index a project by :RTagsJ
"

command! RTagsJ :call rtags#rtags_J()
command! RTagsLog :call rtags#rtagsLogfile()

