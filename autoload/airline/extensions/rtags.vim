let s:spc = g:airline_symbols.space

function! airline#extensions#rtags#init(ext)
    call airline#parts#define_function('rtags_status', 'airline#extensions#rtags#get_status')
    call a:ext.add_statusline_func('airline#extensions#rtags#apply')
endfunction

function! airline#extensions#rtags#apply(...)
    let enabled = rtags#is_enabled()
    if(enabled)
        let w:airline_section_c = get(w:, 'airline_section_c', g:airline_section_c)
        let w:airline_section_c .= s:spc . '%{airline#extensions#rtags#get_status()}'
    endif
endfunction

if(!exists('s:status'))
    let s:status = "..."
endif
function! airline#extensions#rtags#set_status(status)
    let s:status = a:status
endfunction

function! airline#extensions#rtags#get_status()
    return "[" . s:status . "]"
endfunction
