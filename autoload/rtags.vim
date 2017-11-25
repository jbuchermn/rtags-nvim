function! rtags#rtags_J() abort
    call _rtags_J()
endfunction

function! rtags#rtagsLogfile() abort
    call _rtags_logfile()
endfunction

function! rtags#filename_update() abort
    if(&filetype == 'c' || &filetype == 'cpp' || &filetype == 'objc' || &filetype == 'objcpp')
        call _rtags_filename_update()
    endif
endfunction

function! rtags#enable_autoreindex() abort
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

function! rtags#reindex()
    call _rtags_reindex_unsaved()
endfunction

" TODO Configurable, check if there is Neomake
function! rtags#indexing_finished()
    :Neomake
endfunction
