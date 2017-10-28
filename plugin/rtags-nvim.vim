if exists('g:loaded_rtags_nvim') || &compatible
    finish
endif
let g:loaded_rtags_nvim = 1

augroup rtags_nvim_group
    autocmd!
    autocmd InsertLeave *.cpp :call _rtags_reindex_unsaved()
augroup end
