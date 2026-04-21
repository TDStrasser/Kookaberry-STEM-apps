import machine, kooka
import fonts
import time
import math
from machine import Pin

inclination = None
x = None



# Initialise timer counters.
_timer100 = time.ticks_ms()

# On-start code, run once at start-up.
if True:
    inclination = 0

# Main loop code, run continuously.
while True:
    kooka.display.clear()
    kooka.display.setfont(fonts.mono8x8)
    kooka.display.print('Inclinometer', show=0)
    kooka.display.setfont(fonts.mono6x7)
    kooka.display.text(str('A-exit'), int(0), int(63), int(1))
    kooka.display.setfont(fonts.mono8x13)
    kooka.display.text(str('deg'), int(104), int(30), int(1))
    kooka.display.text(str('Incline:'), int(0), int(30), int(1))
    kooka.display.setfont(fonts.sans12)
    kooka.display.text(str("{:2d}".format(round(inclination))), int(70), int(36), int(1))
    if inclination > 44 and inclination < 46:
        kooka.led_red.on()
        Pin("P1", Pin.OUT, value=1)
    else:
        kooka.led_red.off()
        Pin("P1", Pin.OUT, value=0)
    if time.ticks_diff(time.ticks_ms(), _timer100) >= 0:
        _timer100 += 100
        x = kooka.accel.get_xyz()[0]
        if x == 0:
            inclination = 0
        else:
            inclination = math.fabs(math.atan(kooka.accel.get_xyz()[1] / x) / math.pi * 180)
    if kooka.button_a.was_pressed():
        raise SystemExit
    kooka.display.show()
    machine.idle()

# Generated Blockly XML follows
# <xml xmlns="https://developers.google.com/blockly/xml"><variables><variable id="lvch])b:;F?WAhIUtWY`">inclination</variable><variable id="5=v!,OsylRu]/c:|.5^,">x</variable></variables><block type="event_on_start" id="`n7YB2VIyasRss!w*gtA" x="210" y="110"><statement name="DO"><block type="variables_set" id="-reovMg=@qgM?C=oW5#`"><field name="VAR" id="lvch])b:;F?WAhIUtWY`">inclination</field><value name="VALUE"><block type="math_number" id="!hY,0zEhvwPrCJ51KtI:"><field name="NUM">0</field></block></value></block></statement></block><block type="event_every_loop" id="]0[KEARsgK$YCI2A!wi7" x="950" y="150"><statement name="DO"><block type="display_clear" id="xKQ$wXqS#M3pq.KfS/iO"><next><block type="display_setfont" id="n~7psXNI*$D9q)8Vos=~"><field name="FONT">mono8x8</field><next><block type="display_print" id="]Hn$mL053_{?Hq$Oa)Jo"><value name="VALUE"><shadow type="text" id="sI757soKx[Fh]yUghdFO"><field name="TEXT">Inclinometer</field></shadow></value><next><block type="display_setfont" id="pqFF#[qhh]}PJ1k9VE`S"><field name="FONT">mono6x7</field><next><block type="display_text" id="s:=3K$R;Q[:-vx-7*6h["><value name="VALUE"><shadow type="text" id="z8{/h7U)SuNU1ZI}H3ma"><field name="TEXT">A-exit</field></shadow></value><value name="X"><shadow type="math_number" id="qtPy2N`=]$LxA+mj/UQy"><field name="NUM">0</field></shadow></value><value name="Y"><shadow type="math_number" id="_v%+KEKv68p[+=/q?|@2"><field name="NUM">63</field></shadow></value><value name="C"><shadow type="math_number" id="BXMj]D85`$]c]pjK6jXT"><field name="NUM">1</field></shadow></value><next><block type="display_setfont" id="gFNm@-(/#x:F[sZ=rEcA"><field name="FONT">mono8x13</field><next><block type="display_text" id="MLhWunUQlvLufR.kOIa@"><value name="VALUE"><shadow type="text" id="d!_tStXd3pf:^4:Hko=N"><field name="TEXT">deg</field></shadow></value><value name="X"><shadow type="math_number" id="YQtgljQkSh0Ianu(q-Q`"><field name="NUM">104</field></shadow></value><value name="Y"><shadow type="math_number" id=":KgIRAY[RymPT_sna)eI"><field name="NUM">30</field></shadow></value><value name="C"><shadow type="math_number" id="YNhFX+E3/%$D^nYieCW?"><field name="NUM">1</field></shadow></value><next><block type="display_text" id="5`QoP(GyE3/==a$tST(D"><value name="VALUE"><shadow type="text" id="O32j`yAejM;`Qt*^,4^m"><field name="TEXT">Incline:</field></shadow></value><value name="X"><shadow type="math_number" id="$TMC3IhV{J,x.hl59htl"><field name="NUM">0</field></shadow></value><value name="Y"><shadow type="math_number" id="?cP{bwa98XH!?=sQ{,XE"><field name="NUM">30</field></shadow></value><value name="C"><shadow type="math_number" id="Mq,KZU2gz`D9+8VO~({-"><field name="NUM">1</field></shadow></value><next><block type="display_setfont" id="BJh;9uYmIu~gt8Wn{^M6"><field name="FONT">sans12</field><next><block type="display_text" id="$P),ch8;L0e6pOfB+sfS"><value name="VALUE"><shadow type="text" id="x|MP~f~Oi1p~GlyDsI.C"><field name="TEXT">Hello</field></shadow><block type="str_format_int" id="l(g*/AwPMO5ysOF+fV]~"><field name="W">2</field><value name="VALUE"><block type="variables_get" id="xyQ2QDD!uYjKB8a^Z|h("><field name="VAR" id="lvch])b:;F?WAhIUtWY`">inclination</field></block></value></block></value><value name="X"><shadow type="math_number" id="ex5I98N3M9`8*L9dLs_e"><field name="NUM">70</field></shadow></value><value name="Y"><shadow type="math_number" id=",`_vW,$PCYU]zVm:XTJc"><field name="NUM">36</field></shadow></value><value name="C"><shadow type="math_number" id="e@D2trew2i.hY[lS|r1;"><field name="NUM">1</field></shadow></value><next><block type="controls_if" id="*6k^[wmDVOfpt#nW]*)7"><mutation else="1"></mutation><value name="IF0"><block type="logic_operation" id="Ye!qHe#u|ETMxMf[=8TT"><field name="OP">AND</field><value name="A"><block type="logic_compare" id="s5:W~k=esRE0o#SGBc^T"><field name="OP">GT</field><value name="A"><block type="variables_get" id="AT~O52+8R)aR8c7m8{21"><field name="VAR" id="lvch])b:;F?WAhIUtWY`">inclination</field></block></value><value name="B"><block type="math_number" id="M~Fl0J]Ilq9D#jUSV`wy"><field name="NUM">44</field></block></value></block></value><value name="B"><block type="logic_compare" id="rZCDkXclV,x{lZ#xy=cR"><field name="OP">LT</field><value name="A"><block type="variables_get" id="V8;uA:a/`GgG9K~hSUrg"><field name="VAR" id="lvch])b:;F?WAhIUtWY`">inclination</field></block></value><value name="B"><block type="math_number" id="kp2[WzAZNpYTQ(kdQ$iC"><field name="NUM">46</field></block></value></block></value></block></value><statement name="DO0"><block type="led_on" id="jhqoKsz[/$R|@8)f|).K"><field name="LED">led_red</field><next><block type="pin_on" id="}[CPpe5w|=/$%?dC#o3`"><field name="PIN">P1</field></block></next></block></statement><statement name="ELSE"><block type="led_off" id=":A:flaHQu*-lpoAhS6=x"><field name="LED">led_red</field><next><block type="pin_off" id="|Po.5+#=h$ToMS$p7,Yx"><field name="PIN">P1</field></block></next></block></statement></block></next></block></next></block></next></block></next></block></next></block></next></block></next></block></next></block></next></block></next></block></statement></block><block type="event_button_was_pressed" id=")%-(fVVc^mDK-}3VWN,`" x="210" y="250"><field name="BUTTON">kooka.button_a.was_pressed()</field><statement name="DO"><block type="exit_program" id="42@lD^{o*aC:ms@-vxep"></block></statement></block><block type="event_every_seconds" id="MU`dFH/=U9drX^2=O}5A" x="210" y="350"><field name="T">0.1</field><statement name="DO"><block type="variables_set" id="Wkv-MD6Pl.Z!EgGg`A69"><field name="VAR" id="5=v!,OsylRu]/c:|.5^,">x</field><value name="VALUE"><block type="internal_accel_axis" id="R67!?}.GP+mYD5F.1rH|"><field name="AXIS">0</field></block></value><next><block type="controls_if" id="8hTb]Ciie(2t8jnL`C:`"><mutation else="1"></mutation><value name="IF0"><block type="logic_compare" id="kUzC~}|aff_k`L^m:GKd"><field name="OP">EQ</field><value name="A"><block type="variables_get" id="oz^*MwNB[sySx0dSeQ#r"><field name="VAR" id="5=v!,OsylRu]/c:|.5^,">x</field></block></value><value name="B"><block type="math_number" id="ZL|@[SeU~4qc/qn[K]WB"><field name="NUM">0</field></block></value></block></value><statement name="DO0"><block type="variables_set" id="m-@m5$6-~[+nc3]M;y.t"><field name="VAR" id="lvch])b:;F?WAhIUtWY`">inclination</field><value name="VALUE"><block type="math_number" id="mLV^zb=j|P.arZ/rh-Y@"><field name="NUM">0</field></block></value></block></statement><statement name="ELSE"><block type="variables_set" id="U;3v=|_[LiUQ??Ns@CVS"><field name="VAR" id="lvch])b:;F?WAhIUtWY`">inclination</field><value name="VALUE"><block type="math_single" id="HVg(5n)3qZCkB*B4,jx]"><field name="OP">ABS</field><value name="NUM"><block type="math_trig" id="ldu2}D`Qi$d))u,1t6qW"><field name="OP">ATAN</field><value name="NUM"><block type="math_arithmetic" id="UJ{W?:0^GAdi;31)/EF0"><field name="OP">DIVIDE</field><value name="A"><shadow type="math_number" id="1bk7m,B9(Xv(o`T[G[+/"><field name="NUM">1</field></shadow><block type="internal_accel_axis" id="fvBKtr7W:5Z/n-cnwU1Y"><field name="AXIS">1</field></block></value><value name="B"><shadow type="math_number" id="%Pe-).z@|knNgI~gB%{."><field name="NUM">1</field></shadow><block type="variables_get" id="VRk9lnVl~(1%Q4}f;%tm"><field name="VAR" id="5=v!,OsylRu]/c:|.5^,">x</field></block></value></block></value></block></value></block></value></block></statement></block></next></block></statement></block></xml>
