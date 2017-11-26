" Python wrapper functions {{{
function! rtags#rtags_J() abort
    call _rtags_J()
endfunction

function! rtags#rtagsLogfile() abort
    call _rtags_logfile()
endfunction

function! rtags#reindex()
    call _rtags_reindex()
endfunction
" }}}

" On Auto-Commands {{{

function! rtags#bufenter() abort
    let enabled = (index(g:rtags_enabled_filetypes, &filetype) != -1)
    if(enabled)
        call _rtags_filename_update()
    endif

    call _rtags_enable_status_change(enabled)
    
    if(exists(":AirlineRefresh"))
        call airline#extensions#rtags#enable(enabled)
        :AirlineRefresh
    endif
endfunction

function! rtags#vimleave() abort
    call _rtags_enable_status_change(0)
endfunction

function! rtags#filetype() abort
    let enabled = (index(g:rtags_enabled_filetypes, &filetype) != -1)
    
    if(enabled && g:rtags_enable_autoreindex)
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

    call _rtags_enable_status_change(enabled)
    
    if(exists(":AirlineRefresh"))
        call airline#extensions#rtags#enable(enabled)
        :AirlineRefresh
    endif
endfunction
" }}}

" Status Change Callback {{{
function! rtags#on_status_change(in_index, indexing) abort
    if(exists(":Neomake") && g:rtags_enable_automake_once_indexed && !a:indexing)
        :Neomake
    endif

    if(exists(":AirlineRefresh"))
        let status = ""
        if(a:in_index && !a:indexing)
            let status = "I"
        elseif(a:in_index && a:indexing)
            let status = "..."
        elseif(!a:in_index)
            let status = "N"
        endif

        call airline#extensions#rtags#set_status(status)
        :AirlineRefresh
    endif
endfunction
" }}}
