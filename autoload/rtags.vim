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

    call _rtags_enable(enabled)
endfunction

function! rtags#vimleave() abort
    call _rtags_vimleave()
endfunction
" }}}

" Status Change callbacks {{{
function! rtags#on_status_change(in_index, indexing) abort

    " TODO: This functionality should be moved to NVimbols
    " This method is actually called more often, than just when the status chenges
    " to ensure up-to-date Airline. However, we don't want to issue Neomake
    " and NVimbolsClear unless the status actually changes from indexing to
    " not indexing
    if(!exists("s:LastIndexing"))
        let s:LastIndexing = a:indexing
    endif

    if(s:LastIndexing && !a:indexing)
        if(exists(":NVimbolsClear") && !a:indexing)
            :NVimbolsClear
        endif
    endif
    let s:LastIndexing = a:indexing

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
