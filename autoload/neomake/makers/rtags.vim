function! neomake#makers#rtags#set_list_entries(list_entries) abort
    let s:ListEntries = a:list_entries
endfunction

function! neomake#makers#rtags#rtags() abort
    let maker = {'name': 'RTags'}
    function! maker.get_list_entries(jobinfo) abort
        if(exists("s:ListEntries"))
            return s:ListEntries
        else
            return []
        endif
    endfunction
    return maker
endfunction

