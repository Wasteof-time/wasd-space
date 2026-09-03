def printf(screen, rect, text, font, color, center: bool = False):
    tex = font.render(text, True, color)
    tex_rect = tex.get_rect()
    tex_rect.topleft = rect
    if center:
        tex_rect.center = screen.get_rect().center
    screen.blit(tex, tex_rect)
