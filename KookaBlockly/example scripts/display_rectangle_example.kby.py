import machine, kooka



# On-start code, run once at start-up.
if True:
    kooka.display.clear()
    kooka.display.rect(int(60), int(30), int(30), int(20), int(1))
    kooka.display.rect(int(60 - 30 + 1), int(30 - 20 + 1), int(30), int(20), int(1))

# Main loop code, run continuously.
while True:
    kooka.display.show()
    machine.idle()

# Generated Blockly XML follows
# <xml xmlns="https://developers.google.com/blockly/xml"><block type="event_on_start" id=".-MY%+zy4Y8LnkSEW[(+" x="250" y="-90"><statement name="DO"><block type="display_clear" id="swfSZvPg6$lLnE50]K;K"><next><block type="display_rect_v2" id="XFHRG#i=3Xik1b-SnEaJ"><field name="F">FALSE</field><field name="R">FALSE</field><value name="X"><shadow type="math_number" id="YDqI$@MyyEF?3G(fIL77"><field name="NUM">60</field></shadow></value><value name="Y"><shadow type="math_number" id="@7I6q2w/6`Mb@q:0B~!e"><field name="NUM">30</field></shadow></value><value name="W"><shadow type="math_number" id=":p]A6_gI_vG]gxN94FJ2"><field name="NUM">30</field></shadow></value><value name="H"><shadow type="math_number" id="Fn.g?cs4Wq:Hl/Ai[Fu]"><field name="NUM">20</field></shadow></value><value name="C"><shadow type="math_number" id="cfF$N0N{E-y8et]0vA%7"><field name="NUM">1</field></shadow></value><next><block type="display_rect_v2" id="F)-MfZ_]N67ZC?*O0)Qn"><field name="F">FALSE</field><field name="R">TRUE</field><value name="X"><shadow type="math_number" id="7%!eu/N_l{(p0UOeWR$h"><field name="NUM">60</field></shadow></value><value name="Y"><shadow type="math_number" id=")fMnd6#oG)23xueHFFX|"><field name="NUM">30</field></shadow></value><value name="W"><shadow type="math_number" id="%5i9V}R;hdR(qC}EB[-F"><field name="NUM">30</field></shadow></value><value name="H"><shadow type="math_number" id="V@W};!R;|^.9`obB+3IQ"><field name="NUM">20</field></shadow></value><value name="C"><shadow type="math_number" id="P}oHV-nQiucnk@l2~^DJ"><field name="NUM">1</field></shadow></value></block></next></block></next></block></statement></block></xml>
