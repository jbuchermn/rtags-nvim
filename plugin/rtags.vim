" Guard {{{
if exists('g:rtags_loaded') || &compatible
    finish
endif
let g:rtags_loaded = 1
" }}}

" Configuration {{{

" Auto-Reindex enabled by default
if(!exists('g:rtags_enable_autoreindex'))
    let g:rtags_enable_autoreindex = 1
endif

" Auto-Make once indexing is finished
if(!exists('g:rtags_enable_automake_once_indexed'))
    let g:rtags_enable_automake_once_indexed = 1
endif

" By default enbale for all supported filetypes
if(!exists('g:rtags_enabled_filetypes'))
    let g:rtags_enabled_filetypes = [ 'c', 'cpp', 'objc', 'objcpp' ]
endif

" }}}

" Auto-Commands {{{
augroup rtags_nvim_root_group
    autocmd!
    autocmd Filetype * :call rtags#filetype()
    autocmd BufEnter * :call rtags#bufenter()
    autocmd VimLeave * :call rtags#vimleave()
augroup end
" }}}

" Commands {{{
command! RTagsReindex :call rtags#reindex()
command! RTagsJ :call rtags#rtags_J()
command! RTagsLog :call rtags#rtagsLogfile()
" }}}

