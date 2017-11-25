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



"
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Auto-Commands root
"

augroup rtags_nvim_root_group
    autocmd!
    autocmd Filetype * :call rtags#enable_autoreindex()
    autocmd BufEnter * :call rtags#filename_update()
augroup end

"
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Index a project by :RTagsJ
"

command! RTagsJ :call rtags#rtags_J()
command! RTagsLog :call rtags#rtagsLogfile()

