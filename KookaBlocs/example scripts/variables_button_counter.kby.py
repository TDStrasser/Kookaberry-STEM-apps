import machine, kooka

count_b = None
count_c = None
count_d = None

Number = (bool, int, float)



# On-start code, run once at start-up.
if True:
    count_b = 0
    count_c = 0
    count_d = 0

# Main loop code, run continuously.
while True:
    kooka.display.clear()
    kooka.display.print('Button Counter', show=0)
    kooka.display.print('B : ', count_b, show=0)
    kooka.display.print('C : ', count_c, show=0)
    kooka.display.print('D : ', count_d, show=0)
    kooka.display.print('Press A to exit', show=0)
    if kooka.button_a.was_pressed():
        raise SystemExit
    if kooka.button_b.was_pressed():
        count_b = (count_b if isinstance(count_b, Number) else 0) + 1
    if kooka.button_c.was_pressed():
        count_c = (count_c if isinstance(count_c, Number) else 0) + 1
    if kooka.button_d.was_pressed():
        count_d = (count_d if isinstance(count_d, Number) else 0) + 1
    kooka.display.show()
    machine.idle()

# Generated Blockly XML follows
# <xml xmlns="https://developers.google.com/blockly/xml"><variables><variable id="1Q3ZwEv}D|=VCF,vdw~_">count_b</variable><variable id="E=9g//pZ+Lpkm7uh.JJs">count_c</variable><variable id="E{B@6.FRSX+NlY9J100J">count_d</variable></variables><block type="event_on_start" id="8nyJ6{Xh`yVh}HeQIg+I" x="130" y="-130"><statement name="DO"><block type="variables_set" id="]l8NIAk$w:~TpvM_mVxX"><field name="VAR" id="1Q3ZwEv}D|=VCF,vdw~_">count_b</field><value name="VALUE"><block type="math_number" id="*|}HaGkw:([sQWf~y7fy"><field name="NUM">0</field></block></value><next><block type="variables_set" id="zZ%F#=$Db#;5hip8*.N!"><field name="VAR" id="E=9g//pZ+Lpkm7uh.JJs">count_c</field><value name="VALUE"><block type="math_number" id="2?tt-!_vUd?~aa4m.cl="><field name="NUM">0</field></block></value><next><block type="variables_set" id=".mW2=61{=UOZ9f?}^^1}"><field name="VAR" id="E{B@6.FRSX+NlY9J100J">count_d</field><value name="VALUE"><block type="math_number" id="p/p!l1s*@ANQ:y.-+2^-"><field name="NUM">0</field></block></value></block></next></block></next></block></statement></block><block type="event_button_was_pressed" id="AJhiXztuTobQFkh[j)v;" x="530" y="-130"><field name="BUTTON">kooka.button_a.was_pressed()</field><statement name="DO"><block type="exit_program" id="5HZKqz=m]v3b[jUpjVp+"></block></statement></block><block type="event_button_was_pressed" id="prZj$RkJe]Y5BtA,^*Jh" x="530" y="-50"><field name="BUTTON">kooka.button_b.was_pressed()</field><statement name="DO"><block type="math_change" id="EmWx7a8HhGZY#B_Z[*W_"><field name="VAR" id="1Q3ZwEv}D|=VCF,vdw~_">count_b</field><value name="DELTA"><shadow type="math_number" id="m!yX*ukzfJ$:[_DZObjH"><field name="NUM">1</field></shadow></value></block></statement></block><block type="event_every_loop" id="WPmw+Geb=//I_A(wvv4~" x="130" y="10"><statement name="DO"><block type="display_clear" id="#rP-1;J.foH1dVowM,SB"><next><block type="display_print" id="kk#Hl50jGc]2+jV:;*pr"><value name="VALUE"><shadow type="text" id="omXC/kO@7Kln@kGP=i3w"><field name="TEXT">Button Counter</field></shadow></value><next><block type="display_print2" id="AvtUyFD-#FeJ]~y/.s]J"><value name="VALUE1"><shadow type="text" id="1+H_D!omVHNgap~E`(;a"><field name="TEXT">B : </field></shadow></value><value name="VALUE2"><shadow type="math_number" id="QQdHC_QXQ#YvYAHK@A^+"><field name="NUM">123</field></shadow><block type="variables_get" id="T6S-X8c)nC4.E2OlY:)C"><field name="VAR" id="1Q3ZwEv}D|=VCF,vdw~_">count_b</field></block></value><next><block type="display_print2" id="1gLx8fS#R$[_Ne7}=Q[-"><value name="VALUE1"><shadow type="text" id="^k)=GnM(QPS%C7_Eu[n."><field name="TEXT">C : </field></shadow></value><value name="VALUE2"><shadow type="math_number"><field name="NUM">123</field></shadow><block type="variables_get" id="?_89pB8-fg167)H,:d*@"><field name="VAR" id="E=9g//pZ+Lpkm7uh.JJs">count_c</field></block></value><next><block type="display_print2" id="b0E2Wlbu)WS=yeR@_kS@"><value name="VALUE1"><shadow type="text" id="Yn0HwK}cg^Id8`-|Vg?X"><field name="TEXT">D : </field></shadow></value><value name="VALUE2"><shadow type="math_number"><field name="NUM">123</field></shadow><block type="variables_get" id="_[~;9`SO+L.@N-}?a..f"><field name="VAR" id="E{B@6.FRSX+NlY9J100J">count_d</field></block></value><next><block type="display_print" id="gKQc7_LlnH/W)=+3mkQq"><value name="VALUE"><shadow type="text" id="}V#4]gpzgTj-sV;?vh1?"><field name="TEXT">Press A to exit</field></shadow></value></block></next></block></next></block></next></block></next></block></next></block></statement></block><block type="event_button_was_pressed" id="jGa{dKd:RO4KslA35$X|" x="530" y="30"><field name="BUTTON">kooka.button_c.was_pressed()</field><statement name="DO"><block type="math_change" id="G,jyK7_e0Yf;l/{Y@Ing"><field name="VAR" id="E=9g//pZ+Lpkm7uh.JJs">count_c</field><value name="DELTA"><shadow type="math_number" id="x@3=@Y;NEu,[!t6XdlUC"><field name="NUM">1</field></shadow></value></block></statement></block><block type="event_button_was_pressed" id="E`C9Uj;b/iC7C}%lMRjm" x="530" y="110"><field name="BUTTON">kooka.button_d.was_pressed()</field><statement name="DO"><block type="math_change" id="^mzaqINC$@}~Ss8w=]tz"><field name="VAR" id="E{B@6.FRSX+NlY9J100J">count_d</field><value name="DELTA"><shadow type="math_number" id="=B13Ei7;K]!Cj]ppLO=$"><field name="NUM">1</field></shadow></value></block></statement></block></xml>
