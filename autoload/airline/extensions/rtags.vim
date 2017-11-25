let s:spc = g:airline_symbols.space

function! airline#extensions#rtags#init(ext)
    call airline#parts#define_function('rtags_status', 'airline#extensions#rtags#get_status')
    call a:ext.add_statusline_func('airline#extensions#rtags#apply')
endfunction

function! airline#extensions#rtags#apply(...)
    if(&filetype == 'cpp' || &filetype == 'c' || &filetype == 'objc' || &filetype == 'objcpp')
        let w:airline_section_c = get(w:, 'airline_section_c', g:airline_section_c)
        let w:airline_section_c .= s:spc . '%{airline#extensions#rtags#get_status()}'
    endif
endfunction

let s:status = "..."
function! airline#extensions#rtags#set_status(status)
    let s:status = a:status

    " Probably not the nicest way
    :AirlineRefresh
endfunction

function! airline#extensions#rtags#get_status()
    return "[" . s:status . "]"
endfunction
