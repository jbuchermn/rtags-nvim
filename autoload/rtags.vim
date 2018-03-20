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

" Status {{{
function! rtags#is_enabled() abort
    return index(g:rtags_enabled_filetypes, &filetype) != -1
endfunction
" }}}

" On Auto-Commands {{{
function! rtags#bufenter() abort
    let enabled = rtags#is_enabled()
    call _rtags_enable(enabled)
endfunction

function! rtags#vimleave() abort
    call _rtags_vimleave()
endfunction
" }}}

" Status Change callbacks {{{
function! rtags#on_status_change(in_index, indexing) abort
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

function! rtags#on_list_entries_change(list_entries) abort
    call neomake#makers#rtags#set_list_entries(a:list_entries)
    if(exists(":Neomake"))
        :Neomake
    endif
endfunction
" }}}
